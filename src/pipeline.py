"""Reproducible raw-to-staging, star-schema, mart, and quality-control pipeline."""
from __future__ import annotations
import csv, json, re, sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; STAGING=ROOT/'data/staging'; CURATED=ROOT/'data/curated'; REPORTS=ROOT/'reports'; WEB=ROOT/'web'; DB=ROOT/'data/sla_forge.db'
AS_OF=datetime(2025,9,1,tzinfo=timezone.utc)
TICKET_FIELDS={'ticket_id','created_at','first_response_at','resolved_at','priority','category','initial_queue','response_target_hours','resolution_target_hours','reopened','state'}; EVENT_FIELDS={'ticket_id','sequence','queue','assigned_at','unassigned_at'}
PRIORITIES={'P1','P2','P3','P4'}; STATES={'OPEN','PENDING','RESOLVED'}
CATEGORIES={'ACCESS':'Access','HARDWARE':'Hardware','ERP':'ERP','NETWORK':'Network','COLLABORATION':'Collaboration'}; QUEUES={'ACCESS MANAGEMENT':'Access Management','WORKPLACE':'Workplace','BUSINESS APPS':'Business Apps','INFRASTRUCTURE':'Infrastructure','NETWORK':'Network'}
class DataQualityError(ValueError): pass
def percent(n,d): return round(n/d*100,1) if d else 0.0
def stamp(value,field):
 try: x=datetime.fromisoformat(value.strip().replace('Z','+00:00'))
 except ValueError as e: raise DataQualityError(f'invalid {field}: {value!r}') from e
 return x.replace(tzinfo=x.tzinfo or timezone.utc).astimezone(timezone.utc)
def read(name):
 with (RAW/name).open(newline='',encoding='utf8') as f: return list(csv.DictReader(f))
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
def require(rows,fields,label):
 if not rows: raise DataQualityError(f'{label} is empty')
 missing=fields-set(rows[0])
 if missing: raise DataQualityError(f'{label} missing required columns: {sorted(missing)}')
def clean_tickets(raw):
 require(raw,TICKET_FIELDS,'tickets'); ids=[r['ticket_id'].strip().upper() for r in raw]
 if len(ids)!=len(set(ids)): raise DataQualityError('duplicate ticket_id')
 output=[]
 for r in raw:
  tid=r['ticket_id'].strip().upper(); priority=r['priority'].strip().upper(); state=r['state'].strip().upper(); category=CATEGORIES.get(r['category'].strip().upper()); queue=QUEUES.get(r['initial_queue'].strip().upper())
  if not re.fullmatch(r'INC-\d{5}',tid) or priority not in PRIORITIES or state not in STATES or not category or not queue: raise DataQualityError(f'invalid key or controlled value: {tid}')
  created,response=stamp(r['created_at'],'created_at'),stamp(r['first_response_at'],'first_response_at'); resolved=stamp(r['resolved_at'],'resolved_at') if r['resolved_at'].strip() else None
  response_target,resolution_target=float(r['response_target_hours']),float(r['resolution_target_hours'])
  if response<created or resolved and resolved<created or response_target<=0 or resolution_target<=0 or state=='RESOLVED' and not resolved: raise DataQualityError(f'invalid time/range: {tid}')
  output.append({'ticket_id':tid,'created_at':created.isoformat(timespec='minutes'),'first_response_at':response.isoformat(timespec='minutes'),'resolved_at':resolved.isoformat(timespec='minutes') if resolved else '', 'priority':priority,'category':category,'initial_queue':queue,'response_target_hours':response_target,'resolution_target_hours':resolution_target,'reopened':r['reopened'].strip().lower() in ('true','1','yes'),'state':state})
 return output
def clean_events(raw,ids):
 require(raw,EVENT_FIELDS,'assignment_history'); seen=set(); output=[]
 for r in raw:
  tid=r['ticket_id'].strip().upper(); seq=int(r['sequence']); queue=QUEUES.get(r['queue'].strip().upper()); assigned=stamp(r['assigned_at'],'assigned_at'); unassigned=stamp(r['unassigned_at'],'unassigned_at') if r['unassigned_at'].strip() else None
  if tid not in ids or seq<1 or (tid,seq) in seen or not queue or unassigned and unassigned<assigned: raise DataQualityError(f'invalid assignment event: {tid}/{seq}')
  seen.add((tid,seq)); output.append({'ticket_id':tid,'sequence':seq,'queue':queue,'assigned_at':assigned.isoformat(timespec='minutes'),'unassigned_at':unassigned.isoformat(timespec='minutes') if unassigned else ''})
 if {r['ticket_id'] for r in output} != ids: raise DataQualityError('assignment referential integrity/coverage failed')
 return output
