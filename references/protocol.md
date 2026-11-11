# Experimental design and selection

## Define the objective before looking at results

T/W means reported hashrate divided by measured watts. Normalize hash units before comparison. Highest hashrate, highest T/W, lowest power and highest net profit are different objectives. Preserve the whole curve; apply a hashrate floor only if the user actually requests one.

For GPU-only measurements: `efficiency = hash/s / GPU W`. Whole-rig efficiency uses simultaneous wall power, including PSU losses and idle components. Sum individual GPU energy-counter watts only to obtain combined GPU watts. Profit requires current net revenue per hash, fees, uptime, currency conversion and the applicable electricity tariff; an efficiency winner need not be a profit winner.

## Discover the bottleneck on this algorithm and card

Read algorithm documentation, miner release notes and dated community reports. ETH-era practice can teach experimental order and voltage/frequency control; its memory-overclock values are not PearlHash presets. Some algorithms are core/compute bound, others bandwidth/latency/capacity bound; miners and GPU architectures can change the bottleneck.

Hold core, offset and power ceiling fixed while comparing a few supported memory states. Hold the chosen memory state while sweeping core. Then compare conservative offset steps at useful core points, and power ceilings at selected combinations. Record actual clock, voltage if available, P-state, temperature, fan, utilization and VRAM occupancy. A memory change can change P-state and attainable core clocks; do not infer a microarchitectural cause from a MHz label alone.

Core offset with a locked target can change voltage/frequency behavior. An offset is not itself a direct voltage measurement. Do not assume a larger offset is always more efficient or stable. Stop at an observed fault, retain the failed point and do not continue pushing the same fault boundary. Tiny requested steps may round to identical hardware states; claims of 1 Hz tuning require measurable hardware support, not a UI entry.

## Finite staged search

1. Freeze binary/hash, driver, pool, algorithm and comparable background workload. Map each physical card to its miner ID. Calibrate telemetry and an explicit stop/restore path.
2. Measure the existing profile as a reference. Distinguish an existing tuned profile from factory automatic Boost. If a factory comparison is requested, measure it separately.
3. Run coarse supported core/memory probes in the algorithm-appropriate or user-requested order. Core-first and memory-first are both useful designs. Keep other dimensions fixed within each comparison and files separated by physical GPU.
4. Combine promising core/memory/offset values. Use finer increments only where observed differences exceed noise and the hardware actually supports them. Check PL separately: a 250 W ceiling does not mean a card consumes 250 W.
5. Re-run finalists longer with owner-pool proof. Bracket the candidate as A1 -> B -> A2 with the same binary, power method and background conditions. Average the two reference measurements for the baseline. Compare efficiency against `mean(reference hash) / mean(reference watts)`; report exposure and variation.
6. Validate selected profiles together after singles. Shared cooling, PSU, CPU/prover, work supply and background applications can change the result. Do not call the sum of two separate single-card measurements a measured dual result.

Write the exact plan, durations, warmup, rate-window guard, minimum independent windows, temperature/RAM limits and maximum idle wait before execution. Estimate total time. Coverage depends on the miner's actual output cadence, which may change during a run. A fixed 10-minute run is not automatically enough for eight post-warmup windows.

## Quantities that must survive analysis

- GPU identity and requested versus actual settings, including active P-state offset readback.
- Distinct rate windows; do not count repeatedly scraped or duplicate console/log rows as new measurements.
- All warm samples for power, including supply/prover gaps. For energy counters: `(end_mJ - start_mJ)/1000/(end_time-start_time)`. Reject counter resets and nonpositive intervals. Keep sampled-power values separately labeled.
- Owner-pool accepted work, stale/expired rejects, invalid-proof rejects, HW counters and both output streams' fatal errors. Dev-fee submissions are not owner-pool proof. A short run with zero accepted shares can be inconclusive rather than broken.
- Temperature, private commit and working set separately. Process commit is not total physical RAM. GPU VRAM is another quantity. Short validation cannot rule out an overnight leak.
- Every early stop, forced stop, restore command result and independent final readback. Preserve failed points, do not silently remove them from a success narrative.

