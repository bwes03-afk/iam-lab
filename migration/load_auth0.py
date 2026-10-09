import csv, os, time, requests

D = os.environ["AUTH0_DOMAIN"]

# Get a Management API token for this script
tok = requests.post(f"https://{D}/oauth/token", json={
    "grant_type": "client_credentials",
    "client_id": os.environ["AUTH0_MGMT_ID"],
    "client_secret": os.environ["AUTH0_MGMT_SECRET"],
    "audience": f"https://{D}/api/v2/",
}).json()["access_token"]
H = {"Authorization": f"Bearer {tok}"}

created, skipped, failed = 0, 0, 0
with open(os.path.expanduser("~/iam-lab/scripts/globex_users.csv")) as f:
    for row in csv.DictReader(f):
        r = requests.post(f"https://{D}/api/v2/users", headers=H, json={
            "connection": "Username-Password-Authentication",
            "email": row["email"],
            "password": row["password"],
            "given_name": row["firstName"],
            "family_name": row["lastName"],
            "name": f'{row["firstName"]} {row["lastName"]}',
            "email_verified": True,
            "app_metadata": {"globexId": row["globexId"], "department": row["department"]},
        })
        if r.status_code == 201:
            created += 1
        elif r.status_code == 409:
            skipped += 1  # already exists from an earlier run
        else:
            failed += 1
            print("FAILED", row["email"], r.status_code, r.text[:200])
        time.sleep(0.3)  # stay under Auth0's rate limits

print(f"created: {created}, already existed: {skipped}, failed: {failed}")