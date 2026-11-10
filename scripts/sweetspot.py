"""Bounded SRBMiner/NVIDIA Windows experiments. Dry run unless --run."""
import argparse
import ctypes
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import time
import hardware as hw

FATAL = re.compile(r'CUDA error|backend error|validation error|illegal memory access|GPU[^\r\n]*(?:crashed|failed)|failed to set|could not set|insufficient permission', re.I)
STALE = re.compile(r'expired|chain tip changed|stale|job not found', re.I)
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
RATE = re.compile(r'^\[([^]]+)\] GPU(\d+) [^:\r\n]+:\s*([\d.]+)\s*([kMGTPE]?H)/s\s*\[([^\r\n]+)\]')
SCALE = {'H':1, 'kH':1e3, 'MH':1e6, 'GH':1e9, 'TH':1e12, 'PH':1e15, 'EH':1e18}


def save(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    temp.replace(path)


def read(path):
    return Path(path).read_text(encoding='utf-8', errors='replace') if Path(path).exists() else ''


def records(text):
    result = {}
    for line in ANSI.sub('', text).splitlines():
        m = RATE.match(line)
        if m:
            counters = {k:int(v) for k,v in re.findall(r'\b(A|R|HW):(\d+)',m[5])}
            if set(counters) != {'A','R','HW'}:
                raise ValueError('Incomplete SRB counters; adapt the parser before running')
            r = dict(stamp=m[1], id=int(m[2]), hashrate_hs=float(m[3])*SCALE[m[4]], **counters)
            result[(r['stamp'],r['id'])] = r
    return list(result.values())


def log_errors(srb, console):
    # Critical: check BOTH streams even at 0 H/s or when no rate rows parse.
    text = ANSI.sub('', srb+'\n'+console)
    fatal = [x for x in text.splitlines() if FATAL.search(x)]
    rejected = [x for x in srb.splitlines() if 'share rejected' in x.lower()]
    invalid = [x for x in rejected if not STALE.search(x)]
    return fatal, rejected, invalid


def pci_key(value):
    return tuple(int(x,16) for x in re.split('[:.]',value.strip()))


def validate(config, plan):
    for key in ('executable','sha256','algorithm','pool','wallet','devices','power_method','initial_clock_locks'):
        if not config.get(key):
            raise ValueError('Missing config field: '+key)
    if not re.fullmatch('[0-9a-f]{64}',config['sha256']):
        raise ValueError('Supply the independently verified SHA256')
    if config['initial_clock_locks'] != 'known-unlocked':
        raise ValueError('Establish initial clock locks as known-unlocked; unknown locks cannot be restored exactly')
    if config['power_method'] not in ('nvml-energy','sampled-power'):
        raise ValueError('Explicit power_method required; no silent mixed-method fallback')
    devices = config['devices']
    if len({d['uuid'] for d in devices}) != len(devices) or len({d['miner_id'] for d in devices}) != len(devices):
        raise ValueError('Duplicate UUID or miner ID')
    known = {d['uuid'] for d in devices}
    if not plan:
        raise ValueError('Empty plan')
    labels = set()
    for trial in plan:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',trial['label']) or trial['label'] in labels:
            raise ValueError('Labels must be unique safe folder names')
        labels.add(trial['label'])
        if not 0 <= trial['warmup_s'] < trial['duration_s'] <= 3600:
            raise ValueError('Each trial needs a bounded duration <=3600 seconds and a shorter warmup')
        if trial.get('minimum_rate_windows',8) < 3 or trial.get('rate_window_guard_s',90) < 0:
            raise ValueError('Invalid rate coverage')
        selected = trial['settings']
        if not selected or len({d['uuid'] for d in selected}) != len(selected):
            raise ValueError('Duplicate/empty trial device list')
        for d in selected:
            if d['uuid'] not in known:
                raise ValueError('Unknown GPU UUID')
            for k in ('core_mhz','core_offset_mhz','memory_mhz','power_limit_w'):
                if type(d[k]) is not int or (k != 'core_offset_mhz' and d[k] <= 0):
                    raise ValueError('Integer GPU controls required')


def command(config, trial, folder):
    devices = {d['uuid']:d for d in config['devices']}
    selected = sorted(trial['settings'],key=lambda d:devices[d['uuid']]['miner_id'])
    args = [config['executable'],'--algorithm-gpu',config['algorithm'],'--disable-cpu','--gpu-id',','.join(str(devices[d['uuid']]['miner_id']) for d in selected),'--gpu-reset-oc','--disable-worker-watchdog','--gpu-off-temperature',','.join(str(config.get('max_temperature_c',80)) for _ in selected),'--pool',config['pool'],'--tls',str(config.get('tls',True)).lower(),'--wallet',config['wallet'],'--worker',config.get('worker','sweetspot-test'),'--log-file',str(folder/'srb.log'),'--log-file-mode','1']
    for flag,key in [('--gpu-cclock0','core_mhz'),('--gpu-coffset0','core_offset_mhz'),('--gpu-mclock0','memory_mhz'),('--gpu-plimit0','power_limit_w')]:
        args += [flag,','.join(str(d[key]) for d in selected)]
    return args


def preflight(config, nvml):
    if any('REPLACE' in str(config[k]) for k in ('executable','wallet','pool')):
        raise ValueError('Replace example values before live preflight')
    exe = Path(config['executable'])
    if hashlib.sha256(exe.read_bytes()).hexdigest() != config['sha256']:
        raise RuntimeError('Miner binary hash mismatch')
    if hw.existing_miners():
        raise BusyGpu('Another miner exists; waiting without attaching or stopping it')
    gpus = hw.telemetry()
    if any(g['utilization']>15 or g['watts']>80 for g in gpus.values()):
        raise BusyGpu('GPU workload/idle-power readiness failed; inspect actual background load')
    listing = subprocess.run([str(exe),'--list-devices'],capture_output=True,text=True,check=True,timeout=30).stdout
    for d in config['devices']:
        if d['uuid'] not in gpus or pci_key(gpus[d['uuid']]['pci']) != pci_key(d['pci']):
            raise RuntimeError('UUID/PCI mapping changed')
        matches = re.findall(r'GPU(\d+)\s+\[CUDA\]\[\d+\]\s+\[([0-9a-fA-F:.]+)\]',listing)
        if not any(int(gid)==d['miner_id'] and pci_key(pci)==pci_key(d['pci']) for gid,pci in matches):
            raise RuntimeError('SRB GPU ID/PCI mapping changed')
        offsets = nvml.offsets(d['uuid'])
        if not all(any(k.startswith(str(typ)+':') and 'value' in v for k,v in offsets.items()) for typ in (0,2)):
            raise RuntimeError('Cannot independently snapshot/restore both clock offsets on this driver')
        if config['power_method']=='nvml-energy':
            nvml.energy(d['uuid'])  # Refuse unsupported counters before applying controls.
    return gpus


def summarize(config, trial, folder, samples, outcome, graceful, restored, epoch):
    text = read(folder/'srb.log');console=read(folder/'console.log')
    fatal,rejected,invalid=log_errors(text,console)
    rates=records(text)
    expected_ids={d["miner_id"] for d in config["devices"] if d["uuid"] in {x["uuid"] for x in trial["settings"]}}
    if any(r["id"] not in expected_ids for r in rates):
        outcome="error: Unexpected GPU ID in final logs"
    for r in rates:
        r['elapsed']=(datetime.strptime(r['stamp'],'%Y-%m-%d %H:%M:%S').timestamp()-epoch)
    save(folder/'rates.json',rates)
    usable=[s for s in samples if s['elapsed']>=trial['warmup_s']]
    devices={d['uuid']:d for d in config['devices']};result={}
    for setting in trial['settings']:
        uid=setting['uuid'];gid=devices[uid]['miner_id']
        rr=[r for r in rates if r['id']==gid and trial['warmup_s']+trial.get('rate_window_guard_s',90)<=r['elapsed']<=trial['duration_s']]
        accepted=len(re.findall(r'GPU'+str(gid)+r'[^\r\n]*share accepted[^\r\n]*\['+re.escape(config['algorithm'])+r'\]\[0\]',text,re.I))
        item=dict(settings=setting,owner_accepted=accepted,rate_windows=len(rr),power_method=config['power_method'])
        if len(usable)>1 and rr:
            item['hashrate_hs']=statistics.mean(r['hashrate_hs'] for r in rr)
            if config['power_method']=='nvml-energy':
                delta=usable[-1]['energy_mj'][uid]-usable[0]['energy_mj'][uid]
                if delta<0:
                    raise RuntimeError('Energy counter reset; measurement invalid')
                watts=delta/1000/(usable[-1]['epoch']-usable[0]['epoch'])
            else:
                watts=statistics.mean(s['gpus'][uid]['watts'] for s in usable)
            item.update(watts=watts,efficiency_hs_per_w=item['hashrate_hs']/watts,sampled_watts=statistics.mean(s['gpus'][uid]['watts'] for s in usable),actual_core_mhz=statistics.mean(s['gpus'][uid]['core_mhz'] for s in usable),actual_memory_mhz=statistics.mean(s['gpus'][uid]['memory_mhz'] for s in usable),max_temperature_c=max(s['gpus'][uid]['temperature_c'] for s in samples))
            item['controls_verified']=all(abs(s['gpus'][uid]['core_mhz']-setting['core_mhz'])<60 and abs(s['gpus'][uid]['memory_mhz']-setting['memory_mhz'])<25 and abs(s['gpus'][uid]['power_limit_w']-setting['power_limit_w'])<2 and s['offsets'][uid].get('0:'+str(s['gpus'][uid]['pstate']),{}).get('value')==setting['core_offset_mhz'] for s in usable)
        item['valid']=outcome=='completed' and graceful and restored and not fatal and not invalid and not any(r['HW'] for r in rates) and item.get('controls_verified',False) and len(rr)>=trial.get('minimum_rate_windows',8) and accepted>0
        result[uid]=item
    return dict(label=trial['label'],outcome=outcome,graceful=graceful,restored=restored,valid=all(v['valid'] for v in result.values()),gpus=result,fatal=fatal,rejected=rejected,invalid_rejected=invalid,max_private_mib=max((s['memory']['private_commit_bytes']/1024**2 for s in samples),default=0),warmup_s=trial['warmup_s'],duration_s=trial['duration_s'])


def restore(nvml, before, offsets):
    commands=[];errors=[];after_offsets={}
    for uid, original in offsets.items():
        for args in (['-rgc'],['-rmc'],['-pl',str(before[uid]['power_limit_w'])]):
            try:
                p=subprocess.run([hw.SMI,'-i',uid,*args],capture_output=True,text=True,timeout=20)
                commands.append(dict(uuid=uid,args=args,code=p.returncode,stdout=p.stdout,stderr=p.stderr))
                if p.returncode:
                    errors.append(uid+' reset command failed')
            except Exception as exc:
                errors.append(repr(exc))
        try:
            after_offsets[uid]=nvml.restore_offsets(uid,original)
        except Exception as exc:
            errors.append(repr(exc))
    try:
        after=hw.telemetry()
        for uid in offsets:
            if abs(after[uid]['power_limit_w']-before[uid]['power_limit_w'])>=1:
                errors.append(uid+' PL restore mismatch')
    except Exception as exc:
        after={};errors.append(repr(exc))
    return dict(restored=not errors,commands=commands,errors=errors,after=after,offsets=after_offsets)


def run_trial(config,trial,folder,nvml,before):
    folder.mkdir(parents=True,exist_ok=False)
    offsets={d['uuid']:nvml.offsets(d['uuid']) for d in trial['settings']}
    save(folder/'before.json',dict(gpus=before,offsets=offsets))
    args=command(config,trial,folder);save(folder/'command.private.json',args)
    job=hw.OwnedJob();child=memory=None;samples=[];outcome='completed';graceful=False
    selected=set(offsets);ids={d['miner_id'] for d in config['devices'] if d['uuid'] in selected}
    began=time.monotonic();epoch=time.time()
    try:
        with (folder/'console.log').open('wb') as output,(folder/'samples.jsonl').open('w',encoding='utf-8') as stream:
            child=subprocess.Popen(args,cwd=Path(config['executable']).parent,stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            job.assign(child);memory=hw.ProcessMemory(child.pid)
            while time.monotonic()-began<trial['duration_s']:
                if (folder.parent/'STOP').exists():
                    raise RuntimeError('User STOP file')
                if child.poll() is not None:
                    raise RuntimeError('Original miner PID exited')
                gpus=hw.telemetry();ram=memory.read()
                if any(gpus[uid]['temperature_c']>=config.get('max_temperature_c',80) for uid in selected):
                    raise RuntimeError('Temperature stop')
                if any(g['utilization']>15 for uid,g in gpus.items() if uid not in selected):
                    raise RuntimeError('Background GPU load changed; restore and wait, do not kill the other workload')
                if ram['private_commit_bytes']>=config.get('max_private_mib',2048)*1024**2:
                    raise RuntimeError('Private commit stop')
                raw=read(folder/'srb.log');console=read(folder/'console.log');fatal,rejects,invalid=log_errors(raw,console);rr=records(raw)
                if fatal or invalid or any(r['HW'] or r['id'] not in ids for r in rr):
                    raise RuntimeError('Backend, HW, invalid proof or GPU mapping error; no retry')
                sample=dict(elapsed=time.monotonic()-began,epoch=time.time(),gpus=gpus,memory=ram,offsets={uid:nvml.offsets(uid) for uid in selected})
                if config['power_method']=='nvml-energy':
                    sample['energy_mj']={uid:nvml.energy(uid) for uid in selected}
                if sample['elapsed']>=trial['warmup_s']:
                    for setting in trial['settings']:
                        uid=setting['uuid'];g=gpus[uid]
                        active=sample['offsets'][uid].get('0:'+str(g['pstate']),{}).get('value')
                        if abs(g['core_mhz']-setting['core_mhz'])>=60 or abs(g['memory_mhz']-setting['memory_mhz'])>=25 or abs(g['power_limit_w']-setting['power_limit_w'])>=2 or active!=setting['core_offset_mhz']:
                            raise RuntimeError('Live control readback mismatch')
                samples.append(sample);stream.write(json.dumps(sample)+'\n');stream.flush()
                save(folder/'status.json',dict(state='running',elapsed=sample['elapsed'],duration_s=trial['duration_s'],owned_pid=child.pid))
                time.sleep(5)
    except BaseException as exc:
        outcome='error: '+repr(exc)
    finally:
        try:
            if child:
                graceful=hw.stop_owned(child,job)
            else:
                job.close()
        finally:
            if memory:
                memory.close()
            restored=restore(nvml,before,offsets);save(folder/'restore.json',restored)
    try:
        report=summarize(config,trial,folder,samples,outcome,graceful,restored['restored'],epoch)
    except Exception as exc:
        report=dict(label=trial['label'],valid=False,outcome=outcome,analysis_error=repr(exc),graceful=graceful,restored=restored['restored'],gpus={})
    save(folder/'report.json',report);save(folder/'status.json',dict(state='completed-and-stopped',valid=report['valid']))
    return report


class BusyGpu(RuntimeError):
    pass


def wait_ready(config,nvml,wait_seconds):
    deadline=time.monotonic()+wait_seconds
    while True:
        try:
            return preflight(config,nvml)
        except BusyGpu as exc:
            print(json.dumps(dict(state='waiting-for-idle',reason=str(exc))),flush=True)
            if time.monotonic()>=deadline:
                raise RuntimeError('Idle wait budget ended; no miner started; continue waiting in the owning AI session') from exc
            time.sleep(min(10,max(0,deadline-time.monotonic())))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path('runs'))
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--validate-only',action='store_true',help='Offline schema/command validation; no device checks')
    parser.add_argument('--wait-for-idle-s',type=int,default=600)
    args=parser.parse_args()
    if args.wait_for_idle_s<0 or (args.run and args.validate_only):
        parser.error('Invalid wait or conflicting run/validate-only options')
    config=json.loads(args.config.read_text(encoding='utf-8-sig'));plan=json.loads(args.plan.read_text(encoding='utf-8-sig'))
    validate(config,plan)
    if args.validate_only:
        print(json.dumps(dict(mode='offline-schema-only',maximum_mining_s=sum(t['duration_s'] for t in plan),commands=[command(config,t,args.output/t['label']) for t in plan]),indent=2))
        return 0
    if os.name!='nt':
        raise RuntimeError('Live bundled runner requires Windows; offline analysis works on other systems')
    if args.run and not ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError('Administrator token required; no miner started')
    lock=None
    if args.run:
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.CreateMutexW.argtypes,api.CreateMutexW.restype=[ctypes.c_void_p,hw.W.LPCWSTR],hw.W.HANDLE
        api.CloseHandle.argtypes=[hw.W.HANDLE]
        lock=api.CreateMutexW(None,False,r'Local\GpuMiningSweetspotHarness')
        if not lock or ctypes.get_last_error()==183:
            if lock:
                api.CloseHandle(lock)
            raise RuntimeError('Another experiment controller exists or mutex failed')
    nvml=None
    try:
        nvml=hw.Nvml()
        for trial in plan:
            before=wait_ready(config,nvml,args.wait_for_idle_s)
            if not args.run:
                print(json.dumps(dict(mode='live-read-only-preflight',label=trial['label'],command=command(config,trial,args.output/trial['label']))))
                continue
            args.output.mkdir(parents=True,exist_ok=True)
            save(args.output/'config.private.json',config)
            report=run_trial(config,trial,args.output/trial['label'],nvml,before)
            print(json.dumps(report),flush=True)
            if not report['valid']:
                return 1  # Preserve failed/incomplete run; never auto-retry.
        return 0
    finally:
        if nvml:
            nvml.close()
        if lock:
            api.CloseHandle(lock)


if __name__=='__main__':
    raise SystemExit(main())
