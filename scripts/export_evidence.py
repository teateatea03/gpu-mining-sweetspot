"""Export an anonymous numeric capsule; input validity is not independently audited."""
import argparse
import json
import math
from pathlib import Path
import re


def number(value):
    if type(value) not in (int, float):
        return None
    if not math.isfinite(value):
        raise ValueError('Nonfinite measurement cannot be published')
    return value


def boolean(value):
    return value if type(value) is bool else None


def first_number(item, keys):
    return next((v for k in keys if (v := number(item.get(k))) is not None), None)


def power_method(value):
    if not isinstance(value, str):
        return None
    value = value.lower()
    if 'nvml' in value and 'energy' in value:
        return 'nvml-cumulative-energy'
    if 'sampled' in value:
        return 'sampled-power'
    return None


def export(report, label, scope, power_scope='unknown'):
    if not re.fullmatch('[a-z][a-z0-9-]{0,63}', label):
        raise ValueError('Use a short anonymous lowercase label')
    if scope not in ('screening', 'endurance', 'deployment', 'aborted'):
        raise ValueError('Unknown evidence scope')
    if power_scope not in ('gpu', 'wall', 'unknown'):
        raise ValueError('Unknown power scope')
    if not isinstance(report.get('gpus'), dict) or not report['gpus']:
        raise ValueError('A measurement report with a nonempty gpus object is required')
    exit_info = report.get('exit') if isinstance(report.get('exit'), dict) else {}
    audit = report.get('driver_audit') if isinstance(report.get('driver_audit'), dict) else {}
    graceful = boolean(report.get('graceful', exit_info.get('graceful')))
    result = dict(format='public-evidence-capsule-v1', label=label, evidence_scope=scope,
                  power_scope=power_scope, power_method=power_method(report.get('power_method')),
                  observed_seconds=first_number(report, ('observed_mining_seconds', 'observed_seconds')),
                  nominal_seconds=first_number(report, ('nominal_seconds', 'duration_s', 'seconds')),
                  input_declares_valid=boolean(report.get('valid')), graceful=graceful,
                  restored=boolean(report.get('restored')),
                  performance_comparison_valid=boolean(report.get('performance_comparison_valid')),
                  driver_event_count=number(audit.get('count')), gpus={})
    aliases = {'core_mhz': ('core', 'core_lock', 'core_mhz'),
               'core_offset_mhz': ('core_offset', 'core_offset_mhz'),
               'memory_mhz': ('memory', 'memory_lock', 'memory_mhz'),
               'memory_offset_mhz': ('memory_offset', 'memory_offset_mhz'),
               'power_limit_w': ('PL', 'pl', 'power_limit_w')}
    for index, item in enumerate(report['gpus'].values(), 1):
        if not isinstance(item, dict):
            raise ValueError('GPU measurement must be an object')
        settings = item.get('settings') if isinstance(item.get('settings'), dict) else {}
        hs = number(item.get('hashrate_hs'))
        if hs is None:
            ths = number(item.get('ths'))
            hs = number(ths * 1e12) if ths is not None else None
        result['gpus'][f'gpu-{index}'] = dict(
            settings={k: first_number(settings, keys) for k, keys in aliases.items()},
            hashrate_hs=hs, watts=number(item.get('watts')),
            actual_core_mhz=first_number(item, ('actual_core_MHz', 'actual_core_mhz')),
            actual_memory_mhz=first_number(item, ('actual_memory_MHz', 'actual_memory_mhz')),
            power_method=power_method(item.get('power_method', report.get('power_method'))),
            sampled_watts=number(item.get('sampled_watts')),
            owner_accepted=first_number(item, ('owner_accepted', 'accepted')),
            rate_windows=first_number(item, ('rates', 'unique_measurements', 'rate_windows')),
            native_auto_samples=number(item.get('native_AUTO_samples')),
            all_auto=boolean(item.get('all_AUTO')),
            max_core_c=first_number(item, ('max_core_C', 'max_temperature_c')),
            max_hotspot_c=number(item.get('max_hotspot_C')),
            max_memory_junction_c=number(item.get('max_memory_junction_C')),
            hw=number(item.get('HW')), pool_wait_observed=boolean(item.get('pool_wait_observed')))
    result['limitations'] = ['Input assertions are not an independent raw-log audit.',
                             'Anonymous capsule is not a deployment preset or analyzer input.',
                             'Review the exact output before publishing; raw private logs are omitted.']
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--label', required=True)
    p.add_argument('--scope', choices=('screening', 'endurance', 'deployment', 'aborted'), required=True)
    p.add_argument('--power-scope', choices=('gpu', 'wall', 'unknown'), default='unknown')
    args = p.parse_args()
    value = export(json.loads(args.input.read_text(encoding='utf-8-sig')), args.label, args.scope, args.power_scope)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'exported': True, 'gpu_count': len(value['gpus']), 'raw_private_fields_included': False}))


if __name__ == '__main__':
    main()
