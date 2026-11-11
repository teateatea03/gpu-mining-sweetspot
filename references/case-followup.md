# Later endurance and desktop deployment follow-up

These 2026-11-11 operator-recorded results extend the [initial short screening](case-study.md). They do not invalidate every earlier measurement, but prevent treating a short pass as permanent deployment confidence. The original raw logs, wallet, host identifiers and backups remain private. Public numbers cannot independently establish every raw-log assertion.

## What later failed or remained incomplete

- A high-speed dual profile cleared a 30-minute check but later produced E1027/CUDA700 during actual operation. Its short pass was retained as history and daily adoption withdrawn.
- Another dual attempt first reported a fault on the other GPU with a shared error on its peer. HW stayed zero. This did not prove that only one card caused the problem.
- A reduced candidate ran about 24 minutes without CUDA/HW failure, then encountered a pool verification-queue capacity response. It did not complete the planned hour and was not relabeled passed. Treating a recognized temporary pool wait as a fatal GPU event was too strict for daily operation.
- A subsequent short AUTO-fan pilot using core/offset/memory/PL of 1650/+300/405/250 on one card and 2970/+300/14801/290 on the other produced a shared CUDA700/E1027 response in roughly two minutes. Four relevant driver events were preserved. It was not automatically replayed.

Changing frequency, offsets and memory together for recovery does not isolate a unique cause. The first reporting card, cool sensors and HW=0 are insufficient attribution evidence.

## Conservative recovery profile

The final recovery validation was a nominal 3600-second controller run with **3592.94 seconds of actual mining observation**, one SRB process, no RAM recycling, and predeclared coverage. The private controller differed from the bundled public harness; its per-board sensors, fan policy and clock-ceiling semantics were verified separately.

| Card | Core ceiling / offset MHz | Memory / offset MHz | PL ceiling W | Mean TH/s | GPU energy W | Sampled W |
|---|---|---|---:|---:|---:|---:|
| RTX 3080 Ti | 1650 / 0 | 5001 / 0 | 250 | 118.363 | 243.988 | 248.565 |
| RTX 5080 | 2640 / 0 | 14801 / 0 | 290 | 216.921 | 259.689 | 267.764 |
| Combined | | | | 335.284 | 503.677 | 516.329 |

Combined T/W was about 0.6657 TH/s/W. Actual mean cores were about 1569.9 and 2632 MHz; the first card was power-limited. Each card had 38 warmed rate windows and 3508 native AUTO samples. Owner accepted work was 49/92; rejects, HW errors, fatal errors and new relevant System driver events were zero. Both controller levels stopped normally, returned zero and verified restoration. Maximum junction readings were 74°C/60°C.

This was a **stable recovery operating point, not the highest-T/W result**. General desktop graphics and one transient external-activity sample were retained. `performance_comparison_valid=false`; it is not a controlled A/B improvement claim against the initial efficient profiles. The [anonymous capsule](../examples/endurance-summary.json) preserves numeric exposure and measurements, not identities or raw logs. It is not a preset or a normalized ranking input.

## Why testing the desktop entry mattered

A first coarse activity gate treated normal desktop composition as busy and started no miner. An adjusted gate then stopped on a remote-viewer's rendering just beyond a fixed threshold. More importantly, after headless validation the actual desktop launch could not read the compositor's path. Direct elevated CMD had a different token privilege state from an elevated PowerShell helper.

A scoped metadata reader was verified through that real launch route: path unavailable before, correct full path during an existing-token privilege activation, and original state restored afterward. Unknown paths were not silently exempted. The final foreground launch was checked against its new receipt PID and visible window, new session, actual command, native offsets/PL/memory, AUTO policy and owner submissions from both GPUs. The permission-only fix changed neither the validated GPU settings nor the miner binary.

## Transferable conclusion

Keep research, screening, endurance and actual deployment as different evidence levels. A reliable conservative fallback is useful even when its T/W is lower. Report unfinished efficiency tuning rather than naming the recovery profile an optimum. Do not equate a RAM recycling wrapper with fixing a closed miner's internal memory behavior, or a short trial with overnight endurance.
