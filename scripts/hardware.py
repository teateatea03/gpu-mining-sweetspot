"""NVIDIA readback and Windows child ownership. No GPU mutation on import/probe."""
import ctypes as C
from ctypes import wintypes as W
import csv
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess

SMI = shutil.which('nvidia-smi') or str(Path(os.environ.get('SystemRoot', 'C:/Windows'))/'System32/nvidia-smi.exe')


def telemetry():
    fields = 'uuid,name,pci.bus_id,power.draw,power.limit,clocks.gr,clocks.mem,temperature.gpu,utilization.gpu,memory.used,pstate'
    p = subprocess.run([SMI, '--query-gpu='+fields, '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True, timeout=15)
    out = {}
    for row in csv.reader(p.stdout.splitlines()):
        uid, name, pci, watts, pl, core, mem, temp, util, vram, state = (s.strip() for s in row)
        out[uid] = dict(name=name, pci=pci, watts=float(watts), power_limit_w=float(pl), core_mhz=float(core), memory_mhz=float(mem), temperature_c=float(temp), utilization=float(util), vram_mib=float(vram), pstate=int(state.lstrip('P')))
    return out


class ClockOffset(C.Structure):
    _fields_ = [('version', C.c_uint), ('type', C.c_int), ('pstate', C.c_int), ('value', C.c_int), ('minimum', C.c_int), ('maximum', C.c_int)]


class Nvml:
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('Bundled NVML adapter is Windows only; use a platform adapter on other systems')
        self.dll = C.WinDLL(str(Path(os.environ.get('SystemRoot', 'C:/Windows'))/'System32/nvml.dll'))
        self.call('nvmlInit_v2', [])

    def call(self, name, types, *args):
        fn = getattr(self.dll, name)
        fn.argtypes, fn.restype = types, C.c_int
        code = fn(*args)
        if code:
            raise RuntimeError(f'{name}: NVML return {code}')

    def handle(self, uid):
        handle = C.c_void_p()
        self.call('nvmlDeviceGetHandleByUUID', [C.c_char_p, C.POINTER(C.c_void_p)], uid.encode('ascii'), C.byref(handle))
        return handle

    def offsets(self, uid):
        result = {}
        for typ in (0, 2):  # NVML_CLOCK_GRAPHICS, NVML_CLOCK_MEM
            for state in range(16):
                value = ClockOffset(C.sizeof(ClockOffset) | (1 << 24), typ, state, 0, 0, 0)
                try:
                    self.call('nvmlDeviceGetClockOffsets', [C.c_void_p, C.POINTER(ClockOffset)], self.handle(uid), C.byref(value))
                    result[f'{typ}:{state}'] = dict(value=value.value, minimum=value.minimum, maximum=value.maximum)
                except (RuntimeError, AttributeError) as exc:
                    result[f'{typ}:{state}'] = {'unsupported': str(exc)}
        return result

    def energy(self, uid):
        value = C.c_ulonglong()
        self.call('nvmlDeviceGetTotalEnergyConsumption', [C.c_void_p, C.POINTER(C.c_ulonglong)], self.handle(uid), C.byref(value))
        return value.value

    def restore_offsets(self, uid, original):
        current = self.offsets(uid)
        for key, item in original.items():
            if 'value' in item and current.get(key, {}).get('value') != item['value']:
                typ, state = map(int, key.split(':'))
                info = ClockOffset(C.sizeof(ClockOffset) | (1 << 24), typ, state, item['value'], 0, 0)
                self.call('nvmlDeviceSetClockOffsets', [C.c_void_p, C.POINTER(ClockOffset)], self.handle(uid), C.byref(info))
        after = self.offsets(uid)
        if any(after.get(k, {}).get('value') != v['value'] for k, v in original.items() if 'value' in v):
            raise RuntimeError('Independent offset restore readback mismatch')
        return after

    def close(self):
        self.call('nvmlShutdown', [])


class BasicLimits(C.Structure):
    _fields_ = [('process_time', C.c_longlong), ('job_time', C.c_longlong), ('flags', W.DWORD), ('min_ws', C.c_size_t), ('max_ws', C.c_size_t), ('active', W.DWORD), ('affinity', C.c_size_t), ('priority', W.DWORD), ('scheduling', W.DWORD)]


class IoCounters(C.Structure):
    _fields_ = [(name, C.c_ulonglong) for name in ('read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]


class ExtendedLimits(C.Structure):
    _fields_ = [('basic', BasicLimits), ('io', IoCounters)] + [(name, C.c_size_t) for name in ('process_memory', 'job_memory', 'peak_process', 'peak_job')]


class OwnedJob:
    """Kill-on-close applies only to this newly created process tree."""
    def __init__(self):
        self.api = C.WinDLL('kernel32', use_last_error=True)
        self.api.CreateJobObjectW.argtypes, self.api.CreateJobObjectW.restype = [C.c_void_p, W.LPCWSTR], W.HANDLE
        self.api.SetInformationJobObject.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD]
        self.api.AssignProcessToJobObject.argtypes = [W.HANDLE, W.HANDLE]
        self.api.OpenProcess.argtypes, self.api.OpenProcess.restype = [W.DWORD, W.BOOL, W.DWORD], W.HANDLE
        self.api.CloseHandle.argtypes = [W.HANDLE]
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise C.WinError(C.get_last_error())
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000
        if not self.api.SetInformationJobObject(self.handle, 9, C.byref(limits), C.sizeof(limits)):
            self.close()
            raise C.WinError(C.get_last_error())

    def assign(self, process):
        h = self.api.OpenProcess(0x100 | 1, False, process.pid)
        if not h:
            process.terminate()
            raise C.WinError(C.get_last_error())
        try:
            if not self.api.AssignProcessToJobObject(self.handle, h):
                process.terminate()
                raise C.WinError(C.get_last_error())
        finally:
            self.api.CloseHandle(h)

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def stop_owned(process, job, timeout=30):
    graceful = False
    try:
        if process.poll() is None:
            process.send_signal(signal.CTRL_BREAK_EVENT)
            process.wait(timeout=timeout)
            graceful = True
    except (OSError, subprocess.TimeoutExpired):
        graceful = False
    finally:
        job.close()
        # Reap the owned child after job-close fallback; no arbitrary PID kill.
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            graceful = False
    return graceful


class MemoryCounters(C.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(name, C.c_size_t) for name in ('peak_ws', 'ws', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile', 'private_commit')]


class ProcessMemory:
    def __init__(self, pid):
        self.api = C.WinDLL('kernel32', use_last_error=True)
        self.api.OpenProcess.argtypes, self.api.OpenProcess.restype = [W.DWORD, W.BOOL, W.DWORD], W.HANDLE
        self.api.CloseHandle.argtypes = [W.HANDLE]
        self.psapi = C.WinDLL('psapi', use_last_error=True)
        self.psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.c_void_p, W.DWORD]
        self.handle = self.api.OpenProcess(0x400 | 0x10, False, pid)
        if not self.handle:
            raise C.WinError(C.get_last_error())

    def read(self):
        value = MemoryCounters()
        value.cb = C.sizeof(value)
        if not self.psapi.GetProcessMemoryInfo(self.handle, C.byref(value), value.cb):
            raise C.WinError(C.get_last_error())
        return {'private_commit_bytes': value.private_commit, 'working_set_bytes': value.ws}

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def existing_miners():
    command = "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); @(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(SRBMiner-MULTI|krig-miner|lolMiner|t-rex|nbminer|bzminer|gminer|miner|teamredminer)[.]exe$'} | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"
    p = subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], capture_output=True, encoding='utf-8', check=True, timeout=20)
    result = json.loads(p.stdout) if p.stdout.strip() else []
    return result if isinstance(result, list) else [result]


if __name__ == '__main__':
    nvml = Nvml()
    try:
        gpus = telemetry()
        print(json.dumps({'gpus': gpus, 'offsets': {uid: nvml.offsets(uid) for uid in gpus}}, indent=2))
    finally:
        nvml.close()
