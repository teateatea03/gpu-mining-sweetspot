# GPU Mining Sweet Spot — reusable AI skill

Find the highest **measured hashrate per watt**, with per-card experiments, algorithm-aware clock/memory sweeps, pool proof and reversible control. The skill is in [SKILL.md](SKILL.md); an AI can read that file and load only the relevant references.

[繁體中文說明](#繁體中文)

## What is included

- A finite experimental protocol: memory states, core levels, offset combinations, power ceilings, A1/B/A2 comparisons and final multi-GPU validation.
- A Windows NVIDIA/SRBMiner adapter with read-only defaults, idle waiting, UUID/PCI/device-ID checks, energy counters, fatal-log checks and owned-child cleanup.
- A portable offline analyzer for T/W, full tradeoff curves, Pareto frontiers and paired comparisons; different power methods are kept separate.
- A redacted PearlHash case study, 42 numeric screening summaries, and regressions for faults that actually occurred.

The selected objective matters: maximum T/W can sacrifice hashrate. This project does not promise a universal optimum, 24-hour stability, whole-PC watts or profitability. It ships no miner binaries or preset applicable to every GPU. Other miners/vendors/operating systems need a calibrated adapter; the bundled live adapter targets native Windows/NVIDIA/SRBMiner.

## Use as a skill

Clone this repository, then point your AI at `SKILL.md`:

```text
git clone https://github.com/teateatea03/gpu-mining-sweetspot.git
```

For Codex, copy the repository files into the user skill directory under `gpu-mining-sweetspot` (normally `~/.codex/skills/gpu-mining-sweetspot`), then start a new chat and invoke `$gpu-mining-sweetspot`. Other skill-capable agents can install the same `SKILL.md`, scripts and references using their own skill mechanism. Reading a skill does not itself authorize mining or changing another machine.

Example request:

> Use this skill to find my GPUs' highest validated hashrate per watt. Wait while a GPU is busy, test each card separately, then validate the combination. Keep the original launchers until deployment is authorized and finish mining stopped.

## Offline demonstration

Python 3.10+; no pip packages required by the bundled scripts:

```text
python -m unittest discover -s tests -v
python scripts/analyze.py --input examples/measurements.json --output analysis/demo
python scripts/sweetspot.py --config examples/config.example.json --plan examples/plan.example.json --validate-only
```

These commands do not start mining or change GPU controls. The example live configuration contains placeholders; its clock values are schema illustrations. Read [the Windows adapter reference](references/srb-windows.md) before any `--run`. Keep filled configurations and raw run artifacts private. Only the user's explicit task authorizes live hardware experiments; no startup service or permanent monitoring is installed.

## Evidence

The [case study](references/case-study.md) explains the method's actual results and failures. The final efficiency-priority combination measured **302.35 TH/s at 299.34 W of summed GPU energy-counter power**, approximately **1.010 TH/s/W**, over eight minutes, with 11 owner accepted / 0 rejected / 0 HW. These are short local measurements on an RTX 5080 and RTX 3080 Ti. The same requested clocks need not produce the same actual clocks or efficiency on another card.

[Validation notes](VALIDATION.md) distinguish historical live experiments, deterministic tests, read-only probing and refactored live-runner coverage. [MIT license](LICENSE).

## 繁體中文

這套技能讓 AI 尋找顯卡挖礦的 **T/W 甜蜜點（算力 ÷ 功耗）**。每張卡先分開測試，再驗證雙卡組合；會等待使用中的顯卡，不會關閉你的工作程式。

核心流程包含辨認演算法瓶頸、比較顯存檔位、掃描核心、組合核心偏移與功耗上限、原設定前後對照、礦池接受確認，以及停止後還原。完整曲線會保留，失敗點也不隱藏。ETH 時期的調校方法可以參考，參數不能直接照抄到別的演算法。

把整個資料夾安裝成技能後，在新對話使用 `$gpu-mining-sweetspot`。其他 AI 也可以從 `SKILL.md` 開始讀。單純閱讀或安裝技能不會啟動挖礦；實際測試需要使用者授權，並依目標硬體校準停止及還原機制。

功耗以 GPU 能耗計或明確標示的取樣值計算，**不是整機插座功耗**。短測不等於長期穩定、全域最佳或獲利保證。案例參數只作研究證據，不能視為所有同型號顯卡的預設值。
