import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}", "Accept": "application/json"}

users = requests.get(f"{ORG}/api/v1/users",
    params={"search": 'profile.employeeNumber sw "A"', "limit": 200}, headers=H).json()
print(f"deleting {len(users)} seed users")
for u in users:
    url = f"{ORG}/api/v1/users/{u['id']}"
    requests.delete(url, headers=H)   # 1st call: deactivate
    time.sleep(0.3)
    requests.delete(url, headers=H)   # 2nd call: delete
    print("deleted", u["profile"]["login"])
    time.sleep(0.3)