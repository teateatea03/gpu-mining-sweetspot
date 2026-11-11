# Windows operation and deployment

Read this when investigating readiness, thermal coverage, signals or the actual desktop entry. These methods were exercised by a private daily controller; the bundled `sweetspot.py` does not implement this whole controller.

## Identify activity before declaring a GPU busy

A WDDM process list can include idle clients. A PDH percentage is an engine utilization reading, not proof of an AI job. Desktop composition on a low-clock card can report a substantial percentage while board power remains near idle. A blanket 1% per-PID rule or 15% total-utilization rule repeatedly blocked normal desktop use in the case study.

A calibrated observer can:

1. Read `GPU Engine(*)/Utilization Percentage` with `PdhAddEnglishCounterW`, retaining timestamp, PID, engine, adapter LUID and counter status. Wait for a valid sample interval; do not reuse the first initialization sample.
2. Enumerate DXGI adapters and independently join LUID to the selected physical GPU. Names alone are ambiguous when identical cards are present; obtain an unambiguous mapping or stop that branch. Never infer PCI/miner order from DXGI display order.
3. Read the executable's full path using limited query rights. Treat a verified system compositor and an explicitly allowed UI application differently from unknown compute or encoding. Do not exempt an executable just because its basename is `dwm.exe` or `chrome.exe`.
4. Combine engine type, sustained readings, actual board power and observed background work. Calibrate any allowed desktop envelope on this machine. The private controller's thresholds are examples, not a universal busy test. Log blockers with identity and reason instead of printing only “GPU busy.”
5. During mining, exclude only PIDs in the owned Job Object. Use a sustained trigger to stop the owned miner when competing selected-GPU work begins. Do not stop an unselected GPU's user workload or label its presence as corruption of selected-GPU data.

Keep raw observations. Allowing light desktop activity supports practical operation; it does not make the resulting hash/power mean a quiet controlled A/B benchmark.

## Administrator identity can still differ by launch route

The same user had different effective token privilege states when starting through an elevated PowerShell helper and directly through a desktop CMD/BAT. `QueryFullProcessImageNameW` returned a path in one route and an empty result for the protected desktop compositor in the other. This caused a second false wait after the headless test had passed.

When already authorized to use the administrator interface, the private reader temporarily enabled an existing `SeDebugPrivilege` on its own process token using `OpenProcessToken`, `LookupPrivilegeValueW` and `AdjustTokenPrivileges`. It checked `GetLastError` including `ERROR_NOT_ALL_ASSIGNED`, saved the previous state, and restored that state on close. It did not change Windows security policy. If identity remains unavailable, report a metadata/access limitation; it is not evidence of heavy GPU work. Do not guess credentials or disable process protections.

Verify through the real desktop entry: before activation, during the query, and after restoration. Do not assume a hidden helper reproduces the foreground token. Permission restoration is per reader lifetime; keep nested/concurrent readers from undoing each other's state.

## Temperature and fan coverage

Core, hotspot and memory junction are separate signals. Calibrate availability per physical board and driver. NVML may lack a sensor that another supported interface can expose; verify the alternative before relying on it. Keep unavailable values null, not zero. Read actual memory type, board limits and cooling configuration; another GPU series or an RVN report is not its thermal specification.

Use timestamp/latency checks so a stale low temperature cannot pass. The private dual controller used per-board core/hotspot limits and a 90°C junction stop under a user ceiling of 92°C. These were local limits. Its fan policy was verified through native AUTO-policy readback on every channel, not by expecting a fixed fan percentage. Record original fan policy and restore it even after a partial setter failure. The public harness currently checks core temperature only and has no fan-policy controller.

## Owned stop and outcome propagation

Keep a real Popen handle and an owned kill-on-close Job Object. Signal only the owned child process group. If console attachment differs, use a separate short-lived helper attached to that owned console; do not detach the user's foreground console or broadcast to unrelated processes. A helper can attach, send CTRL_BREAK to the child group, exit, and let the controller wait and reap. Failures and timeouts remain evidence.

A Python handler may not execute promptly during a long blocking sleep/wait. Short interruptible wait slices keep a RAM guard responsive. Give the outer controller enough time for the inner controller's bounded cleanup, and propagate the inner exit code. An outer return of zero cannot override an inner forced stop or failure. Preserve the Job fallback for a wedged CUDA process, but never mark that fallback graceful or use it to justify automatic retry.

Test this path first with responsive CPU-only parent/child fixtures, then a bounded actual miner. A long Python sleeper that cannot handle its pending signal can misdiagnose the fixture as a console failure. CPU success does not prove native miner cleanup.

## Deploy the source chain actually used

Back up the source config/BAT, guard modules and existing shortcuts. Resolve each link to its effective command, binary/hash, wallet, pool/TLS, device-vector order, thermal/RAM rules and fan policy. Verify check-only without starting a second miner. Test each single-card command mapping and the combined vector.

Then use the requested foreground entry. Match the new launch receipt's exact PID, creation time and visible window; do not reuse a prior visible PID or merely the newest old log. Require a new session, live miner, actual native parameters, AUTO policy if requested, and owner accepted work on every selected GPU. Keep busy waiting separate from a successful start. Avoid GPU capture/overlay tools while measuring: the observer can change performance.

Audit System driver events using an invariant UTC XPath/FilterXml query. Save native event XML if formatted messages are unavailable. Correlate time/device without asserting a unique cause. A later idle audit with no new events does not erase events from an earlier failed run.
