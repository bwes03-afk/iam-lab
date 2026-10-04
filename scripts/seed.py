import csv, random
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
DEPTS = ["Engineering", "Sales", "Finance", "HR", "Support"]
LOCS = ["Remote-US", "Los Gatos", "New York"]

acme = []
for i in range(1, 51):
    first, last = fake.first_name(), fake.last_name()
    acme.append({
        "employeeId": f"A{i:05d}",
        "firstName": first, "lastName": last,
        "email": f"{first}.{last}@acme-lab.test".lower(),
        "department": random.choice(DEPTS),
        "title": fake.job(),
        "location": random.choice(LOCS),
        "managerId": "" if i <= 5 else f"A{random.randint(1, 5):05d}",
        "startDate": fake.date_between("-5y", "today").isoformat(),
        "status": "ACTIVE",
    })

globex = []
for i in range(1, 31):
    if i <= 10:  # planted duplicates: same person as an Acme worker
        src = acme[i * 3]
        first, last = src["firstName"], src["lastName"]
    else:
        first, last = fake.first_name(), fake.last_name()
    globex.append({
        "globexId": f"G{i:04d}",
        "firstName": first, "lastName": last,
        "email": f"{first}.{last}@globex-lab.test".lower(),
        "department": random.choice(DEPTS),
        "password": "Globex!" + fake.password(length=10),
    })

for name, rows in [("acme_workers.csv", acme), ("globex_users.csv", globex)]:
    with open(name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
print("done")