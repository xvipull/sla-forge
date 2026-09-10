"""Create de-identified static dashboard captures from governed curated data."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/sla-forge-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports/screenshots'; OUT.mkdir(parents=True,exist_ok=True)
data=pd.read_csv(ROOT/'data/curated/ticket_sla_mart.csv'); data['created_at']=pd.to_datetime(data['created_at'])
def save(name): plt.tight_layout(); plt.savefig(OUT/name,dpi=160,bbox_inches='tight'); plt.close()
fig,axs=plt.subplots(1,3,figsize=(12,3.5)); fig.suptitle('SLAForge | Executive SLA overview',color='#1F4E78',weight='bold'); sla=100*(1-data.sla_breached.mean()); axs[0].text(.5,.58,f'{sla:.1f}%',ha='center',va='center',fontsize=26,weight='bold',color='#1F4E78'); axs[0].text(.5,.25,'SLA attainment',ha='center',fontsize=11); axs[0].set_axis_off(); axs[1].bar(['MTTA','MTTR'],[data.mtta_hours.mean(),data.mttr_hours.mean()],color=['#5B9BD5','#70AD47']); axs[1].set_ylabel('Hours'); axs[1].set_title('Response and resolution'); q=data.groupby('initial_queue').sla_breached.mean().sort_values(); axs[2].barh(q.index,100*(1-q.values),color='#5B9BD5'); axs[2].axvline(90,color='#C0504D',ls='--'); axs[2].set_xlim(0,100); axs[2].set_title('Queue SLA attainment'); save('01-executive-sla-overview.png')
fig,ax=plt.subplots(figsize=(9,4)); q=data.groupby('initial_queue').agg(sla=('sla_breached',lambda x:100*(1-x.mean())),transfers=('transfer_count','mean'),tickets=('ticket_id','size')); ax.scatter(q.transfers,q.sla,s=q.tickets*2.5,c=q.sla,cmap='RdYlGn',vmin=70,vmax=95,edgecolor='white',linewidth=.8); [ax.annotate(i,(r.transfers,r.sla),xytext=(5,3),textcoords='offset points') for i,r in q.iterrows()]; ax.axhline(90,color='#C0504D',ls='--'); ax.set(xlabel='Average transfers',ylabel='SLA attainment (%)',title='Queue diagnostics | handoffs versus SLA'); save('02-queue-root-cause.png')
fig,ax=plt.subplots(figsize=(10,4)); high=data[(data.risk_score>=70)|data.sla_breached].sort_values('risk_score',ascending=False).head(10); ax.barh(high.ticket_id.iloc[::-1],high.risk_score.iloc[::-1],color='#ED7D31'); ax.axvline(70,color='#C0504D',ls='--'); ax.set(xlabel='Risk score',title='Breach-risk triage | priority worklist'); save('03-breach-risk-triage.png')