def create_db(tickets,events,mart):
 DB.unlink(missing_ok=True); con=sqlite3.connect(DB); con.execute('PRAGMA foreign_keys=ON'); con.executescript((ROOT/'sql/02_star_schema.sql').read_text())
 con.executemany('INSERT INTO stg_tickets VALUES (:ticket_id,:created_at,:first_response_at,:resolved_at,:priority,:category,:initial_queue,:response_target_hours,:resolution_target_hours,:reopened,:state)',tickets); con.executemany('INSERT INTO stg_assignment_history VALUES (:ticket_id,:sequence,:queue,:assigned_at,:unassigned_at)',events)
 for p in sorted({r['priority'] for r in tickets}): con.execute('INSERT INTO dim_priority(priority_code) VALUES(?)',(p,))
 for c in sorted({r['category'] for r in tickets}): con.execute('INSERT INTO dim_category(category_name) VALUES(?)',(c,))
 for q in sorted({r['initial_queue'] for r in tickets}|{r['queue'] for r in events}): con.execute('INSERT INTO dim_queue(queue_name) VALUES(?)',(q,))
 for d in sorted({r['created_at'][:10] for r in tickets}|{r['resolved_at'][:10] for r in tickets if r['resolved_at']}):
  x=datetime.fromisoformat(d); con.execute('INSERT INTO dim_date VALUES(?,?,?,?,?)',(int(x.strftime('%Y%m%d')),d,x.year,x.month,x.strftime('%Y-%m')))
 keys={table:{name:key for key,name in con.execute(f'SELECT {table}_key,{table}_name FROM dim_{table}')} for table in ('category','queue')}; priorities={name:key for key,name in con.execute('SELECT priority_key,priority_code FROM dim_priority')}; ticket_keys={}
 for r in mart:
  cursor=con.execute('INSERT INTO fact_ticket_sla(ticket_id,created_date_key,resolved_date_key,priority_key,category_key,initial_queue_key,created_at,first_response_at,resolved_at,response_target_hours,resolution_target_hours,reopened,state,mtta_hours,mttr_hours,age_hours,response_breached,resolution_breached,sla_breached,transfer_count,risk_score,risk_band) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(r['ticket_id'],int(r['created_at'][:10].replace('-','')),int(r['resolved_at'][:10].replace('-','')) if r['resolved_at'] else None,priorities[r['priority']],keys['category'][r['category']],keys['queue'][r['initial_queue']],r['created_at'],r['first_response_at'],r['resolved_at'] or None,r['response_target_hours'],r['resolution_target_hours'],int(r['reopened']),r['state'],r['mtta_hours'],r['mttr_hours'],r['age_hours'],int(r['response_breached']),int(r['resolution_breached']),int(r['sla_breached']),r['transfer_count'],r['risk_score'],r['risk_band']))
  ticket_keys[r['ticket_id']]=cursor.lastrowid
 con.executemany('INSERT INTO fact_assignment(ticket_key,queue_key,event_sequence,assigned_at,unassigned_at) VALUES(?,?,?,?,?)',[(ticket_keys[r['ticket_id']],keys['queue'][r['queue']],r['sequence'],r['assigned_at'],r['unassigned_at'] or None) for r in events]); con.executescript((ROOT/'sql/03_kpi_views.sql').read_text()); con.commit(); counts={t:con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ('stg_tickets','stg_assignment_history','fact_ticket_sla','fact_assignment')}; con.close(); return counts
def build_mart(tickets,events):
 counts=Counter(r['ticket_id'] for r in events); mart=[]
 for source in tickets:
  r=dict(source); created,response=stamp(r['created_at'],'created_at'),stamp(r['first_response_at'],'first_response_at'); end=stamp(r['resolved_at'],'resolved_at') if r['resolved_at'] else AS_OF; mtta=round((response-created).total_seconds()/3600,2); mttr=round((end-created).total_seconds()/3600,2); transfers=counts[r['ticket_id']]-1; rb=mtta>r['response_target_hours']; xb=mttr>r['resolution_target_hours']; risk=round(min(99,18+transfers*16+int(r['reopened'])*14+mttr/r['resolution_target_hours']*28+(r['initial_queue']=='Infrastructure')*7),1)
  r.update(mtta_hours=mtta,mttr_hours=mttr,age_hours=mttr,response_breached=rb,resolution_breached=xb,sla_breached=rb or xb,transfer_count=transfers,risk_score=risk,risk_band='Critical' if risk>=70 else 'Watch' if risk>=48 else 'Stable'); mart.append(r)
 return mart
def report(raw_tickets,raw_events,tickets,events,mart,db_counts):
 max_created=max(stamp(r['created_at'],'created_at') for r in tickets); freshness=round((AS_OF-max_created).total_seconds()/3600,2)
 if freshness>168: raise DataQualityError(f'source stale by {freshness} hours')
 nulls=[]
 for rows,label,limits in ((raw_tickets,'tickets',{'ticket_id':0,'created_at':0,'first_response_at':0,'resolved_at':15}),(raw_events,'assignment_history',{'ticket_id':0,'assigned_at':0})):
  for field,limit in limits.items():
   n=sum(not r[field].strip() for r in rows); rate=round(n/len(rows)*100,2)
   if rate>limit: raise DataQualityError(f'{label}.{field} null rate exceeds threshold')
   nulls.append({'field':f'{label}.{field}','null_count':n,'null_percent':rate,'threshold_percent':limit})
 transfer_ok=sum(r['transfer_count'] for r in mart)==len(events)-len(tickets)
 if not transfer_ok: raise DataQualityError('transfer reconciliation failed')
 return {'status':'PASS','run_as_of':AS_OF.isoformat(),'source':{'tickets':len(raw_tickets),'assignment_events':len(raw_events)},'checks':{'required_columns':'PASS','duplicates':'PASS','invalid_ranges':'PASS','referential_integrity':'PASS','freshness':{'max_created_at':max_created.isoformat(),'age_hours':freshness,'threshold_hours':168,'status':'PASS'},'null_thresholds':nulls},'database_row_counts':db_counts,'reconciliation':{'raw_to_staging_tickets':len(raw_tickets)-len(tickets),'staging_to_fact_tickets':len(tickets)-db_counts['fact_ticket_sla'],'raw_to_staging_events':len(raw_events)-len(events),'staging_to_fact_events':len(events)-db_counts['fact_assignment'],'transfer_value_reconciled':transfer_ok,'total_transfers':sum(r['transfer_count'] for r in mart)}}
def main():
 raw_tickets,raw_events=read('tickets.csv'),read('assignment_history.csv'); tickets=clean_tickets(raw_tickets); events=clean_events(raw_events,{r['ticket_id'] for r in tickets}); mart=build_mart(tickets,events); write(STAGING/'stg_tickets.csv',tickets); write(STAGING/'stg_assignment_history.csv',events); db_counts=create_db(tickets,events,mart); by_queue=defaultdict(list)
 for r in mart: by_queue[r['initial_queue']].append(r)
 scorecards=[{'queue':q,'tickets':len(v),'sla':percent(sum(not x['sla_breached'] for x in v),len(v)),'mttr':round(sum(x['mttr_hours'] for x in v)/len(v),1),'reopen':percent(sum(x['reopened'] for x in v),len(v)),'transfers':round(sum(x['transfer_count'] for x in v)/len(v),1),'risk':round(sum(x['risk_score'] for x in v)/len(v),1)} for q,v in by_queue.items()]; scorecards.sort(key=lambda x:x['risk'],reverse=True); write(CURATED/'ticket_sla_mart.csv',mart); write(CURATED/'queue_scorecards.csv',scorecards)
 totals={'tickets':len(mart),'sla_attainment':percent(sum(not x['sla_breached'] for x in mart),len(mart)),'mtta':round(sum(x['mtta_hours'] for x in mart)/len(mart),1),'mttr':round(sum(x['mttr_hours'] for x in mart)/len(mart),1),'reopen_rate':percent(sum(x['reopened'] for x in mart),len(mart)),'fcr':percent(sum(x['transfer_count']==0 and not x['reopened'] for x in mart),len(mart))}; monthly=defaultdict(list); aging=Counter()
 for row in mart:
  monthly[row['created_at'][:7]].append(row)
  if row['state']!='RESOLVED': aging['0-24h' if row['age_hours']<24 else '24-48h' if row['age_hours']<48 else '48-72h' if row['age_hours']<72 else '72h+']+=1
 dashboard={'generated_at':'01 Sep 2025','totals':totals,'queues':scorecards,'monthly':[{'month':m,'sla':percent(sum(not x['sla_breached'] for x in rows),len(rows)),'tickets':len(rows)} for m,rows in sorted(monthly.items())],'aging':[{'bucket':b,'count':aging[b]} for b in ('0-24h','24-48h','48-72h','72h+')],'exceptions':sorted([{'id':x['ticket_id'],'queue':x['initial_queue'],'priority':x['priority'],'reason':'SLA breach' if x['sla_breached'] else 'High breach risk','risk':x['risk_score'],'age':round(x['age_hours'],1)} for x in mart if x['sla_breached'] or x['risk_score']>=70],key=lambda x:x['risk'],reverse=True)[:12]}; WEB.joinpath('data.json').write_text(json.dumps(dashboard,indent=2)); REPORTS.joinpath('data_quality_report.json').write_text(json.dumps(report(raw_tickets,raw_events,tickets,events,mart,db_counts),indent=2)); print('Published validated staging data, SQLite star schema, marts, and DQ report.')
if __name__=='__main__': main()
