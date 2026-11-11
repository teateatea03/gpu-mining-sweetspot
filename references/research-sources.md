# Sources and how to use them

These links were retained from the originating 2026-11-10/11 investigation. Recheck current contents for a new experiment. Manufacturer specifications establish model/API constraints; miner release notes establish version behavior; community reports provide hypotheses, not guarantees for another card.

## Primary sources

- [SRBMiner releases](https://github.com/doktor83/SRBMiner-Multi/releases) and [parameters](https://github.com/doktor83/SRBMiner-Multi/blob/master/Parameters): kernel changes, removed flags, device-vector ordering and reset semantics for the actual binary.
- [SRB 3.7.3 notes](https://github.com/doktor83/SRBMiner-Multi/releases/tag/3.7.3) and [3.8.0](https://github.com/doktor83/SRBMiner-Multi/releases/tag/3.8.0): historical Pearl guidance. Do not assume an older switch still exists.
- [NVIDIA NVML](https://docs.nvidia.com/deploy/nvml-api/) and [device commands](https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlDeviceCommands.html): offsets versus locks, return codes, telemetry and deprecations. An API example is not evidence the card supports it.
- [nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/): actual identity, power bounds and readback.
- [Microsoft AdjustTokenPrivileges](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges), [AttachConsole](https://learn.microsoft.com/en-us/windows/console/attachconsole), [GenerateConsoleCtrlEvent](https://learn.microsoft.com/en-us/windows/console/generateconsolectrlevent): privilege lifetime, console membership and event scope.
- [Gigabyte 2060 12 GB family specification](https://www.gigabyte.com/Graphics-Card/GV-N2060D6-12GD/sp) and [NVIDIA model comparison](https://www.nvidia.com/en-me/geforce/graphics-cards/compare/?section=compare-specs): distinguish chip/memory variants; a family page does not identify an unknown retail SKU.
- [MSI V/F-curve guide](https://www.msi.com/blog/msi-afterburner-overclocking-undervolting-guide): useful concepts, not Linux/Turing voltages to copy.

## Operator experience and sensor coverage

- [5080 PRL](https://www.hashrate.no/gpus/5080/PRL), [3080Ti PRL](https://www.hashrate.no/gpus/3080ti/PRL), [2060 12 GB PRL](https://new.hashrate.no/gpus/206012/PRL) and [RVN](https://hashrate.no/gpus/206012/RVN): record date, miner, driver, board, clock conventions, power method and whether PL is settable. Cross-miner external comparisons do not establish a local tuning gain.
- [ETH/RVN discussion](https://www.reddit.com/r/Ravencoin/comments/oty0ov): historical algorithm/thermal reasoning. Choices for a different memory variant are not safety limits.
- [gddr6_temps support](https://github.com/jjziets/gddr6_temps): newer-series coverage does not establish TU106 support.
- [Official Skypool PRL announcements](https://api.main.skypool.xyz/v1/info/getAnnounce?page=prl): the historical CN backup announcement illustrates checking the pool's own source. A different entrance does not prove an independent verification backend.

Extract the controlled sequence from ETH-era material, not its offsets. Verify the actual algorithm bottleneck locally, then use a finite plan.
