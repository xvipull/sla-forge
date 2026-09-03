"""Generate deterministic, privacy-safe service desk ticket and assignment history data."""
from __future__ import annotations
import csv, random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / "data" / "raw"
random.seed(24)
QUEUES = [("Access Management", 0.13), ("Workplace", 0.10), ("Business Apps", 0.18), ("Infrastructure", 0.22), ("Network", 0.17)]
CATEGORIES = [("Access", .30), ("Hardware", .18), ("ERP", .20), ("Network", .17), ("Collaboration", .15)]
PRIORITIES = [("P1", 4, 8), ("P2", 8, 24), ("P3", 16, 48), ("P4", 24, 72)]

def main():
    RAW.mkdir(parents=True, exist_ok=True); tickets=[]; history=[]
    start = datetime(2025, 1, 1, 8)
    for n in range(1, 721):
        priority, response_target, resolution_target = random.choices(PRIORITIES, [5, 20, 45, 30])[0]
        queue, queue_risk = random.choices(QUEUES, [18, 17, 23, 24, 18])[0]
        category, _ = random.choices(CATEGORIES, [30, 18, 20, 17, 15])[0]
        created = start + timedelta(hours=random.randrange(24 * 242), minutes=random.randrange(60))
        transfers = min(random.choices([0,1,2,3], [55,29,12,4])[0], 3)
        reopened = random.random() < (.07 + transfers*.045 + (category == "ERP")*.04)
        responded = created + timedelta(hours=max(.3, random.lognormvariate(.65 + queue_risk*2, .55)))
        resolution_hours = random.lognormvariate(2.35 + queue_risk*1.7 + transfers*.21 + (priority == "P1")*.30, .55)
        if reopened: resolution_hours += random.uniform(6, 25)
        resolved = created + timedelta(hours=resolution_hours)
        state = "Open" if n % 19 == 0 else ("Pending" if n % 23 == 0 else "Resolved")
        if state != "Resolved": resolved = None
        tickets.append({"ticket_id":f"INC-{n:05d}","created_at":created.isoformat(timespec="minutes"),"first_response_at":responded.isoformat(timespec="minutes"),"resolved_at":resolved.isoformat(timespec="minutes") if resolved else "","priority":priority,"category":category,"initial_queue":queue,"response_target_hours":response_target,"resolution_target_hours":resolution_target,"reopened":reopened,"state":state})
        assigned = created
        chain=[queue] + [random.choice([x[0] for x in QUEUES if x[0] != queue]) for _ in range(transfers)]
        for step, assigned_queue in enumerate(chain):
            # A source ownership interval can never end before it begins.  This
            # also keeps generated extracts valid under the pipeline's interval
            # quality control when a synthetic resolution is unusually fast.
            ended = max((resolved or datetime(2025,9,1)), assigned) if step == len(chain)-1 else assigned + timedelta(hours=random.uniform(1, 10))
            history.append({"ticket_id":f"INC-{n:05d}","sequence":step+1,"queue":assigned_queue,"assigned_at":assigned.isoformat(timespec="minutes"),"unassigned_at":ended.isoformat(timespec="minutes")})
            assigned=ended
    for name, rows in [("tickets.csv",tickets),("assignment_history.csv",history)]:
        with (RAW/name).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    print(f"Generated {len(tickets)} tickets and {len(history)} assignment events.")
if __name__ == "__main__": main()
