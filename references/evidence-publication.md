# Publish the method and evidence safely

Publication requires the user's authorization; reuse it when already given. Prepare and verify the exact public tree before publishing. Keep live mining controllers separate from the documentation checkout so editing a skill cannot change an active experiment.

## Evidence levels

| Level | What it supports |
|---|---|
| Research/source note | A hypothesis or starting range, not a measured gain on this card. |
| Screen | An observed operating point over its stated exposure, not deployment endurance. |
| Endurance | This exact combination and continuous duration passed frozen criteria. Not a global optimum or overnight guarantee. |
| Deployment | The real guard/shortcut/terminal route was checked, with native state and owner acceptance. A helper's success is insufficient. |

Keep failed and incomplete entries. Later failure withdraws deployment confidence for that candidate without rewriting historical measurements. Keep different binaries, fan policies, display roles, power methods and scopes distinguishable. Explicit non-comparable results must not enter comparative rankings.

## Whitelist export

Use an offline copy of the private report:

```text
python scripts/export_evidence.py --input PATH_TO_PRIVATE_REPORT --output publication/capsule.json --label anonymous-endurance --scope endurance --power-scope gpu
```

The exporter supports known numeric summary shapes and assigns neutral GPU aliases. It omits original keys, wallet/worker, commands, UUID/PCI inventory, host/path values, event XML, raw output and backups. Missing telemetry stays null; nonfinite measurements are rejected. Review the exact output: an intentionally supplied label can itself identify someone, and this is not a universal document redactor.

The capsule is a public numeric summary, **not input to `scripts/analyze.py`**. It does not manufacture `controls_verified`, audit private logs or turn an input assertion into proof. Ranking needs normalized reports backed by raw evidence. The analyzer separates power methods/scopes and excludes explicit non-comparability. Legacy GPU-only harness reports default to GPU scope; external reports must specify GPU versus wall scope.

Inspect every changed/tracked file, not just the export. Use a secret scanner and a targeted scan for the source machine's wallet, private address, UUID, account names and path prefixes. Keep identifiers outside the repository and CI logs. Preserve private backups/provenance. Do not publish wallet-bearing diagnostic URLs or account/host screenshots.

## Reproducible claims

Include requested/actual settings, duration/warmup/coverage, continuous generation count, owner proof, rejection categories, power method/scope, thermal coverage, fan policy, cleanup and driver audit coverage. A screenshot or one peak number is insufficient.

State which features exist in released code and which require an adapted controller. Separate CPU tests, read-only probes, historical GPU evidence and model-forward testing. Do not redistribute closed miner binaries or imply their internals were repaired.

Publish one reviewed tree, verify remote files and CI, and report the URL/commit. Updating an installed skill affects later skill loads; it is not a reason to restart mining or unrelated apps.
