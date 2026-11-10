# Validation and limits

Validated locally on 2026-11-10 with Python 3.12 on native Windows.

- Sixteen deterministic unittest scenarios pass. They cover fatal errors without rate rows, both output streams, stale versus invalid rejects, unit/timestamp normalization, per-device vector ordering, idle waiting without process mutation, owner-proof gating, restoration failure, forced-stop classification, unconditional cleanup on trial exceptions, the eight-window coverage gate, A-B-A arithmetic and power-method separation.
- The bundled offline analyzer runs on the 42 redacted completed screening summaries: 40 owner-proven rows are included and two owner-unproven rows excluded, across three GPU/power-method groups. Failed or aborted runs are recorded separately, not represented as successful rows.
- The refactored NVML adapter performed a read-only probe on both local cards, reading offsets, energy counters and telemetry. The actual default CLI also passed read-only binary/hash/device-ID preflight for both cards without starting mining. A native Python sleeper child exercised the actual Windows Job Object, process-memory reader and graceful owned stop. That smoke test changed no GPU controls and started no miner.
- Skill frontmatter and invocation YAML are parsed and the maintained skill-creator validator is run. Local reference links are checked. The public working tree is scanned with Gitleaks through qtools, plus a targeted privacy check for the source machine's identifiers.
- CI is configured for offline compilation, unittest, schema/command validation and fixture analysis on Linux. CI performs no GPU operations.

The originating real mining runs validate the case study's local measurements and original control implementation. The standalone refactoring has not been re-run through a complete live mining sweep; it needs a short, authorized stop/restore calibration on a new target before long experiments. A deterministic pass does not establish AI decision quality, cross-driver compatibility or endurance.

Manual skill-routing scenarios were reviewed against the instructions: a highest-T/W request keeps lower-hash efficient points; a GPU busy with user work leads to waiting without killing applications; a research-only request does not start mining; missing card mapping or unreadable restoration state blocks mutation while offline preparation continues. These are instruction reviews, not an independent model forward-test or Promptfoo quality evaluation. No additional paid model/provider evaluation was run.

Private raw hardware evidence and deployment backups remain with the originating user. Published numeric summaries are redacted; readers cannot independently audit every underlying raw log from this repository alone. No wallet, internal address, private host path or hardware UUID is needed to use the skill.
