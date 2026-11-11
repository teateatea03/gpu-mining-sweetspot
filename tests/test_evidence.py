import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import analyze
import export_evidence as evidence


def source():
    return {'valid': True, 'exit': {'graceful': True}, 'restored': True,
            'performance_comparison_valid': False, 'observed_mining_seconds': 3593,
            'power_method': 'NVML cumulative GPU energy', 'driver_audit': {'count': 0, 'xml': 'PRIVATE_EVENT_MARKER'},
            'session': 'PRIVATE_PATH_MARKER', 'command': ['PRIVATE_WALLET_MARKER'],
            'gpus': {'PRIVATE_UUID_MARKER': {'settings': {'core': 1500, 'core_offset': 0, 'PL': 200},
                       'ths': 120, 'watts': 180, 'sampled_watts': 185, 'owner_accepted': 4, 'rates': 38,
                       'HW': 0, 'all_AUTO': True, 'raw_log': 'PRIVATE_NETWORK_MARKER'}}}


class EvidenceTests(unittest.TestCase):
    def test_whitelist_omits_nested_private_values_and_gpu_keys(self):
        result = evidence.export(source(), 'example-endurance', 'endurance', 'gpu')
        self.assertNotIn('PRIVATE_', json.dumps(result))
        self.assertEqual(list(result['gpus']), ['gpu-1'])
        self.assertEqual(result['gpus']['gpu-1']['hashrate_hs'], 120e12)
        self.assertEqual(result['gpus']['gpu-1']['watts'], 180)
        self.assertIsNone(result['gpus']['gpu-1']['settings']['memory_mhz'])
        self.assertFalse(result['performance_comparison_valid'])

    def test_string_false_and_missing_telemetry_do_not_become_proof(self):
        value = source(); value['valid'] = 'false'; del value['restored']
        result = evidence.export(value, 'incomplete', 'screening')
        self.assertIsNone(result['input_declares_valid']); self.assertIsNone(result['restored'])
        self.assertEqual(result['power_scope'], 'unknown')

    def test_nonfinite_measurement_rejected(self):
        value = source(); value['gpus']['PRIVATE_UUID_MARKER']['watts'] = float('nan')
        with self.assertRaises(ValueError): evidence.export(value, 'bad', 'aborted')

    def test_capsule_cannot_accidentally_enter_validated_rankings(self):
        result = evidence.export(source(), 'endurance', 'endurance')
        self.assertEqual(analyze.analyze([result])['rows'], [])

    def test_explicit_noncomparable_measurement_excluded_from_rankings(self):
        r = {'label': 'desktop', 'valid': True, 'graceful': True, 'restored': True,
             'performance_comparison_valid': False, 'gpus': {'card': {'valid': True,
             'controls_verified': True, 'owner_accepted': 3, 'hashrate_hs': 100,
             'watts': 50, 'power_method': 'nvml-energy'}}}
        self.assertEqual(analyze.analyze([r])['rows'], [])

    def test_wall_and_gpu_watts_cannot_share_a_frontier(self):
        base = {'label': 'gpu', 'valid': True, 'graceful': True, 'restored': True,
                'gpus': {'card': {'valid': True, 'controls_verified': True,
                'owner_accepted': 1, 'hashrate_hs': 100, 'watts': 50, 'power_method': 'sampled-power'}}}
        wall = json.loads(json.dumps(base)); wall['label'] = 'wall'; wall['power_scope'] = 'wall'
        self.assertEqual(len(analyze.analyze([base, wall])['groups']), 2)
        with self.assertRaises(ValueError): analyze.paired(base, wall, base)

    def test_boolean_numbers_do_not_establish_measurement_or_owner_proof(self):
        for key in ('hashrate_hs', 'watts', 'owner_accepted'):
            item = {'valid': True, 'controls_verified': True, 'owner_accepted': 1,
                    'hashrate_hs': 100, 'watts': 50, 'power_method': 'nvml-energy'}
            item[key] = True
            value = {'label': 'bad-number', 'valid': True, 'graceful': True,
                     'restored': True, 'gpus': {'card': item}}
            self.assertEqual(analyze.analyze([value])['rows'], [])

    def test_unqualified_comparison_marker_excluded(self):
        for marker in (None, 'false'):
            value = {'label': 'unknown', 'valid': True, 'graceful': True, 'restored': True,
                     'performance_comparison_valid': marker,
                     'gpus': {'card': {'valid': True, 'controls_verified': True,
                     'owner_accepted': 1, 'hashrate_hs': 100, 'watts': 50, 'power_method': 'nvml-energy'}}}
            self.assertEqual(analyze.analyze([value])['rows'], [])

    def test_offline_export_cli_preserves_measurements_without_private_fields(self):
        script = Path(__file__).resolve().parents[1]/'scripts/export_evidence.py'
        with tempfile.TemporaryDirectory() as d:
            input_path = Path(d)/'input.private.json'; output = Path(d)/'capsule.json'
            input_path.write_text(json.dumps(source()), encoding='utf-8')
            p = subprocess.run([sys.executable, str(script), '--input', str(input_path),
                                '--output', str(output), '--label', 'cli-example',
                                '--scope', 'endurance', '--power-scope', 'gpu'], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertNotIn('PRIVATE_', output.read_text(encoding='utf-8'))


if __name__ == '__main__': unittest.main()
