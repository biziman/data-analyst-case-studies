"""Render review figures from case outputs. Requires matplotlib; run from any folder."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
with (ROOT/'9-ctv-geo-uplift/outputs/primary_results.csv').open() as f:
    r=next(row for row in csv.DictReader(f) if row['metric']=='revenue_usd')
estimate=float(r['incremental_roas']);lo=float(r['incremental_roas_95ci_low']);hi=float(r['incremental_roas_95ci_high'])
fig,ax=plt.subplots(figsize=(8,3.1))
ax.errorbar(estimate,0,xerr=[[estimate-lo],[hi-estimate]],fmt='o',color='#176b8c',capsize=6,markersize=8)
ax.axvline(1,color='#b14632',linestyle='--',label='Case direct-revenue threshold: 1.0')
ax.set(xlim=(0,1.15),ylim=(-.6,.6),yticks=[],xlabel='Incremental app revenue / CTV spend',title='Synthetic CTV lift does not meet the stated payback rule')
ax.text(estimate,.16,f'{estimate:.2f} (95% interval {lo:.2f}–{hi:.2f})',ha='center')
ax.legend(loc='lower right',frameon=False)
fig.text(.02,.02,'Simulated matched-geo test; 20 pairs. Revenue during test only; not profit or lifetime value.',fontsize=9)
fig.tight_layout(rect=(0,.07,1,1));fig.savefig(ROOT/'9-ctv-geo-uplift/outputs/iroas_decision.png',dpi=160);plt.close(fig)
r=json.loads((ROOT/'11-payment-fraud-investigation/outputs/rule_validation.json').read_text())
labels=['Flagged fraud','Flagged non-fraud','Missed fraud'];values=[r[k] for k in ['true_positive','false_positive','false_negative']]
fig,ax=plt.subplots(figsize=(8,3.6))
bars=ax.barh(labels[::-1],values[::-1],color=['#b14632','#dda944','#176b8c'])
for bar,value in zip(bars,values[::-1]):ax.text(value+.7,bar.get_y()+bar.get_height()/2,str(value),va='center')
ax.set(xlim=(0,max(values)*1.2),xlabel='Synthetic payment attempts',title='Review rules find 38 injected fraud attempts and miss 50')
fig.text(.02,.02,f'Post-analysis hidden-label check only. Precision {r["precision"]:.1%}; recall {r["recall"]:.1%}. Not real merchant performance.',fontsize=9)
fig.tight_layout(rect=(0,.07,1,1));fig.savefig(ROOT/'11-payment-fraud-investigation/outputs/rule_validation.png',dpi=160);plt.close(fig)
