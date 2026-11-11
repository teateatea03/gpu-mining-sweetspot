# Windows NVIDIA / SRBMiner adapter

## Supported boundary

Python 3.10+ standard library, native Windows, NVIDIA driver/NVML/nvidia-smi, a user-supplied verified SRBMiner binary and a valid wallet/pool for the selected GPU algorithm. The originating run used SRBMiner 3.8.6 / driver 621.01. Obtain miners from their actual upstream release; this repository ships no miner binary and does not verify a download's origin merely by hashing it.

Sources: [SRBMiner upstream](https://github.com/doktor83/SRBMiner-Multi), [NVIDIA NVML API](https://docs.nvidia.com/deploy/nvml-api/), [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/). Check the installed version's flags, supported clocks, PL bounds and algorithm output before live execution.

The adapter uses `nvmlDeviceGetClockOffsets` for graphics/memory across P-states 0-15 and independent readback after restoration. Older getters returning unsupported do not prove these APIs are unsupported. It refuses live preflight if neither graphics nor memory offsets can be independently read. A card/driver without suitable controls needs a different tested adapter, not silent unverified tuning.

## Prepare a private configuration and a finite plan

Copy `examples/config.example.json` and `examples/plan.example.json` outside the public repository, or use ignored `config.local.json` and `plan.local.json`. Replace every placeholder. Never publish your wallet, host paths, UUID inventory or raw command logs by accident. Placeholder example values are not hardware recommendations.

Config fields:

- `executable`, `sha256`: absolute binary and independently verified expected SHA256.
- `algorithm`, `pool`, `wallet`, `tls`, `worker`: owner-pool connection. Validate the wallet using that coin's actual address rules; the generic adapter does not implement every coin's checksum.
- `devices`: UUID, PCI and SRB miner ID for each card that may be selected. Confirm IDs using `--list-devices`; NVIDIA and miner indices are not assumed equal.
- `power_method`: `nvml-energy` or explicitly `sampled-power`. No automatic mixed-method fallback.
- `initial_clock_locks`: `known-unlocked`. This is an operator-established prerequisite, not a magically measurable NVML assertion. Existing non-default locks require an adapter able to snapshot/restore them; do not run this adapter on unknown pre-existing locks.
- `max_temperature_c`, `max_private_mib`: stop thresholds chosen for the actual hardware/task. Default 80 C and 2048 MiB process private commit are examples, not universal thermal or memory limits.

Each plan entry has a unique `label`, `duration_s`, `warmup_s`, `rate_window_guard_s`, `minimum_rate_windows` and a nonempty `settings` array. Each setting contains UUID, `core_mhz`, `core_offset_mhz`, `memory_mhz`, `power_limit_w`. Single-card entries implement sweeps; a multi-card entry validates combinations. Command vectors are ordered by SRB ID, not input array order. Only one controller owns controls at a time. Each trial is bounded to at most one hour; the whole finite plan's duration is printed by offline validation.

Choose duration after observing reporting cadence. The example 900-second duration / 150-second warmup / 90-second rate guard / eight-window minimum is an illustration with margin, not a guarantee. The rate mean is the arithmetic mean of distinct miner-reported windows; it is not a precise pool-derived effective hashrate. Slow/changing report cadence and work-supply gaps remain limitations.

## Modes

Run from the skill directory; use your actual Python executable. In PowerShell set `$env:PYTHONUTF8='1'` first.

```text
python scripts/sweetspot.py --config config.local.json --plan plan.local.json --validate-only
python scripts/hardware.py
python scripts/sweetspot.py --config config.local.json --plan plan.local.json
python scripts/sweetspot.py --config config.local.json --plan plan.local.json --output runs/session-a --wait-for-idle-s 600 --run
python scripts/analyze.py --input runs/session-a --output analysis/session-a
python scripts/analyze.py --input runs/session-a --output analysis/paired --pair runs/session-a/A1/report.json runs/session-a/B/report.json runs/session-a/A2/report.json
```

`--validate-only` checks schema and command construction offline; it does not verify hardware, the binary or pool. Default live preflight only reads telemetry, NVML offsets, binary hash and miner device listing. Only `--run` starts mining and requires an administrator token. Do not restart tools or elevate by guessing credentials; use the available authorized interface.

If busy, the runner prints `waiting-for-idle` and waits up to the supplied window. It never stops the other workload. A wait timeout starts no miner; the owning AI may continue waiting within the user's authorization. Do not convert a finite timeout into a permanent automation or a fault retry. Another existing miner is treated as busy: wait without attaching to or stopping it.

During a run, the operator/AI must monitor competing work on selected GPUs. The bundled adapter detects changed utilization on unselected GPUs, thermal/commit faults and SRB errors, but GPU utilization alone cannot distinguish its own mining from another workload on the same selected GPU. Windows WDDM process lists may be incomplete and list idle desktop clients. Capture process/VRAM/background evidence; do not equate presence with activity or absence with no interference. Use the `STOP` path on evidence of competing work, restore and wait. Never call contaminated data a controlled A/B.

## Stop, restore and audit

Create `runs/session-a/STOP` or interrupt the owning controller. It sends CTRL_BREAK to its own Popen child process group, waits, then closes its own kill-on-close Windows Job Object if necessary. Forced cleanup is recorded as non-graceful and cannot pass validation. It never kills an arbitrary PID or all processes by name. The job protects child ownership; hard OS/driver failure still needs human recovery and is not a guaranteed rollback.

Every trial writes before/command/sample/rate/report/restore files. `command.private.json`, config, logs and raw hardware snapshots can contain personal information. Output directories and private configs are gitignored, but audit actual tracked files before publishing.

Finally resets core/memory locks to the established unlocked baseline, restores prior PL and all readable prior offsets, then independently checks offsets and PL. Cleanup runs even on Ctrl+C, CUDA failure or memory stop. A restore failure invalidates the trial and ends the plan. A failed/incomplete trial is not automatically retried. Finishing one trial does not authorize applying it to daily launchers.

Inspect both stdout and stderr/exit status from launch wrappers. In Windows PowerShell, cache `Process.Handle` before `WaitForExit()` to retain a meaningful `ExitCode`; a null wrapper value is an orchestration ambiguity, not proof the GPU failed. Preserve child reports and reconcile rather than automatically re-running expensive completed work. Use hidden windows for background helpers.

For Windows System driver events, use an invariant UTC XPath/FilterXml time query when custom localized DateTime formatting breaks FilterHashtable. Save native event XML when the formatted Message is null. Correlate events by time/device without assuming causation.

## Validation limits

The repository's deterministic tests and read-only hardware probe do not constitute a live mining test of every refactored code path, supported card or driver. The case study's historical real runs establish the method and measured local results. Calibrate the new adapter's short owned stop/restore path on the target system before a long plan. Other miners and OSes require their own parser, owner-pool identification and lifecycle/control adapter; the offline analyzer accepts normalized reports.

## Advanced controller boundary

The bundled preflight still uses a conservative all-GPU utilization/power readiness check. It can reject normal Windows desktop activity or work on another card. Its core-temperature-only check, lack of fan-policy control and strict clock tolerance do not implement the private daily controller. Diagnose with [Windows operations](windows-operations.md); use a calibrated adapter when these limitations matter. Do not silently raise an idle threshold, call unavailable sensors safe, or claim the packaged code passed the private controller's full deployment validation.

Known temporary pool-capacity waits, finite reconnect grace, per-board sensors, AUTO fan restoration and RAM recycling require explicit state/lifecycle support. See [failure triage](failure-triage.md). These documentation methods are not automatic behavior of this basic runner.
