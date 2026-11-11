# Linux and Turing case boundaries

The bundled live runner is Windows-only. Use a separately calibrated Linux adapter; do not run Windows code against an SSH host or assume matching API names imply matching behavior.

## Discover the board

Confirm identity through the authorized session, UUID/PCI, GPU/memory variant, driver/kernel, supported PL range, clocks, offsets, sensors and current work. An RTX 2060 12 GB TU106 differs from a 6 GB 2060 or 2060 Super. Marketing memory rate and NVML P2 readings may use different conventions. A community PL of 200 W was outside one board's actual 184 W maximum.

Read manufacturer information and dated operator experience before setting limits. Keep the exact SKU uncertain when only a matching-family page is available. Unsupported junction reads remain null. A tool documented for newer architectures does not establish Turing support. Routine clock tuning does not justify undocumented register access or driver/boot changes.

## Control and lifecycle calibration

Use supported setters and independent getters. Legacy and modern offset APIs differ; do not replace a calibrated setter mid-run just because a newer API example exists. Snapshot relevant readable P-states. A positive V/F offset at fixed core is not an exact millivolt value without voltage telemetry.

Calibrate CPU-only owned process groups, signals, service timeouts and restoration before GPU work. For foreground operation, verify the real graphical session and a terminal/PTY attached to the controller. An SSH connection or stale remote-desktop display does not prove visibility on the physical desktop. Finite experiment services, continuous mining and permanent boot services are different authorizations.

Stop on native faults/Xid, stale telemetry, competing selected-GPU work or failed controls. Restore unconditionally. Do not change unlock, BIOS, boot, kernel, driver or GUI configuration merely to complete this skill.

## Local result, not a preset

One 12 GB board's core/offset/PL candidate improved hash about 13.36% while GPU energy increased about 28.43%, reducing T/W about 11.74%. A speed objective could choose it; maximum efficiency would not. VRAM stayed at original rate because junction temperature was unavailable and memory control differed.

Separate AUTO validation mattered: fan speed varied under firmware policy. Native core telemetry and a conservative core stop did not prove an unreadable junction remained below a chosen ceiling. Preserve that uncertainty and the user's requirements when planning further work. See the dated manufacturer, API and operator links in [research-sources.md](research-sources.md).
