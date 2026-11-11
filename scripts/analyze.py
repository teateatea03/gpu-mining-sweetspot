"""Offline efficiency and Pareto analysis. Never starts a miner or changes a GPU."""
import argparse
import csv
import json
import math
from pathlib import Path


def accepted_rows(reports):
    rows=[];excluded=[]
    for report in reports:
        for gpu,item in report.get('gpus',{}).items():
            comparable=(report.get('performance_comparison_valid',True) is True and item.get('performance_comparison_valid',True) is True and not report.get('pool_work_supply_gap') and item.get('pool_wait_observed') is not True)
            eligible=comparable and all(report.get(k) is True for k in ('valid','graceful','restored')) and item.get('valid') is True and item.get('controls_verified') is True and type(item.get('owner_accepted')) is int and item['owner_accepted']>0 and not report.get('fatal') and not report.get('invalid_rejected')
            numeric=all(type(item.get(k)) in (float,int) and math.isfinite(item[k]) and item[k]>0 for k in ('hashrate_hs','watts'))
            row=dict(gpu=gpu,label=report['label'],settings=item.get('settings'),power_method=item.get('power_method'),power_scope=item.get('power_scope',report.get('power_scope','gpu')),hashrate_hs=item.get('hashrate_hs'),watts=item.get('watts'),owner_accepted=item.get('owner_accepted'),rate_windows=item.get('rate_windows'))
            if not eligible or not numeric or not row['power_method'] or row['power_scope'] not in ('gpu','wall'):
                excluded.append(dict(**row,reason='Missing proof/control/restoration/validity, invalid measurement, fatal error, or explicitly non-comparable workload'))
                continue
            row['efficiency_hs_per_w']=row['hashrate_hs']/row['watts'];rows.append(row)
    return rows,excluded


def analyze(reports):
    rows,excluded=accepted_rows(reports);groups={}
    for row in rows:
        groups.setdefault((row['gpu'],row['power_method'],row['power_scope']),[]).append(row)
    results=[]
    for (gpu,method,scope),items in groups.items():
        frontier=[r for r in items if not any(s['hashrate_hs']>=r['hashrate_hs'] and s['watts']<=r['watts'] and (s['hashrate_hs']>r['hashrate_hs'] or s['watts']<r['watts']) for s in items)]
        results.append(dict(gpu=gpu,power_method=method,power_scope=scope,best_observed_efficiency=max(items,key=lambda r:r['efficiency_hs_per_w']),pareto_frontier=sorted(frontier,key=lambda r:r['watts'])))
    return dict(rows=rows,excluded=excluded,groups=results,limitation='Observed means, not a global optimum or endurance proof; never mix GPU and wall watts or different measurement methods.')


def paired(a1,b,a2):
    result={}
    for uid in b.get('gpus',{}):
        rows=[]
        for report in (a1,b,a2):
            found,_=accepted_rows([report]);found=[r for r in found if r['gpu']==uid]
            if len(found)!=1:
                raise ValueError('Paired comparison requires three valid owner-accepted reports for the same GPU')
            rows.append(found[0])
        if len({(r['power_method'],r['power_scope']) for r in rows})!=1 or rows[0]['settings']!=rows[2]['settings']:
            raise ValueError('A1/A2 settings or power methods differ')
        ah=(rows[0]['hashrate_hs']+rows[2]['hashrate_hs'])/2
        aw=(rows[0]['watts']+rows[2]['watts'])/2
        result[uid]=dict(baseline_hashrate_hs=ah,baseline_watts=aw,hash_change_percent=(rows[1]['hashrate_hs']/ah-1)*100,power_change_percent=(rows[1]['watts']/aw-1)*100,efficiency_change_percent=(rows[1]['efficiency_hs_per_w']/(ah/aw)-1)*100)
    if not result:
        raise ValueError('No comparable GPUs')
    return result


def load(path):
    value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    return value['trials'] if 'trials' in value else [value]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True,help='One normalized report, a trials JSON, or a directory of trial report.json files')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--pair',nargs=3,type=Path,metavar=('A1','B','A2'))
    a=p.parse_args();reports=[]
    for path in sorted(a.input.rglob('report.json')) if a.input.is_dir() else [a.input]:
        reports.extend(load(path))
    result=analyze(reports)
    if a.pair:
        result['paired']=paired(*(load(path)[0] for path in a.pair))
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'analysis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (a.output/'curve.csv').open('w',encoding='utf-8-sig',newline='') as f:
        keys=['gpu','label','hashrate_hs','watts','efficiency_hs_per_w','power_method','power_scope','owner_accepted','rate_windows','settings']
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(result['rows'])
    print(json.dumps({'included':len(result['rows']),'excluded':len(result['excluded']),'groups':len(result['groups'])}))


if __name__=='__main__':
    main()
