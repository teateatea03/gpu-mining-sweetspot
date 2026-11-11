---
name: gpu-mining-sweetspot
description: Find and validate GPU mining settings using algorithm-aware clock, memory and power experiments, comparable energy measurements, pool proof and reversible deployment. Use for hashrate-per-watt or speed/power tuning.
---

# GPU mining sweet spots

Produce a measured tradeoff curve for each physical card, then validate the selected combination and actual launch path. Follow the user's objective: highest T/W, highest speed, a stated speed floor, or profit. These are different objectives; do not invent a 95%-of-peak filter or an arbitrary watt ceiling. A stable recovery profile can be a useful outcome without being an efficiency winner.

## Essential constraints

- Reuse existing authorization. Research, installation and reading this skill do not authorize GPU mutation, stopping other applications or publishing private evidence. Finish the work already authorized without asking for every diagnostic substep.
- Wait while the selected card has competing work. Identify the actual process, GPU and engine before declaring it busy: desktop composition, an idle GPU context and an AI workload are different observations. Stop only the owned miner if competing work begins. Keep observation bounded and the owning session active.
- Match UUID, PCI, miner ID and, when using Windows engine counters, adapter LUID. Keep per-card data separate and serialize hardware control. Do not assume display, NVIDIA and miner ordering agree.
- Snapshot readable offsets, PL and fan policy before mutation. Establish clock locks as known-unlocked or use a verified snapshot/restore adapter. Unsupported getters do not mean zero. Keep cleanup unconditional, ownership explicit and restoration independently checked.
- Freeze durations, warmup, report-window coverage, thermal/RAM limits, fan policy and stop rules before execution. Stop on CUDA/backend/HW/control errors or unknown invalid proof; HW=0 and cool temperatures do not establish stability. Preserve faults; no automatic hardware-fault retry or repeated push beyond a failed boundary.
- Use energy delta/time when supported, otherwise consistently labeled sampled power. GPU watts are not wall watts. Keep supply gaps and desktop activity in the evidence; contaminated or explicitly non-comparable results cannot win a controlled ranking.
- Deduplicate timestamp/device report windows and require owner-pool proof. Keep expired work separate from unknown invalid proof. A short run with no accepted shares may be inconclusive. Never weaken coverage after looking at results.
- Validate singles, then the combination, then the real desktop/terminal entry. A short pass is screening evidence; later failure withdraws deployment confidence. Validate daily AUTO fan operation separately from a fixed-fan experiment.
- Finish stopped with restoration proof unless continued mining was requested. Deploy validated settings through the actual guard/BAT/shortcut chain, with backups and effective-command checks. State any remaining optimization or endurance work plainly.

## Read only the relevant material

- **Design an experiment or choose a point:** [protocol.md](references/protocol.md), including the core-first/VRAM-first alternatives, V/F behavior, PL sweep and A1/B/A2 comparison.
- **Use the bundled Windows runner:** [srb-windows.md](references/srb-windows.md) before any `--run`. It is a basic harness, not the complete daily controller described in the case study. Its coarse idle check, core-temperature-only limit and strict clock tolerance may make it unsuitable for a particular plan; adapt and calibrate first rather than bypassing a guard.
- **Diagnose Windows idle, permissions, thermal sensors, signals or desktop deployment:** [windows-operations.md](references/windows-operations.md).
- **Classify a disconnect, rejection, RAM increase or crash:** [failure-triage.md](references/failure-triage.md).
- **Work on Linux/Turing hardware:** [linux-turing.md](references/linux-turing.md). The 12 GB RTX 2060 observations do not define limits for every 2060 or another architecture.
- **Review actual successes and failures:** [initial case study](references/case-study.md) and [later endurance/deployment follow-up](references/case-followup.md). Values are historical measurements, not presets.
- **Find sources:** [research-sources.md](references/research-sources.md) separates manufacturer/API information, miner release notes and community experiments.
- **Publish reusable evidence:** [evidence-publication.md](references/evidence-publication.md). Use the whitelist exporter and inspect the exact files to publish.

## Tools and capability boundary

Python 3.10+; standard-library scripts. Use explicit UTF-8 on Windows.

| Tool | Actual capability |
|---|---|
| `scripts/hardware.py` | Windows NVIDIA telemetry/offset readback and owned child helpers; probe does not mutate GPU controls. |
| `scripts/sweetspot.py` | Offline schema/command validation, read-only live preflight by default, explicit bounded `--run`; basic core-temperature/commit checks and stop/restore. |
| `scripts/analyze.py` | Offline curves, separate power-method groups, Pareto frontier and A1/B/A2; rejects explicit non-comparability flags. Input assertions still need raw evidence. |
| `scripts/export_evidence.py` | Offline whitelist export of a private measurement summary to an anonymous public capsule; no raw paths, wallet, commands or event XML. It does not independently audit validity. |

The advanced PID/LUID classifier, per-board junction/hotspot safeguards, temporary metadata privilege handling, AUTO fan controller and foreground launcher from the private case are documented methods, **not implemented features of the bundled live runner**. Other miners, platforms and board-specific sensors require a calibrated adapter. Do not copy a documentation example into production and claim it was live-tested there.

Return requested and actual settings, hash rate, power method/scope, T/W, pool proof, rejections, errors, exposure, cleanup and remaining uncertainty. State whether launchers were deployed and whether mining is running. Distinguish deterministic checks, historical hardware experiments and independent model behavior testing.
