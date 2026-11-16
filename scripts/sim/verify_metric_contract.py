#!/usr/bin/env python3
"""Fact-proof checks for generated simulator data."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'docs/tools/metric-contract/data/sim.json'
def main():
    original=DATA.read_bytes(); subprocess.run([sys.executable,str(ROOT/'scripts/sim/generate_metric_contract.py')],check=True)
    assert hashlib.sha256(original).digest()==hashlib.sha256(DATA.read_bytes()).digest(), 'generator is not byte deterministic'
    d=json.loads(DATA.read_text()); t=d['truth']; days=d['days']; checks=[]
    def ck(cond,msg): assert cond,msg; checks.append(msg)
    cr=t['control_rate']; tr=t['treatment_rate']; revc=cr*t['control_gift']; revt=tr*t['treatment_gift']
    ck(tr/cr-1>0,'conversion lift positive'); ck(revt/revc-1<0,'revenue per visitor lift negative')
    ck((tr/cr-1)>(revt/revc-1),'denominator changes lift ordering')
    ck(sum(x['treatment_gift'] for x in days)/len(days)<sum(x['control_gift'] for x in days)/len(days),'window/gift ordering')
    ck((tr-cr)>0 and (t['treatment_gift']-t['control_gift'])<0,'maturity sign flip')
    reps=d['replays']; daily=sum(min(r['daily_p'])<.05 for r in reps)/len(reps)
    fixed=sum(r['fixed_p']<.05 for r in reps)/len(reps); seq=sum(r['sequential_p']<.05 for r in reps)/len(reps)
    guards=sum(min(r['guardrail_p'])<.05 for r in reps)/len(reps)
    ck(.18<=daily<=.38,'daily-peek rate in range'); ck(fixed<=.08,'fixed-horizon rate bounded'); ck(seq<=.08,'sequential rate bounded')
    ck(.35<=guards<=.55,'12-null flag rate in range'); ck(any(x['lift']>0 and y['lift']<0 for x in d['holdout'] for y in d['holdout']),'holdout preset flips')
    ck(len(days)==42 and len(reps)==200,'complete replay series')
    print(f'{len(checks)} assertions passed')
if __name__=='__main__':
    try: main()
    except Exception as e: print(f'verification failed: {e}',file=sys.stderr); sys.exit(1)
