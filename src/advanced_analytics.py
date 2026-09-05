"""Train an explainable, time-split logistic breach-risk model and persist governed outputs."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; DB=ROOT/'data/sla_forge.db'; REPORT=ROOT/'reports/model_evaluation.json'
MODEL_NAME='explainable_logistic_breach_risk_v1'; THRESHOLD=.50
def sigmoid(values): return 1/(1+np.exp(-np.clip(values,-30,30)))
def auc(y,score):
    ranks=pd.Series(score).rank(method='average').to_numpy(); positives=y.sum(); negatives=len(y)-positives
    return round(float((ranks[y==1].sum()-positives*(positives+1)/2)/(positives*negatives)),4) if positives and negatives else 0.5
def metrics(y,score):
    pred=(score>=THRESHOLD).astype(int); tp=int(((pred==1)&(y==1)).sum()); fp=int(((pred==1)&(y==0)).sum()); fn=int(((pred==0)&(y==1)).sum())
    return {'auc':auc(y,score),'precision':round(tp/(tp+fp),4) if tp+fp else 0.,'recall':round(tp/(tp+fn),4) if tp+fn else 0.,'accuracy':round(float((pred==y).mean()),4)}
def feature_matrix(data,columns=None):
    categorical=pd.get_dummies(data[['priority','category','initial_queue']],dtype=float)
    numeric=data[['transfer_count']].astype(float)/3
    features=pd.concat([categorical,numeric],axis=1)
    if columns is not None: features=features.reindex(columns=columns,fill_value=0.)
    return features
def train_logistic(x,y):
    design=np.column_stack([np.ones(len(x)),x.to_numpy()]); weights=np.zeros(design.shape[1]);
    for _ in range(1800):
        probabilities=sigmoid(design@weights); gradient=(design.T@(probabilities-y))/len(y)+.02*np.r_[0,weights[1:]]; weights-=.18*gradient
    return weights
def baseline(data):
    # Explicit operational policy baseline: urgent work or repeated Infrastructure handoffs.
    return ((data.priority.isin(['P1','P2']))|((data.initial_queue=='Infrastructure')&(data.transfer_count>=2))).astype(float).to_numpy()
def main():
    if not DB.exists(): raise FileNotFoundError('Run the data pipeline before advanced analytics.')
    con=sqlite3.connect(DB); data=pd.read_sql_query('SELECT ticket_key,ticket_id,created_at,priority,category,initial_queue,transfer_count,sla_breached FROM v_ticket_kpi',con); data=data.sort_values(['created_at','ticket_id']).reset_index(drop=True)
    split=max(1,int(len(data)*.8)); data['data_partition']=np.where(np.arange(len(data))<split,'train','test'); train,test=data.iloc[:split],data.iloc[split:]; y_train=train.sla_breached.astype(int).to_numpy(); y_test=test.sla_breached.astype(int).to_numpy()
    train_x=feature_matrix(train); weights=train_logistic(train_x,y_train); all_x=feature_matrix(data,train_x.columns); probabilities=sigmoid(np.column_stack([np.ones(len(data)),all_x.to_numpy()])@weights); baseline_scores=baseline(data)
    model_metrics=metrics(y_test,probabilities[split:]); baseline_metrics=metrics(y_test,baseline_scores[split:]); run_id='brm-20250901-v1'; assumptions='Temporal 80/20 split; priority, category, initial queue and current transfer count only; no elapsed time, response timestamps, resolution timestamps, or reopen state.'
    con.executescript((ROOT/'sql/05_decision_support.sql').read_text()); con.execute('DELETE FROM fact_breach_risk_prediction WHERE model_run_id=?',(run_id,)); con.execute('DELETE FROM model_driver WHERE model_run_id=?',(run_id,)); con.execute('DELETE FROM model_run WHERE model_run_id=?',(run_id,))
    con.execute('INSERT INTO model_run VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(run_id,MODEL_NAME,datetime.now(timezone.utc).isoformat(),len(train),len(test),THRESHOLD,json.dumps(list(train_x.columns)),assumptions,model_metrics['auc'],model_metrics['precision'],model_metrics['recall'],model_metrics['accuracy']))
    drivers=pd.DataFrame({'feature_name':train_x.columns,'coefficient':weights[1:]}); drivers['odds_ratio']=np.exp(drivers.coefficient); drivers['direction']=np.where(drivers.coefficient>=0,'increases breach risk','reduces breach risk'); drivers['driver_rank']=drivers.coefficient.abs().rank(ascending=False,method='first').astype(int)
    con.executemany('INSERT INTO model_driver VALUES(?,?,?,?,?,?)',[(run_id,row.feature_name,float(row.coefficient),float(row.odds_ratio),row.direction,int(row.driver_rank)) for row in drivers.itertuples(index=False)])
    rows=[]
    for row,score,base in zip(data.itertuples(index=False),probabilities,baseline_scores): rows.append((run_id,int(row.ticket_key),row.data_partition,int(row.sla_breached),float(score),'High' if score>=THRESHOLD else 'Standard',float(base),'High' if base>=THRESHOLD else 'Standard'))
    con.executemany('INSERT INTO fact_breach_risk_prediction VALUES(?,?,?,?,?,?,?,?)',rows); con.commit(); con.close()
    REPORT.write_text(json.dumps({'model_run_id':run_id,'model_name':MODEL_NAME,'split':{'train':len(train),'test':len(test),'method':'chronological 80/20'},'threshold':THRESHOLD,'features':list(train_x.columns),'model_test_metrics':model_metrics,'rule_baseline_test_metrics':baseline_metrics,'top_drivers':drivers.sort_values('driver_rank').head(8).round(4).to_dict(orient='records'),'limitations':['Synthetic data only; do not infer production accuracy.','The outcome is historical SLA breach, not a causal result.','Transfer count may evolve during ticket lifetime; refresh predictions as ownership changes.','Use for ticket prioritization, not employee-performance decisions.']},indent=2)); print(f'Published {MODEL_NAME}: test AUC {model_metrics["auc"]} vs baseline {baseline_metrics["auc"]}.')
if __name__=='__main__': main()
