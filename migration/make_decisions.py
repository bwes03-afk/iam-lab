import csv, os

M = os.path.expanduser("~/iam-lab/migration")
rows = []
for bucket, decision, approver in [("exact", "LINK", "auto: exact rule"),
                                   ("review", "PENDING", "")]:
    with open(f"{M}/{bucket}.csv") as f:
        for r in csv.DictReader(f):
            rows.append({"globexId": r["globexId"], "globexEmail": r["globexEmail"],
                         "name": r["name"], "acmeEmployeeId": r["acmeEmployeeId"],
                         "bucket": bucket, "decision": decision,
                         "approvedBy": approver, "note": r["reason"]})

with open(f"{M}/decisions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} decisions ({sum(r['decision']=='PENDING' for r in rows)} pending)")