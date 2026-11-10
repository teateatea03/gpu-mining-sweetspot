---
name: gpu-mining-sweetspot
description: Find and validate GPU mining efficiency sweet spots using bounded per-card clock, offset, memory and power sweeps, consistent energy measurements, pool proof and reversible controls. Use when tuning mining hashrate per watt.
---

# GPU mining sweet spots

Produce a measured tradeoff curve and validated settings for each physical card. When the user wants the highest T/W, optimize `hashrate / watts`, not peak hashrate or minimum watts alone. Distinguish GPU efficiency from whole-rig efficiency and profit. Do not impose a hidden 95%-of-peak filter.

This skill contains an offline analyzer and a Windows NVIDIA/SRBMiner adapter. Other miners, vendors and operating systems require an adapter calibrated against their actual logs, counters and control APIs. Do not claim that one card's settings generalize to another card or algorithm.

## Operating invariants

- Use the user's existing authorization for experiments, stopping owned miners and deployment. Research alone does not authorize starting a miner, changing clocks, shutting down other applications or publishing data.
- If a target GPU is busy with the user's work, wait for idle; do not stop that workload. Bound each observation window and keep the owning AI session active. If a wait expires, report the pending state or continue waiting within existing authorization. Do not schedule permanent monitoring. If competing work starts during a trial, stop only the owned miner, restore settings and exclude the contaminated measurement.
- Match UUID, PCI location and miner device index immediately before controls. Keep each physical card's artifacts separate. Serialize controls; research may run concurrently, hardware controllers may not.
- Snapshot power limits and independently readable offsets before mutation. Establish initial clock locks as known-unlocked, or provide a separately verified restore adapter for existing locks. Unsupported getters are not evidence of zero offsets. If restoration cannot be verified, stop the plan.
- Use a finite plan, thermal/RAM limits, owned process trees and unconditional cleanup. Stop on backend/CUDA/HW/control/invalid-proof errors; scan both log and console even at 0 H/s. A zero HW counter does not prove success. Do not automatically retry hardware faults or push beyond a failed offset.
- Power comes from cumulative energy delta divided by elapsed time when supported. Otherwise label sampled power and keep it consistent across paired comparisons. Include work-supply gaps; do not retain only busy samples. GPU watts are not wall watts.
- Deduplicate hash windows by source timestamp and GPU ID. Require enough independent warmed windows and real owner-pool accepted work. Count stale rejects separately; do not hide them or assume every rejection is caused by clocks.
- Preserve all failed/incomplete runs and recovery evidence. Reconcile coverage gaps before deciding on a bounded follow-up; do not change acceptance thresholds after observing results.
- Finish stopped with restoration readback, unless the user explicitly wants mining to continue. Deploy only validated settings within the requested scope; back up launchers and verify effective commands through actual shortcut/guard chains.

## Choose the relevant reference

- For experimental design, algorithm bottlenecks, sequential combinations, A-B-A checks, noise and selecting T/W: read [references/protocol.md](references/protocol.md).
- For Windows/NVIDIA/SRBMiner execution, prerequisites, schema, waits, telemetry limits and cleanup: read [references/srb-windows.md](references/srb-windows.md) before using `scripts/sweetspot.py --run`.
- For evidence from the originating PearlHash experiment, including failures and a report-coverage mistake: read [references/case-study.md](references/case-study.md). Values are examples, not presets.

## Tools and output

Python 3.10+; scripts use the standard library. Set `PYTHONUTF8=1` on Windows.

- `scripts/hardware.py`: read-only NVIDIA telemetry/offset probe; never starts mining.
- `scripts/sweetspot.py`: offline `--validate-only`, live read-only preflight by default, explicit `--run` for a finite SRB plan. It waits for idle before starting and aborts the remaining plan on an invalid trial. It does not install miners, disable antivirus, alter drivers/BIOS or edit daily launchers.
- `scripts/analyze.py`: offline full curve, separate power-method groups, best observed T/W and Pareto frontiers; optional `--pair A1 B A2` comparison. Its input validity fields must be backed by raw evidence; the analyzer cannot prove those assertions independently.

Return parameters, actual clocks, hashrate, power method/scope, T/W, pool acceptance/rejections, errors, exposure time, restoration and remaining uncertainty. Separate a short validated candidate from endurance evidence and a global optimum. Link the artifacts. State whether daily settings were deployed and whether mining is running. Model-driven forward testing is separate from deterministic script tests; do not claim one proves the other.
