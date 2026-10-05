import os, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}",
     "Accept": "application/json", "Content-Type": "application/json"}
PASSWORD = os.environ["LAB_TEST_PASSWORD"]

# Pick a few users from your People list; one per department is plenty
TEST_USERS = [
    "test.joiner@acme-lab.test",
    # add 3 or 4 more logins here
]

for login in TEST_USERS:
    r = requests.post(f"{ORG}/api/v1/users/{login}", headers=H,
                      json={"credentials": {"password": {"value": PASSWORD}}})
    print(login, r.status_code, r.json().get("status"))