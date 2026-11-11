# Failure classification and recovery

Use both output streams, owner-pool messages, native sensors and driver events. Keep a finite observation/recovery plan. Do not turn every failure into an automatic restart.

| Observation | Interpretation and next action |
|---|---|
| CUDA/backend error, illegal access, nonzero HW, failed control readback | Stop the owned run, restore and audit. Withdraw the candidate. No automatic replay or continued push past that boundary. |
| HW=0 and low temperature | Useful readings, not proof of valid computation or stability. CUDA700 occurred with HW=0 and cool cards. |
| “shared GPU error” on another card | The reporting card need not identify the originating fault. Keep timing and both cards' evidence; do not repeatedly lower only one card while declaring the other innocent. |
| Known pool capacity response, disconnect or socket unavailable | A supply wait, not by itself a GPU fault. A daily controller may allow reconnection with backoff. Retain time, energy and zero-rate samples; do not rank against uninterrupted data. |
| Expired/stale work after a reconnect or new job | Record separately from invalid proof. It can occur without unstable clocks. |
| Generic “core operation rejected,” unknown proof rejection or unclassified backend response | Do not whitelist it as congestion just because a disconnect also occurred. Stop or reconcile before continuing GPU work. |
| Zero warmed hash without evidence of a supply wait | Investigate/stop. A narrow reconnect grace must expire; network waits must not mask CUDA, HW or proof errors. |
| No accepted shares in a short trial | May be inconclusive due to difficulty/exposure. Do not fake proof, count dev-fee shares or immediately blame clocks. |
| High commit, working set, VRAM or whole-machine RAM | Different quantities. Establish which rose and its time course before calling it a leak. |
| Null wrapper exit code, missing samples or forced cleanup | Preserve uncertainty/failure. Reconcile completed work rather than silently replaying it. |

## Supply availability and performance

A supply state machine needs exact owner-pool identity, bounded history, explicit patterns, reconnect timing and tests that computation faults still stop. Owner acceptance can confirm recovery. Reconnect must not mask arbitrary later zeros forever. Do not transplant single-pool index rules into failover without checking indices and the owner/dev-fee distinction.

Get alternate endpoints from official documentation or announcements. Verify DNS, TCP, TLS hostname/certificate and the coin's actual authorization protocol before spending GPU time. Authorize success plus a job proves connectivity, not accepted mining work or independent backend capacity. PearlHash's observed authorization used a params object; an incorrect generic subscribe array returning “Expected object” was a client-protocol mistake, not proof the endpoint was down. Do not publish wallet-bearing dashboard URLs.

## RAM growth and bounded recycling

Sample process private commit and working set alongside workload, shares, network events and elapsed time; keep VRAM separate. A large initial CUDA allocation is not evidence of unbounded growth. Preserve growth rate rather than inferring a secret optimization from allocation size.

For an authorized recycling workaround, use a minimum runtime, consecutive threshold samples, cooldown, restart-rate limit, owned process trees and restoration/readback. The private case's 2 GiB, 30-minute minimum and two-per-hour policy were local choices. GPU faults must never trigger a RAM-policy retry. Calibrate handoff, fan policy and restart-rate limiting separately. Do not concatenate generations into one continuous endurance run. A wrapper workaround does not repair internal allocation logic.

## Preserve failure and recovery evidence

Retain requested/actual settings, both streams, first error time, temperatures, native driver XML, process exit/fallback and restoration. A conservative recovery profile is a deliberate new candidate, not a successful retry of the failed point. Changing several dimensions may be appropriate for recovery, but does not isolate a unique cause.
