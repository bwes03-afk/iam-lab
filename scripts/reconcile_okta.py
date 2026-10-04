import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}",
     "Accept": "application/json", "Content-Type": "application/json"}

workers = requests.get("http://localhost:8080/workers").json()
found, created, failed = 0, 0, 0

for w in workers:
    r = requests.get(f"{ORG}/api/v1/users/{w['email']}", headers=H)
    if r.status_code == 200:
        found += 1
    elif r.status_code == 404:
        profile = {
            "firstName": w["firstName"], "lastName": w["lastName"],
            "email": w["email"], "login": w["email"],
            "employeeNumber": w["employeeId"], "department": w["department"],
            "title": w["title"], "managerId": w["managerId"] or "",
            "workLocation": w["location"], "employmentStatus": w["status"],
        }
        c = requests.post(f"{ORG}/api/v1/users?activate=false",
                          headers=H, json={"profile": profile})
        if c.status_code == 200:
            created += 1
        else:
            failed += 1
            print("FAILED", w["email"], c.status_code, c.text[:200])
    else:
        failed += 1
        print("LOOKUP FAILED", w["email"], r.status_code, r.text[:200])
    time.sleep(0.4)  # stay under rate limits

print(f"already in Okta: {found}, created: {created}, failed: {failed}")