## Decision and uncertainty

Rank only comparable, valid points. Keep different power methods/scopes in separate groups. A Pareto frontier retains points for which no measured point has both more hashrate and less power. The highest observed T/W is one point on that curve; small differences may be indistinguishable in practice.

Confirm the preferred point with repeated/longer exposure proportional to the user's intended use. Similar cards can have different silicon, cooling and memory. Do not claim a unique global optimum, 24-hour stability or the miner's secret optimization from a short local curve. If a run misses a predeclared coverage criterion, keep it incomplete, explain why, and design at most a bounded follow-up from the observed cadence. Do not relabel it as passed by weakening the criterion.

Deployment is a separate evidence step: back up the actual source BAT/config and shortcuts, resolve guard indirection, verify per-GPU vector ordering, keep wallet/pool/thermal/RAM guards, and use a check-only path to prove effective commands without starting mining. Restore and leave stopped unless continuing mining was requested.

## Core-first search and power reduction

A useful sequence from RVN-era practice is:

1. Hold VRAM and PL fixed, increase the chosen core control in small supported steps (15 MHz was one operator's step). Record whether it is an absolute lock, Boost offset or a V/F-curve adjustment. Stop at an error or predeclared limit; a deliberate crash is not required to find a useful point.
2. Return to a conservative lower point. A 30 MHz backoff was that operator's starting margin, not a stability guarantee.
3. Restore the reference core setting; sweep VRAM independently (100 MHz requested increments were an example). Following a fault, a 200-300 MHz backoff was a candidate margin, not a universal value. Stop further pushing that boundary.
4. Combine promising points and validate together. Their effects need not add: power sharing, P-state, memory latency and display traffic can change clocks and stability.
5. Lower PL from the combination's measured demand, for example in supported 5 W steps. Measure hash, voltage when available, actual clocks and energy. A 10 W retreat from an unstable or materially slower point is a candidate to validate, not proof of a sweet spot.

Choose memory-first or core-first based on algorithm sensitivity and the user's requested method. Use coarse probes before fine sweeps. Smaller steps are useful only if they change a measurable hardware state. A direct voltage/frequency curve needs its own supported interface and restore plan; an offset at fixed MHz is not an exact voltage setting.

A PL below previously observed wattage can retain nearly the same hash, but measure it. The allowed minimum PL and actual consumption differ; locking frequency may keep consumption below that minimum limit. Do not invent a 250 W operating budget because an example uses it. Distinguish expected PL throttling from a failed setter: a ceiling may legitimately reduce actual clock. Declare accepted readback semantics before the sweep. The bundled runner's strict clock tolerance is not an adapter for every throttling experiment.

## Speed-first selection at fixed clocks

When speed takes priority, use the [speed-retention branch and measured case](speed-retention.md). Screen core offsets with a fixed supported clock/memory combination, then reduce PL while observing hash uncertainty and the full warmed clock distribution. Freeze the speed criterion before confirmation. A lower power ceiling is not necessarily lower consumption, and retaining a clock bin alone does not establish identical throughput. Revalidate the combination under its daily fan policy; preserve hardware-valid runs that lose clock retention as separate outcomes. Do not turn close means under drifting desktop load into a controlled efficiency claim.

## Algorithm and environment matrix

Keep coin algorithm, miner/kernel version, GPU architecture, memory type/capacity, driver, display role and thermal policy together in each comparison. An ETH bandwidth optimization, RVN compute optimization, synthetic GEMM result or another miner's benchmark does not establish a PearlHash improvement.

Low VRAM frequency may save energy in a compute-heavy miner yet interfere with rendering on a display card. Requested MHz, reported memory MHz and marketing effective data rate are different quantities. Probe supported states and actual behavior instead of assuming a universal multiplier.

If fixed 80% fans were authorized for exploration, restore the agreed daily policy afterward. Validate the finalist again with AUTO fans: temperature-dependent Boost/voltage and shared dual-card cooling can change the operating point. Document core, hotspot and junction sensors separately; an absent sensor is not a safe reading.
