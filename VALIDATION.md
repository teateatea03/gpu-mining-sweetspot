# Validation and limits

## 2026-11-11 publication update

- Twenty-five deterministic unittest scenarios pass with Python 3.12 on native Windows. The original sixteen scenarios remain; nine added cases cover whitelist privacy, missing/non-Boolean assertions, nonfinite/Boolean numbers, capsule/ranking separation, explicit non-comparability, GPU-versus-wall grouping, paired scope mismatches and the offline exporter CLI.
- The original 42 screening summaries still produce 40 included and two excluded rows across three GPU/power-method/scope groups. Short screening rankings do not approve deployment. The anonymous endurance capsule is a separate evidence format, not ranking input.
- Offline compile, schema/command validation and anonymous export are exercised. Skill metadata, local document links, secret scanning and source-identifier checks are part of the publication check. CI runs compilation, unittests, schema/command validation and fixture analysis on Linux without GPUs.
- This update changes documentation and offline evidence/analysis code. It does not start, stop, reconfigure or test the live miner. The operating miner and private daily controller are outside the publication checkout.

## Hardware evidence boundaries

The initial case used real per-card experiments, owner-pool submissions and cleanup, followed by short combined checks. Those runs validate their historical observations, not endurance at every similar setting.

The later private controller completed a nominal one-hour recovery validation with 3592.94 seconds of mining observation, one miner generation, native AUTO fan evidence, no rejects/HW/fatal errors or new relevant System driver events, and normal stop/restoration. It also verified actual foreground deployment and a desktop-token metadata difference. Its sensors, process classifier, fan control and launcher logic are documented in the follow-up; they are not thereby implemented or live-tested in the bundled basic runner.

The bundled refactoring's prior coverage included native read-only NVML offsets/energy/device preflight and CPU-only owned-child lifecycle smoke. It has not been run through a new complete live sweep for this publication. Calibrate a target-specific short stop/restore path before authorizing long experiments. Its coarse all-GPU readiness rule, core-temperature-only check, missing fan controller, strict clock tolerance and partial same-GPU competing-work detection remain explicit limitations. Do not bypass those limitations by relabeling output or claiming private controller coverage applies to this code.

Private raw logs and deployment backups remain with the originating user. The public capsule preserves selected numeric fields and input assertions, not an independently reproducible raw-log audit. Nothing establishes a universal optimum, cross-driver equivalence, a fixed voltage from an offset, an unreadable junction temperature, whole-PC power, overnight memory behavior or profitability.

## Behavior evaluation

Instruction review and deterministic script tests are different from model-forward testing. Any independent scenario pass for this update is recorded separately with scope and limitations; it is not a paid-provider quality benchmark or evidence of live hardware control. See the entrypoint's capability matrix when choosing an adapter.

An independent reviewer attempt returned partial source-based scenario observations, but an evaluator tool path-authority restriction prevented completing the review. Those observations are not publication clearance or a completed independent forward-test. Model behavior remains unmeasured beyond the stated manual/partial inspection.
