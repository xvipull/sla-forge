"""Purposeful EDA for SLA distribution, quality, outliers, and operational drivers."""
from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/sla-forge-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT=Path(__file__).resolve().parents[1]; DB=ROOT/'data/sla_forge.db'; FIGURES=ROOT/'reports/figures'; REPORT=ROOT/'reports/eda_summary.json'
def save(name):
    FIGURES.mkdir(parents=True,exist_ok=True); plt.tight_layout(); plt.savefig(FIGURES/name,dpi=160,bbox_inches='tight'); plt.close()
def main():
    if not DB.exists(): raise FileNotFoundError('Run python3 src/pipeline.py before EDA.')
    con=sqlite3.connect(DB); tickets=pd.read_sql_query('SELECT * FROM v_ticket_kpi',con); staging=pd.read_sql_query('SELECT * FROM stg_tickets',con).replace('',np.nan); con.close()
    sns.set_theme(style='whitegrid',palette='deep')
    # 1: Which queues combine low SLA attainment with material workload?
    queue=tickets.groupby('initial_queue',as_index=False).agg(ticket_count=('ticket_id','size'),sla_attainment_pct=('sla_breached',lambda x:100*(1-x.mean()))).sort_values('sla_attainment_pct')
    fig,ax=plt.subplots(figsize=(8,4)); sns.barplot(data=queue,x='sla_attainment_pct',y='initial_queue',hue='ticket_count',palette='Blues',legend=False,ax=ax); ax.axvline(90,color='#c44e52',ls='--',label='90% target'); ax.set(xlabel='SLA attainment (%)',ylabel='Initial queue',title='SLA attainment by queue'); ax.legend(); save('sla_attainment_by_queue.png')
    # 2: Distribution and outliers of resolution time by priority support capacity and policy review.
    fig,ax=plt.subplots(figsize=(8,4)); sns.boxplot(data=tickets,x='priority',y='mttr_hours',order=['P1','P2','P3','P4'],showfliers=False,ax=ax); sns.stripplot(data=tickets,x='priority',y='mttr_hours',order=['P1','P2','P3','P4'],color='#4c4c4c',alpha=.18,size=2,ax=ax); ax.set(xlabel='Priority',ylabel='Resolution / as-of age (hours)',title='Resolution-time distribution by priority'); save('mttr_distribution_by_priority.png')
    # 3: Numeric correlations expose drivers behind the triage score and breach pattern.
    numeric=tickets[['mtta_hours','mttr_hours','transfer_count','reopened','sla_breached','risk_score']].astype(float); fig,ax=plt.subplots(figsize=(7,5)); sns.heatmap(numeric.corr(),annot=True,cmap='vlag',center=0,fmt='.2f',ax=ax); ax.set_title('Operational metric correlations'); save('operational_driver_correlation.png')
    q1,q3=np.quantile(tickets.mttr_hours,[.25,.75]); iqr=q3-q1; outliers=tickets[tickets.mttr_hours>q3+1.5*iqr]
    summary={'ticket_count':int(len(tickets)),'missingness_pct':{column:round(float(value)*100,2) for column,value in staging.isna().mean().items()},'mttr_iqr_outlier_threshold_hours':round(float(q3+1.5*iqr),2),'mttr_outlier_count':int(len(outliers)),'numeric_correlations':numeric.corr().round(3).to_dict(),'top_breach_driver_categories':tickets.groupby('category').sla_breached.mean().sort_values(ascending=False).head(3).round(3).to_dict()}
    REPORT.write_text(json.dumps(summary,indent=2)); print(f'Published {len(tickets)} tickets, 3 figures, and EDA summary.')
if __name__=='__main__': main()
