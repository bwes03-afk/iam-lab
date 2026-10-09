import csv, os, re, unicodedata

LAB = os.path.expanduser("~/iam-lab")

def norm(s):
    """Lowercase, strip accents and anything that isn't a letter."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())

def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))

acme = load(f"{LAB}/scripts/acme_workers.csv")
globex = load(f"{LAB}/scripts/globex_users.csv")

# Index Acme workers by normalized full name (a name can belong to more than one person)
by_name = {}
for a in acme:
    by_name.setdefault((norm(a["firstName"]), norm(a["lastName"])), []).append(a)

buckets = {"exact": [], "review": [], "new": []}
for g in globex:
    candidates = by_name.get((norm(g["firstName"]), norm(g["lastName"])), [])
    same_dept = [a for a in candidates if a["department"] == g["department"]]
    if len(same_dept) == 1:
        bucket, a, reason = "exact", same_dept[0], "name and department match"
    elif candidates:
        bucket, a = "review", candidates[0]
        reason = ("name matches more than one Acme worker" if len(candidates) > 1
                  else f"name matches, department differs ({g['department']} vs {a['department']})")
    else:
        bucket, a, reason = "new", None, "no matching Acme worker"
    buckets[bucket].append({
        "globexId": g["globexId"],
        "globexEmail": g["email"],
        "name": f'{g["firstName"]} {g["lastName"]}',
        "acmeEmployeeId": a["employeeId"] if a else "",
        "acmeEmail": a["email"] if a else "",
        "reason": reason,
    })

# Write one CSV per bucket (no passwords are ever copied out)
fields = ["globexId", "globexEmail", "name", "acmeEmployeeId", "acmeEmail", "reason"]
for name, rows in buckets.items():
    with open(f"{LAB}/migration/{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

print({k: len(v) for k, v in buckets.items()})

# Self-check: did we catch every planted duplicate?
planted = {f"G{i:04d}" for i in range(1, 11)}
found = {r["globexId"] for r in buckets["exact"] + buckets["review"]}
print(f"planted duplicates found: {len(planted & found)} of {len(planted)}")
missed = planted - found
if missed:
    print("missed:", sorted(missed))
extra = found - planted
if extra:
    print("unexpected matches (check these by hand):", sorted(extra))