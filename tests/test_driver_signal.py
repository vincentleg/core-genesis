"""Real subprocess signal propagation fixture; no browser or inference evidence."""
import json,os,signal,sys,tempfile,threading,time,unittest
from pathlib import Path
from scripts.test_core import run_bounded

class SignalTests(unittest.TestCase):
    def test_sigterm_forwards_and_retains_child_summary(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);child=out/'fixture.py'
            child.write_text("import signal,time,json\nfrom pathlib import Path\np=Path(__file__).parent\ndef stop(*args):\n (p/'summary.json').write_text(json.dumps({'fixture_only':True,'signal_received':True}))\n raise SystemExit(0)\nsignal.signal(signal.SIGTERM,stop)\n(p/'ready').write_text('fixture')\ntime.sleep(5)\n")
            sent=[]
            def send():
                deadline=time.monotonic()+2
                while time.monotonic()<deadline:
                    if (out/'ready').exists() and getattr(signal.getsignal(signal.SIGTERM),'__name__','')=='stop':
                        sent.append(True);os.kill(os.getpid(),signal.SIGTERM);return
                    time.sleep(0.01)
            thread=threading.Thread(target=send);thread.start()
            result=run_bounded([sys.executable,str(child)],out,10);thread.join(timeout=2)
            self.assertEqual(sent,[True]);self.assertEqual(result,1)
            self.assertTrue(json.loads((out/'summary.json').read_text())['signal_received'])
            self.assertEqual(json.loads((out/'watchdog.json').read_text())['reason'],'Interrupted')
