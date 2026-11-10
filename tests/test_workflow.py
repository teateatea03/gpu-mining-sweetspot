import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import analyze as a
import sweetspot as s


def report(label='B',hs=100,watts=50,method='nvml-energy'):
    return dict(label=label,valid=True,graceful=True,restored=True,fatal=[],invalid_rejected=[],gpus={'GPU-A':dict(valid=True,controls_verified=True,owner_accepted=2,rate_windows=8,hashrate_hs=hs,watts=watts,power_method=method,settings={'core_mhz':1500})})


class WorkflowTests(unittest.TestCase):
    def test_backend_failure_without_rate_rows(self):
        fatal,_,_=s.log_errors('', 'GPU0 0 H/s\nPearl backend error E1027 (CUDA error 700: illegal memory access)')
        self.assertTrue(fatal)
        self.assertEqual(s.records('GPU0 0 H/s'),[])

    def test_log_fatal_survives_console_fallback(self):
        self.assertTrue(s.log_errors('CUDA error 700','everything looks normal')[0])

    def test_stale_is_recorded_but_invalid_proof_is_fatal(self):
        _,rejects,invalid=s.log_errors('share rejected stale job\nshare rejected invalid proof','')
        self.assertEqual(len(rejects),2);self.assertEqual(len(invalid),1)

    def test_timestamp_dedup_unit_normalization_and_zero_hw(self):
        line='[2026-01-01 01:00:00] GPU0 Model: 1.25 TH/s [A:2 R:0 HW:0]'
        rows=s.records(line+'\n'+line)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['hashrate_hs'],1.25e12)

    def test_low_hash_efficient_point_not_dropped_by_hidden_floor(self):
        data=a.analyze([report('fast',100,100),report('efficient',70,40)])
        self.assertEqual(len(data['rows']),2)
        self.assertEqual(data['groups'][0]['best_observed_efficiency']['label'],'efficient')
        self.assertEqual(len(data['groups'][0]['pareto_frontier']),2)

    def test_no_owner_proof_and_restore_failures_excluded(self):
        no_proof=report('no-proof');no_proof['gpus']['GPU-A']['owner_accepted']=0
        bad_restore=report('bad-restore');bad_restore['restored']=False
        data=a.analyze([report(),no_proof,bad_restore])
        self.assertEqual(len(data['rows']),1);self.assertEqual(len(data['excluded']),2)

    def test_mixed_power_methods_not_ranked_together(self):
        data=a.analyze([report(),report('sampled',100,20,'sampled-power')])
        self.assertEqual(len(data['groups']),2)
        with self.assertRaises(ValueError):
            a.paired(report('A1'),report(),report('A2',method='sampled-power'))

    def test_paired_reference_is_bracket_mean(self):
        result=a.paired(report('A1',100,100),report('B',100,80),report('A2',100,100))['GPU-A']
        self.assertAlmostEqual(result['efficiency_change_percent'],25)
        self.assertAlmostEqual(result['power_change_percent'],-20)

    def test_nonfinite_measurements_excluded(self):
        data=a.analyze([report(hs=float('nan')),report(watts=-1)])
        self.assertEqual(data['rows'],[])

    def test_command_order_uses_miner_id(self):
        config=dict(executable='miner.exe',algorithm='algo',pool='pool',wallet='wallet',devices=[dict(uuid='B',miner_id=1),dict(uuid='A',miner_id=0)])
        trial=dict(settings=[dict(uuid='B',core_mhz=2000,core_offset_mhz=100,memory_mhz=1000,power_limit_w=200),dict(uuid='A',core_mhz=1500,core_offset_mhz=50,memory_mhz=500,power_limit_w=150)])
        cmd=s.command(config,trial,Path('run'))
        self.assertEqual(cmd[cmd.index('--gpu-id')+1],'0,1')
        self.assertEqual(cmd[cmd.index('--gpu-cclock0')+1],'1500,2000')
        self.assertEqual(cmd[cmd.index('--gpu-coffset0')+1],'50,100')

    def test_busy_wait_does_not_start_or_kill_any_process(self):
        with patch.object(s,'preflight',side_effect=[s.BusyGpu('busy'),{'GPU-A':{}}]),patch.object(s.time,'sleep') as sleep,patch.object(s.subprocess,'Popen') as start:
            self.assertEqual(s.wait_ready({},None,60),{'GPU-A':{}})
            sleep.assert_called_once();start.assert_not_called()

    def test_restore_failure_is_recorded(self):
        nvml=Mock();nvml.restore_offsets.side_effect=RuntimeError('readback mismatch')
        with patch.object(s.subprocess,'run',return_value=Mock(returncode=0,stdout='',stderr='')),patch.object(s.hw,'telemetry',return_value={'A':{'power_limit_w':200}}):
            result=s.restore(nvml,{'A':{'power_limit_w':200}},{'A':{}})
        self.assertFalse(result['restored']);self.assertEqual(len(result['commands']),3)

    def test_example_offline_cli_starts_no_miner(self):
        root=Path(__file__).resolve().parents[1]
        p=subprocess.run([sys.executable,str(root/'scripts/sweetspot.py'),'--config',str(root/'examples/config.example.json'),'--plan',str(root/'examples/plan.example.json'),'--validate-only'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['mode'],'offline-schema-only')


class LifecycleTests(unittest.TestCase):
    def test_forced_stop_never_passes_as_graceful(self):
        child=Mock();child.poll.return_value=None;child.send_signal.side_effect=OSError('no console');job=Mock()
        with patch.object(s.hw.signal,'CTRL_BREAK_EVENT',1,create=True):
            self.assertFalse(s.hw.stop_owned(child,job))
        job.close.assert_called_once()

    def test_trial_error_still_stops_and_restores(self):
        config=dict(executable='miner.exe',algorithm='algo',pool='pool',wallet='wallet',power_method='sampled-power',devices=[dict(uuid='A',miner_id=0)])
        trial=dict(label='failure',duration_s=10,warmup_s=1,settings=[dict(uuid='A',core_mhz=1000,core_offset_mhz=0,memory_mhz=1000,power_limit_w=100)])
        child=Mock();child.poll.return_value=None;nvml=Mock();nvml.offsets.return_value={}
        with tempfile.TemporaryDirectory() as tmp,patch.object(s.hw,'OwnedJob'),patch.object(s.hw,'ProcessMemory'),patch.object(s.hw,'telemetry',side_effect=RuntimeError('telemetry failed')),patch.object(s.hw,'stop_owned',return_value=True) as stop,patch.object(s,'restore',return_value={'restored':True}) as restore,patch.object(s.subprocess,'Popen',return_value=child),patch.object(s.subprocess,'CREATE_NEW_PROCESS_GROUP',512,create=True):
            result=s.run_trial(config,trial,Path(tmp)/'failure',nvml,{'A':{}})
            self.assertFalse(result['valid']);self.assertIn('telemetry failed',result['outcome']);stop.assert_called_once();restore.assert_called_once()

    def test_seven_windows_remain_incomplete(self):
        epoch=__import__('datetime').datetime(2026,1,1).timestamp()
        config=dict(algorithm='algo',power_method='sampled-power',devices=[dict(uuid='A',miner_id=0)])
        trial=dict(label='coverage',warmup_s=0,rate_window_guard_s=0,duration_s=100,minimum_rate_windows=8,settings=[dict(uuid='A',core_mhz=1000,core_offset_mhz=0,memory_mhz=1000,power_limit_w=100)])
        samples=[dict(elapsed=t,epoch=epoch+t,gpus={'A':dict(watts=50,core_mhz=1000,memory_mhz=1000,power_limit_w=100,pstate=0,temperature_c=50)},offsets={'A':{'0:0':{'value':0}}},memory={'private_commit_bytes':100}) for t in (0,90)]
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);lines=[f'[2026-01-01 00:00:{i:02d}] GPU0 Model: 100 H/s [A:1 R:0 HW:0]' for i in range(7)]
            (folder/'srb.log').write_text('\n'.join(lines)+'\nGPU0 share accepted [algo][0]',encoding='utf-8')
            result=s.summarize(config,trial,folder,samples,'completed',True,True,epoch)
        self.assertFalse(result['valid']);self.assertEqual(result['gpus']['A']['rate_windows'],7)
        self.assertTrue(result['gpus']['A']['controls_verified']);self.assertEqual(result['gpus']['A']['owner_accepted'],1)


if __name__=='__main__':
    unittest.main()
