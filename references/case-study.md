# Initial PearlHash screening (historical)

**Later qualification:** Read [the endurance/deployment follow-up](case-followup.md) before using these short results as deployment evidence. The observations below describe the initial session, not the current profile.

Measured on 2026-11-10 using SRBMiner 3.8.6, NVIDIA driver 621.01, one RTX 5080 and one RTX 3080 Ti. The user requested controlled per-card research, followed by maximum validated hashrate per GPU watt. This is a local case study, not universal clock recommendations or a full reproducibility archive. Private raw logs, wallets, UUIDs, network addresses and host paths are not published. `examples/measurements.json` contains normalized, redacted numeric summaries for the offline analyzer.

## Single-card A1 -> B -> A2 comparison

Power is warmed NVML cumulative energy delta/time. Requested values below are core MHz / core offset MHz / memory MHz / PL W.

| Card/profile | Requested settings | TH/s | GPU W | TH/s/W | Owner accepted |
|---|---|---:|---:|---:|---:|
| 5080 A1 | 2610 / +300 / 14801 / 250 | 218.450 | 200.817 | 1.088 | 12 |
| 5080 B | 2640 / +450 / 14801 / 250 | 221.227 | 191.045 | 1.158 | 8 |
| 5080 A2 | 2610 / +300 / 14801 / 250 | 218.545 | 201.830 | 1.083 | 5 |
| 5080 efficient C | 2250 / +450 / 810 / 250 | 182.528 | 132.747 | 1.375 | 6 |
| 3080 Ti A1 | 1650 / +200 / 405 / 250 | 132.815 | 195.277 | 0.680 | 2 |
| 3080 Ti B | 1650 / +300 / 405 / 250 | 132.788 | 182.322 | 0.728 | 6 |
| 3080 Ti A2 | 1650 / +200 / 405 / 250 | 132.840 | 198.370 | 0.670 | 5 |
| 3080 Ti efficient C | 1500 / +200 / 405 / 250 | 120.805 | 164.108 | 0.736 | 4 |

B profiles ran six minutes, C profiles five minutes; all eight segments had zero rejects/HW and normal stop/restoration. B versus bracketed reference: 5080 +1.25% hash / -5.11% power / +6.70% efficiency; 3080 Ti -0.029% hash / -7.37% power / +7.92% efficiency. C improves efficiency more while reducing hash: +26.69% on 5080 and +9.08% on 3080 Ti versus the original references.

All 42 completed screening points remain in the redacted dataset, including screen-valid but owner-unproven short points, which the analyzer excludes from validated ranking. Four aborted/faulted calibration or search points are summarized separately. No hidden 95% hash floor was used. C was the highest observed owner-proven efficiency among these single-card points; small neighboring differences and limited exposure still matter.

## Real failures and measurement lessons

- 3080 Ti 1650 / +350 / 405 / 250 produced E1027 / CUDA700 illegal memory access. Its HW counter remained zero. Three nvlddmkm events occurred in the same second, with native XML containing Out Of Range Address. Cause cannot be proven from this alone. The configuration was excluded; +400/+450 were not executed.
- The original guard looked for fatal errors only after selecting a stream with parseable TH/s rows. A 0 H/s failure could evade that path. It was corrected to scan both log and console unconditionally, then regression-tested against saved output without recreating the GPU fault.
- Windows PowerShell once recorded a null child exit code. Caching `Process.Handle` before waiting fixed the wrapper; original records and successful child evidence were preserved rather than re-running every completed test.
- A ten-minute dual run stopped/restored normally and had owner proof but only seven warmed report windows per card against the planned eight. It remained coverage-incomplete. A separate bounded eight-minute run with a 90-second warmup met the eight-window criterion; the original was not relabeled valid.
- Minimum memory was not universally best on 5080; memory states changed P-state and actual core. The efficient 2250 MHz request actually averaged about 2220 MHz. Voltage and VRAM junction temperature were unavailable.

## Initial-session dual results and chosen objective

The retained-speed B combination passed its supplemental validation at 354.19 TH/s / 378.18 W GPU energy average, 13 owner accepted, zero rejects/HW. The user's final objective was highest T/W, so the C combination was separately validated and deployed:

| Card | Requested settings | Dual TH/s | Dual GPU W | Dual TH/s/W |
|---|---|---:|---:|---:|
| RTX 5080 | 2250 / +450 / 810 / 250 | 181.486 | 133.796 | 1.356 |
| RTX 3080 Ti | 1500 / +200 / 405 / 250 | 120.865 | 165.540 | 0.730 |
| Combined | | 302.351 | 299.336 | 1.010 |

This eight-minute dual validation had eight warmed windows per card, 11 owner accepted, zero rejects/HW, no new fatal errors, graceful stop and verified restoration. Combined efficiency improved about 7.8% over the retained-speed dual run. This is the ratio of combined hashrate to summed GPU watts, not the sum/average of the individual efficiency ratios.

At the end of that initial session, the original launcher/shortcut/guard chain was backed up, three parameter sources updated and effective commands checked without starting mining again. Mining finished stopped, locks reset, offsets read back as zero and original PL restored. Short tests do not prove endurance, fix a historical RAM accumulation issue or establish whole-PC electricity cost. Different measurement methods are explicitly separated.
