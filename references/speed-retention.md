# Preserve speed, then reduce power

Use this branch when the objective is the highest demonstrated stable speed with lower actual watts. Maximizing H/W alone can select a slower operating point. The following case used PearlHash and SRBMiner 3.8.6; numbers describe two individual boards, not architecture-wide presets.

## Search and selection

1. Establish a repeatable speed reference at a conservative supported core/memory combination, with enough PL headroom. Identify whether memory changes affect hash rate, P-state or display behavior. Preserve requested and actual clock units; memory MHz labels are not effective transfer rates.
2. At fixed core lock and memory, screen conservative positive core offsets. The offset can alter the V/F operating point needed to sustain the same clock. It is not a measured voltage or a guarantee that a larger offset is better. If voltage telemetry is unavailable, record null; a voltage-limit Boolean is not voltage.
3. Lower PL in supported steps while holding the selected combination fixed. Compare real energy/time, warmed hash and the full actual clock distribution. A lower PL that neither lowers actual watts nor preserves clocks is not an improvement. Distinguish a supported hardware bin, such as requested 3000 and actual 2992 MHz, from additional PL throttling.
4. Freeze the speed-retention criterion before the final comparison. Use repeated comparable runs or uncertainty estimates for a hash-based criterion. Actual clock-bin retention is useful corroboration for this case, not a universal proof of equal throughput. Do not invent a speed floor or declare equality from two close means.
5. Validate singles, the combination, then the intended daily fan policy. Fixed-fan results do not transfer unchanged to AUTO: warmer silicon can change power demand. If the combination loses clocks, preserve that run as hardware-valid if it met its frozen criteria, but do not promote it as full-speed preservation. A bounded refinement needs a new written plan and unchanged coverage; avoid unlimited clock chasing.
6. Check the real launch route with fresh owner-pool accepts per card, native fan policy, actual clocks, binary/command vectors and a visible console if requested. A direct miner launcher can remain direct; experimental instrumentation does not require installing a production watchdog. Document which thermal safeguards remain in daily operation.

Light desktop activity can make a practical operating point useful while invalidating a controlled A/B efficiency ranking. An interrupted A1/B/A2 sequence or drifting reference remains incomplete/non-comparable. Never average it into a claimed percentage improvement.

## Historical per-card screens

These are separate finite screens with fan80, not a uniform controlled comparison across every row. GPU W uses NVML cumulative energy divided by elapsed time, not wall power. Preserve idle/work-supply gaps in the measured interval and keep sampled watts separately labeled.

| Board | Core lock / offset MHz | Memory lock MHz | PL W | TH/s | GPU W | Observation |
|---|---|---:|---:|---:|---:|---|
| RTX 3080 Ti | 1770 / +200 | 405 | 255 | 142.472 | 241.741 | Full 1770 clock |
| RTX 3080 Ti | 1770 / +200 | 405 | 250 | 142.230 | 243.866 | Full clock; one expired-work reject |
| RTX 3080 Ti | 1770 / +200 | 405 | 245 | 142.000 | 241.194 | Mean clock about 1761.7; throttled |
| RTX 5080 | 3000 / +450 | 14801 | 290 | 253.830 | 284.491 | Actual 2992 clock retained |
| RTX 5080 | 3000 / +450 | 14801 | 285 | 252.834 | 281.518 | Mean clock about 2984.6 |
| RTX 5080 | 3000 / +450 | 14801 | 280 | 251.802 | 276.899 | Further clock/speed reduction |

The Ti screen at 1800/+200 suffered a driver reset, despite core/memory temperatures below the stop limits. Initial cleanup failed during the driver fault; a separate recovery readback succeeded. The failed point was preserved and not automatically retried. Subsequent testing backed down to 1770. Cool temperatures and HW=0 do not establish stability.

An offset A1/B/A2 comparison was interrupted by desktop activity; its later reference drifted. Those data do not establish a controlled offset gain or a global optimum.

## Combination and AUTO verification

| Nominal continuous exposure | Ti PL / 5080 PL W | Mean total TH/s | Total GPU energy W | Classification |
|---|---|---:|---:|---|
| 30 min AUTO | 255 / 290 | 395.6139 | 537.0480 | Hardware-valid, intermittent lower clock bins after warming |
| 30 min AUTO | 260 / 295 | 396.2322 | 540.2781 | Selected; warmed target clock bins retained |

Only the PL ceilings changed for this bounded refinement. The second run measured about 3.23 W more GPU energy power, not the 10 W sum of ceiling increments. The close means are observations under ordinary desktop conditions, not a controlled causal gain estimate or proof that every lower-power combination is worse.

Final plan: 1800 seconds, 180-second warmup plus 90-second report guard, at least 15 unique timestamp/device rate windows per card, fresh owner proof, no CUDA/HW/unknown-invalid-proof errors, thermal bounds, clean owned stop/restoration and a fresh System driver-event audit. The case used core stop limits 80/75°C, Ti hotspot95°C and memory junction90°C under a user ceiling92°C; these are local policies, not universal board ratings.

| Final result | RTX 3080 Ti | RTX 5080 |
|---|---:|---:|
| Core lock / offset MHz | 1770 / +200 | 3000 / +450 |
| Actual warmed core MHz | 1770 | 2992 |
| Memory lock / offset MHz | 405 / 0 | 14801 / 0 |
| PL W | 260 | 295 |
| Mean TH/s | 142.2389 | 253.9933 |
| Mean GPU energy W | 252.1207 | 288.1575 |
| Unique rate windows | 18 | 18 |
| Owner accepted | 29 | 34 |
| Warmed clock/fan samples | 300 | 300 |
| Max core / memory junction °C | 75.88 / 72 | 70.81 / 62 |
| Max hotspot °C | 85.78 | unavailable |

Final combined rejects0/HW0; all warmed samples had AUTO fan policy and the listed actual core bin. A post-run System query after a saved EventRecordID watermark found no new Display, nvlddmkm or WHEA events; query/log continuity and the frozen plan hash were checked. This audit covers the final run and does not erase the earlier driver reset.

Three launchers (each single and the pair) passed offline parameter/vector/binary checks. The selected pair was started in a visible administrator console, native AUTO and clocks were read back, and both cards produced fresh owner-pool accepts from the new session. Daily operation used direct SRB with native core-temperature protection, without the experiment's full junction/hotspot observer. SRB's `--gpu-reset-oc` was verified as reset-on-start; reset-on-exit was not promised.

The round executed23 cases:20 passed;3 did not pass (instrumentation abort, driver reset, desktop interruption). The public [numeric capsule](../examples/speed-retention-capsule.json) is an anonymized whitelist export of the final run, not a raw-log audit or analyzer input. Raw logs, hardware identifiers, wallet, private launchers and event XML remain private. Earlier one-hour recovery data are from different settings/conditions and cannot establish a before/after improvement percentage. No overnight stability or universal optimum was established.

## Reuse boundaries

These are documented techniques from an adapted private controller. The bundled basic runner does not gain AUTO, junction/hotspot, refined activity classification or full-clock-bin selection simply because this reference exists. Calibrate and validate an appropriate adapter before live use; do not copy these historical values to another GPU.
