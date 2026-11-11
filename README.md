# GPU Mining Sweet Spot — reusable AI skill

Find a GPU's measured speed/power tradeoff, validate the chosen operating point, and check the real deployment path. Start with [SKILL.md](SKILL.md). [繁體中文](#繁體中文)

## Method library

- Algorithm-aware core/VRAM order, V/F behavior, combinations, PL reduction, per-card data and A1/B/A2 comparisons: [protocol](references/protocol.md).
- Windows desktop versus compute activity, adapter identity, token privilege differences, fan/thermal coverage, owned stop and actual shortcut validation: [Windows operations](references/windows-operations.md).
- CUDA/HW versus pool waits, stale versus invalid work, RAM growth and bounded recycling: [failure triage](references/failure-triage.md).
- RTX2060 variants, unreadable junction telemetry and Linux lifecycle/control differences: [Linux/Turing](references/linux-turing.md).
- Historical measurements, including later failures after short passes: [initial study](references/case-study.md), [endurance follow-up](references/case-followup.md), [source bibliography](references/research-sources.md).
- Speed-first tuning with fixed-clock offsets, stepped PL and daily AUTO revalidation: [speed-retention method and later case](references/speed-retention.md).
- Publishing anonymous evidence with limits intact: [publication guide](references/evidence-publication.md).

## Implemented tools and limits

The repository includes a basic Windows NVIDIA/SRBMiner experiment harness, portable offline analysis, synthetic regressions, 42 historical screening summaries and an anonymous endurance capsule. The private daily controller's advanced PID/LUID, per-board junction/hotspot, AUTO fan and foreground controls are documented techniques; they are **not all implemented by the bundled harness**. Read its [capability boundary](references/srb-windows.md) before using it.

Highest T/W can reduce hash rate. Maximum speed, lowest watts and profit are different objectives. This project offers no universal preset, global optimum or overnight stability claim, ships no miner binary, and does not modify antivirus, BIOS or drivers. GPU power is not wall power.

## Use as a skill

```text
git clone https://github.com/teateatea03/gpu-mining-sweetspot.git
```

For Codex, install the repository under `~/.codex/skills/gpu-mining-sweetspot`, start a new chat and invoke `$gpu-mining-sweetspot`. Other skill-capable agents can read `SKILL.md` and use their own installation mechanism. Installation alone authorizes no hardware operations.

Example:

> Use this skill to measure my GPUs' speed/power curve. My objective is highest T/W. Wait while a selected card has competing work, test cards separately, then validate the combination. Reuse my existing experiment authorization and preserve other applications. Report the tradeoff, actual launch validation and any remaining uncertainty.

## Offline checks

Python 3.10+, standard-library tools:

```text
python -m unittest discover -s tests -v
python scripts/analyze.py --input examples/measurements.json --output analysis/demo
python scripts/sweetspot.py --config examples/config.example.json --plan examples/plan.example.json --validate-only
```

These commands start no miner. Live configurations contain placeholders. Keep filled configs and raw logs private. See [validation notes](VALIDATION.md) for deterministic, historical hardware and model-testing coverage. The exporter preserves only approved numeric fields; review the exact output before publication. The endurance capsule is evidence for readers, not analyzer input or a preset.

## Later speed-first case

A later SRBMiner 3.8.6 experiment selected a dual-card point after separate offset/PL screens and AUTO fan verification: **396.232 TH/s at 540.278 GPU energy-counter W** over a nominal 30-minute run, owner accepts29/34, rejects0/HW0, retained warmed clock bins, normal stop/restoration and no new relevant driver events. A lower-ceiling AUTO combination remained hardware-valid but intermittently lost clocks. The round also retained a prior Ti driver-reset failure and an interrupted/drifting A/B comparison. See the [method, measured tables and limits](references/speed-retention.md) and [anonymous numeric capsule](examples/speed-retention-capsule.json).

This is a speed-first local operating point, not a new maximum-H/W claim or a controlled percentage improvement over the earlier recovery profile. The publication adds documentation/evidence; it does not implement the private controller in the bundled runner or alter an active miner.

## Earlier recovery case

The initial eight-minute efficiency screening measured 302.35 TH/s at 299.34 GPU W. Later work demonstrated that short passes can fail after deployment. A separate conservative recovery profile completed a nominal one-hour validation: 335.284 TH/s at 503.677 GPU energy-counter W, owner accepted 49/92, no rejects/HW/fatal errors or new relevant driver events, and normal stop/restoration.

These results used different operating points and conditions. The later run retained desktop activity and is explicitly non-comparable for controlled ranking. It establishes a recovery operating point, **not a new maximum-T/W result**. Higher-efficiency retuning remains separate. See the follow-up for exact exposure and limitations.

## 繁體中文

這套技能整理如何找出「算力／耗電」甜蜜點，也保留高算力優先時的取捨。流程包括：辨認演算法瓶頸、原廠與現有參數對照、核心與顯存分別掃描、組合驗證、逐步降低PL、A1/B/A2對照、雙卡長測，以及真正桌面捷徑的啟動、停止與還原驗證。

新增內容包含桌面繪圖造成的忙碌誤判、管理員啟動路徑仍可能有權限差異、不同顯卡的溫度與感測器限制、礦池斷線與無效計算的區分、RAM成長觀測，以及失敗點與短測結果如何正確保留。ETH／RVN經驗用來學方法，參數不能直接套到珍珠幣或其他架構。

公開版明確區分「已實作工具」與「需要自行校準的進階控制流程」。提供匿名的一小時驗證數據，不含錢包、內網位址、硬體識別與私人路徑；保守恢復檔也不會被說成最高T/W。日常風扇AUTO必須另驗證，短測通過與HW=0都不等於長期穩定。

本次另補上「先保留可重現高算力，再減少實際耗電」分支：固定核心時脈搭配offset、逐步降低PL、核對暖機後時脈分布，最後重新驗證自動風扇。雙卡30分鐘平均396.232 TH/s／540.278 GPU W，保留先前驅動重置與不完整對照，不能解讀為最高T/W或過夜穩定。詳見[方法與結果](references/speed-retention.md)。

[MIT license](LICENSE)
