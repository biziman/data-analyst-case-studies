"""Render review figures from case outputs. Requires matplotlib; run from any folder."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

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
# Case 2: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'2-product-experiment-tracking-audit/2-product-experiment-tracking-audit.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
res=ns['results']
groups=['control','test']
assigned=[res[g]['assigned_users'] for g in groups]
payers=[res[g]['payers'] for g in groups]
rates=[p/a for p,a in zip(payers,assigned)]
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10,3.8),gridspec_kw={'width_ratios':[1,1.15]})
x=[0,1];w=.32
ax1.bar([i-w/2 for i in x],[0,0],width=w,color='#dda944',label='Reported by broken event grouping')
ax1.bar([i+w/2 for i in x],payers,width=w,color='#176b8c',label='Payers found by user-level join')
for i,p in enumerate(payers):
    ax1.text(i+w/2,p+10,str(p),ha='center',fontsize=10)
    ax1.text(i-w/2,10,'0',ha='center',fontsize=10)
ax1.set(xticks=x,xticklabels=[f'{g.capitalize()}\n({a:,} exposed)' for g,a in zip(groups,assigned)],
        ylabel='Users',title='Payments attributed per group:\nbroken grouping vs user-level join',ylim=(0,max(payers)*1.3))
ax1.legend(frameon=False,fontsize=9,loc='upper left')
bars=ax2.bar([g.capitalize() for g in groups],rates,color=['#176b8c','#b14632'],width=.5)
for bar,rate,p,a in zip(bars,rates,payers,assigned):
    ax2.text(bar.get_x()+bar.get_width()/2,rate*1.03,f'{rate:.2%}\n({p:,}/{a:,})',ha='center',fontsize=10)
ax2.set(ylim=(0,max(rates)*1.4),ylabel='Payers / assigned users',title='Conversion per assigned user\nafter the user-level join')
ax2.yaxis.set_major_formatter(PercentFormatter(1.0))
fig.text(.02,.02,'Synthetic events generated in the notebook (seed 17); payment probability set to 8% control / 10% test as a simulation input. Not an experiment result.',fontsize=9)
fig.tight_layout(rect=(0,.10,1,1))
out_dir=ROOT/'2-product-experiment-tracking-audit/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'tracking_audit.png',dpi=160);plt.close(fig)
# Case 3: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'3-player-ltv-forecast/3-player-ltv-forecast.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
bands={}
for row in ns['test']:
    band='zero' if row['d7_revenue']==0 else ('low' if row['d7_revenue']<1 else 'high')
    predicted=ns['predicted_mean'].get(ns['segment'](row),ns['global_mean'])
    totals=bands.setdefault(band,[0.0,0.0,0])
    totals[0]+=row['revenue_120'];totals[1]+=predicted;totals[2]+=1
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.1),gridspec_kw={'width_ratios':[1,1.05]})
labels=['Global-average\nbaseline','Segment\nforecast'];maes=[ns['baseline_mae'],ns['forecast_mae']]
bars=ax1.bar(labels,maes,color=['#dda944','#176b8c'],width=.5)
for bar,value in zip(bars,maes):ax1.text(bar.get_x()+bar.get_width()/2,value+.04,f'${value:.2f}',ha='center',fontsize=10)
ax1.set(ylim=(0,max(maes)*1.25),ylabel='Mean absolute error, 120-day revenue (USD)',
        title=f'Forecast error on {len(ns["test"]):,} held-out players:\nsegment forecast is {1-ns["forecast_mae"]/ns["baseline_mae"]:.1%} lower')
names={'zero':'Zero first-week revenue','low':'Low first-week revenue','high':'High first-week revenue'}
y=range(len(bands))
for i,band in enumerate(['high','low','zero']):
    actual,predicted,n=bands[band]
    ax2.plot([actual/n,predicted/n],[i,i],color='#999999',linewidth=1.5,zorder=1)
    ax2.scatter([actual/n],[i],color='#176b8c',marker='D',s=55,zorder=2,label='Observed' if i==0 else None)
    ax2.scatter([predicted/n],[i],color='#b14632',marker='o',s=55,zorder=2,label='Forecast' if i==0 else None)
ax2.set(yticks=list(y),yticklabels=[f'{names[b]}\n(n={bands[b][2]:,})' for b in ['high','low','zero']],xscale='log',
        xlabel='Mean 120-day revenue per player (USD, log scale)',
        title='Predicted versus observed mean revenue,\nby first-week revenue band')
ax2.legend(frameon=False,fontsize=9,loc='lower right')
ax2.invert_yaxis()
fig.text(.02,.02,f'Synthetic players (seed 2026); {len(ns["train"]):,} train / {len(ns["test"]):,} test split by player ID. Band means are dominated by rare large payers.\nSimulation result only, not assessment data or a marketing outcome.',fontsize=9)
fig.tight_layout(rect=(0,.12,1,1))
out_dir=ROOT/'3-player-ltv-forecast/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'forecast_benchmark.png',dpi=160);plt.close(fig)
# Case 4: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'4-gameplay-change-evaluation/4-gameplay-change-evaluation.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
est,lo,hi=ns['did']('damage')
change_a=ns['mean'](ns['player_change']('A','damage'));change_b=ns['mean'](ns['player_change']('B','damage'))
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10,4.0),gridspec_kw={'width_ratios':[1.15,1]})
ax1.errorbar(est,0,xerr=[[est-lo],[hi-est]],fmt='o',color='#176b8c',capsize=6,markersize=8)
ax1.axvline(0,color='#555555',linestyle='--',label='No change: 0')
ax1.axvline(25,color='#b14632',linestyle=':',label='Planted effect in generator: +25')
ax1.set(xlim=(lo-6,31),ylim=(-.6,.6),yticks=[],xlabel='Damage points per battle',
        title='Damage difference-in-differences\n(post − pre, Group A − Group B)')
ax1.text(est,.16,f'{est:.1f} (95% interval {lo:.1f} to {hi:.1f})',ha='center')
ax1.legend(loc='lower right',frameon=False,fontsize=9)
bars=ax2.bar(['Group A','Group B'],[change_a,change_b],color=['#176b8c','#b14632'],width=.5)
for bar,value in zip(bars,[change_a,change_b]):
    ax2.text(bar.get_x()+bar.get_width()/2,value+(1 if value>=0 else -2.6),f'{value:+.1f}',ha='center',fontsize=10)
ax2.axhline(0,color='#555555',linewidth=.8)
ax2.set(ylim=(min(change_a,change_b)*1.45,max(change_a,change_b)*2.2),ylabel='Change in mean damage (points)',
        title=f'Pre-to-post change in mean damage, by group\n(DiD = A − B = {est:.1f})')
fig.text(.02,.02,'Synthetic battle records (seed 420); 800 players, 8 battles per player per period;\nplayer-level bootstrap (1,000 resamples, fixed seed). Simulation only, not assessment findings.',fontsize=9)
fig.tight_layout(rect=(0,.12,1,1))
out_dir=ROOT/'4-gameplay-change-evaluation/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'did_damage.png',dpi=160);plt.close(fig)
# Case 5: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'5-donation-checkout-ab-test/5-donation-checkout-ab-test.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(8,3.4),gridspec_kw={'width_ratios':[1,1.2]})
groups=['control','variant'];conv=[100*sum(v>0 for v in ns['outcomes'][g])/len(ns['outcomes'][g]) for g in groups]
bars=ax1.bar(['Control','Variant'],conv,color=['#176b8c','#dda944'],width=.55)
for bar,value in zip(bars,conv):ax1.text(bar.get_x()+bar.get_width()/2,value+.15,f'{value:.2f}%',ha='center')
ax1.set(ylim=(0,max(conv)*1.25),title='Conversion improves significantly')
ax1.set_ylabel('Donation conversion (% of visitors)',fontsize=9)
ax1.text(.5,-.30,f"+{100*(ns['p_v']-ns['p_c']):.2f} pp (two-proportion z-test p={ns['p_value_conversion']:.4f})",transform=ax1.transAxes,ha='center',fontsize=9)
est=ns['rpv_difference'];lo=ns['low'];hi=ns['high']
ax2.errorbar(est,0,xerr=[[est-lo],[hi-est]],fmt='o',color='#b14632',capsize=6,markersize=8)
ax2.axvline(0,color='#555555',linestyle='--',label='No revenue change: 0')
ax2.set(xlim=(lo-.4,hi+.4),ylim=(-.6,.6),yticks=[],xlabel='Revenue per randomized visitor (USD)',title='Revenue-per-visitor interval includes zero')
usd=lambda v:('\u2212' if v<0 else '')+'$'+f'{abs(v):.2f}'
ax2.text(est,.18,f'{usd(est)} (95% interval {usd(lo)} to {usd(hi)})',ha='center')
ax2.legend(loc='lower right',frameon=False)
fig.text(.02,.02,'Synthetic experiment, 6,000 visitors per arm; visitors resampled 1,000 times. Simulation result only, not a client outcome.',fontsize=9)
fig.tight_layout(rect=(0,.10,1,1))
out_dir=ROOT/'5-donation-checkout-ab-test/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'revenue_per_visitor.png',dpi=160);plt.close(fig)
# Case 6: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'6-funnel-channel-attribution/6-funnel-channel-attribution.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
channels=[r[0] for r in ns['channel_summary']];credit=[r[1] for r in ns['channel_summary']]
src=ns['source_revenue'];alloc=ns['attributed_revenue'];paths=len(ns['purchase_checks'])
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9,3.6),gridspec_kw={'width_ratios':[1.35,1]})
bars=ax1.bar(channels,credit,color='#176b8c',width=.55)
for bar,value in zip(bars,credit):ax1.text(bar.get_x()+bar.get_width()/2,value+90,f'${value:,.0f}',ha='center',fontsize=9)
ax1.set(ylim=(0,max(credit)*1.22),ylabel='Credited revenue (USD)',title='Credit spreads evenly across channels')
ax1.text(.5,-.28,'Descriptive rule-based credit — not incremental lift',transform=ax1.transAxes,ha='center',fontsize=9)
bars2=ax2.bar(['Purchase revenue','Allocated credit'],[src,alloc],color=['#176b8c','#dda944'],width=.5)
for bar,value in zip(bars2,[src,alloc]):ax2.text(bar.get_x()+bar.get_width()/2,value+320,f'${value:,.0f}',ha='center',fontsize=9)
ax2.set(ylim=(0,src*1.25),ylabel='USD (all purchases)',title='Credit equals purchase revenue')
ax2.text(.5,-.28,f'Difference ${alloc-src:,.2f}; {paths}/{paths} purchase shares sum to 100%',transform=ax2.transAxes,ha='center',fontsize=9)
fig.text(.02,.02,'Synthetic sessions (seed 601); 400 users, 1,209 sessions, 300 purchases; depth-weighted 30-day lookback rule.\nSimulation only, not a client outcome.',fontsize=9)
fig.tight_layout(rect=(0,.14,1,1))
out_dir=ROOT/'6-funnel-channel-attribution/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'credit_by_channel.png',dpi=160);plt.close(fig)
# Case 7: run the notebook's code cells to keep one source of truth for the simulation.
nb=json.loads((ROOT/'7-cohort-ltv-roll-forward/7-cohort-ltv-roll-forward.ipynb').read_text())
ns={}
for cell in nb['cells']:
    if cell['cell_type']=='code':
        exec(''.join(cell['source']),ns)
statistics=ns['statistics'];curves=ns['curves'];factors=ns['factors']
CAMPAIGNS=ns['CAMPAIGNS'];TIERS=ns['TIERS'];N=ns['N_COHORTS']
days=list(range(ns['MAX_DAY']+1))
seg_style={('prospecting',1):('#176b8c','-'),('prospecting',2):('#176b8c','--'),
           ('retargeting',1):('#b14632','-'),('retargeting',2):('#b14632','--')}
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9,3.8),gridspec_kw={'width_ratios':[1.5,1]})
for campaign in CAMPAIGNS:
    for tier in TIERS:
        seg=(campaign,tier);color,ls=seg_style[seg]
        for cohort in range(N):
            ax1.plot(days,curves[(cohort,campaign,tier)],color=color,linestyle=ls,alpha=.12,linewidth=.8)
        med=[statistics.median([curves[(c,campaign,tier)][d] for c in range(N)]) for d in days]
        ax1.plot(days,med,color=color,linestyle=ls,linewidth=2,label=f'{campaign} \u00b7 tier {tier} ({factors[seg]:.2f}\u00d7)')
        ax1.plot(30,med[30],'o',color=color,markersize=5)
ax1.set(xlim=(0,360),xlabel='Cohort age (days)',ylabel='Cumulative IAP revenue (USD)',title='Curve factors differ by segment')
ax1.legend(frameon=False,fontsize=8,loc='lower right')
ax1.text(.02,.97,'Dots: D30 read point; curves end at the D360 target.\nMaturity status: cohorts 24\u201329 held out, D360 hidden\nat forecast time. Calendar-valid label maturity is not\nenforced \u2014 the simulation has no cohort dates.',transform=ax1.transAxes,va='top',fontsize=8,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
w_seg=100*ns['wape']('segment_forecast_d360');w_glob=100*ns['wape']('global_forecast_d360')
bars=ax2.bar(['Segment factors','One global factor'],[w_seg,w_glob],color=['#176b8c','#b14632'],width=.55)
for bar,value in zip(bars,[w_seg,w_glob]):ax2.text(bar.get_x()+bar.get_width()/2,value+.35,f'{value:.1f}%',ha='center')
ax2.set(ylim=(0,w_glob*1.25),ylabel='WAPE on held-out D360 (%)',title='Segment factors beat\nthe global factor')
ax2.text(.5,-.22,'24 held-out forecasts (6 cohorts \u00d7 4 segments)',transform=ax2.transAxes,ha='center',fontsize=8)
fig.text(.02,.02,'Synthetic cohort curves (seed 41); 30 weekly cohorts \u00d7 4 segments; cohort curves faint, segment medians bold.\nSimulation only, not a client outcome.',fontsize=9)
fig.tight_layout(rect=(0,.12,1,1))
out_dir=ROOT/'7-cohort-ltv-roll-forward/outputs';out_dir.mkdir(exist_ok=True)
fig.savefig(out_dir/'curve_factors.png',dpi=160);plt.close(fig)
