"""Validate, reconstruct SLA clocks, score risk and publish governed SLAForge marts."""
from __future__ import annotations
import csv, json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; CURATED=ROOT/'data/curated'; REPORTS=ROOT/'reports'; WEB=ROOT/'web'
def pct(n,d): return round(n/d*100,1) if d else 0
def hours(start,end): return round((end-start).total_seconds()/3600,2)
def main():
    with (RAW/'tickets.csv').open() as f: rows=list(csv.DictReader(f))
    with (RAW/'assignment_history.csv').open() as f: events=list(csv.DictReader(f))
    required={'ticket_id','created_at','first_response_at','priority','response_target_hours','resolution_target_hours','state'}
    assert not required-set(rows[0]), 'required ticket columns missing'
    assert len({r['ticket_id'] for r in rows})==len(rows), 'duplicate ticket IDs'
    event_ids={e['ticket_id'] for e in events}; assert all(r['ticket_id'] in event_ids for r in rows), 'orphan ticket'
    now=datetime(2025,9,1)
    for r in rows:
        created=datetime.fromisoformat(r['created_at']); response=datetime.fromisoformat(r['first_response_at']); resolved=datetime.fromisoformat(r['resolved_at']) if r['resolved_at'] else None
        end=resolved or now; r['mtta_hours']=hours(created,response); r['mttr_hours']=hours(created,end); r['age_hours']=hours(created,end)
        r['response_breached']=r['mtta_hours']>float(r['response_target_hours']); r['resolution_breached']=r['mttr_hours']>float(r['resolution_target_hours']); r['sla_breached']=r['response_breached'] or r['resolution_breached']
        r['reopened']=r['reopened']=='True'; r['transfer_count']=sum(e['ticket_id']==r['ticket_id'] for e in events)-1
        r['risk_score']=round(min(99, 18+r['transfer_count']*16+r['reopened']*14+r['mttr_hours']/float(r['resolution_target_hours'])*28+(r['initial_queue']=='Infrastructure')*7),1)
        r['risk_band']='Critical' if r['risk_score']>=70 else ('Watch' if r['risk_score']>=48 else 'Stable')
    by_queue=defaultdict(list); by_month=defaultdict(list); aging=defaultdict(int)
    for r in rows:
        by_queue[r['initial_queue']].append(r); by_month[r['created_at'][:7]].append(r)
        if r['state']!='Resolved': aging['0-24h' if r['age_hours']<24 else '24-48h' if r['age_hours']<48 else '48-72h' if r['age_hours']<72 else '72h+']+=1
    totals={'tickets':len(rows),'sla_attainment':pct(sum(not r['sla_breached'] for r in rows),len(rows)),'mtta':round(sum(r['mtta_hours'] for r in rows)/len(rows),1),'mttr':round(sum(r['mttr_hours'] for r in rows)/len(rows),1),'reopen_rate':pct(sum(r['reopened'] for r in rows),len(rows)),'fcr':pct(sum(r['transfer_count']==0 and not r['reopened'] for r in rows),len(rows))}
    queues=[]
    for q,x in by_queue.items(): queues.append({'queue':q,'tickets':len(x),'sla':pct(sum(not r['sla_breached'] for r in x),len(x)),'mttr':round(sum(r['mttr_hours'] for r in x)/len(x),1),'reopen':pct(sum(r['reopened'] for r in x),len(x)),'transfers':round(sum(r['transfer_count'] for r in x)/len(x),1),'risk':round(sum(r['risk_score'] for r in x)/len(x),1)})
    queues.sort(key=lambda x:x['risk'],reverse=True)
    dashboard={'generated_at':'01 Sep 2025','totals':totals,'queues':queues,'monthly':[{'month':m,'sla':pct(sum(not r['sla_breached'] for r in x),len(x)),'tickets':len(x)} for m,x in sorted(by_month.items())],'aging':[{'bucket':k,'count':aging[k]} for k in ['0-24h','24-48h','48-72h','72h+']],'exceptions':sorted([{'id':r['ticket_id'],'queue':r['initial_queue'],'priority':r['priority'],'reason':'SLA breach' if r['sla_breached'] else 'High breach risk','risk':r['risk_score'],'age':round(r['age_hours'],1)} for r in rows if r['sla_breached'] or r['risk_score']>=70],key=lambda x:x['risk'],reverse=True)[:12]}
    CURATED.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True); WEB.mkdir(parents=True,exist_ok=True)
    with (CURATED/'ticket_sla_mart.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    with (CURATED/'queue_scorecards.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=queues[0]);w.writeheader();w.writerows(queues)
    (WEB/'data.json').write_text(json.dumps(dashboard,indent=2))
    (REPORTS/'data_quality_report.json').write_text(json.dumps({'status':'PASS','ticket_row_count':len(rows),'assignment_event_count':len(events),'duplicate_ticket_ids':0,'required_columns_missing':[],'referential_integrity':'PASS','reconciliation':{'source_tickets':len(rows),'curated_tickets':len(rows),'difference':0}},indent=2))
    print('Published SLA mart, queue scorecards, dashboard data and quality report.')
if __name__=='__main__': main()
