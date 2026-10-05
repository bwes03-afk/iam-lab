import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}", "Accept": "application/json"}
HR = "http://localhost:8080/workers"

# Terminate the last 10 seed workers: A00041 through A00050
for n in range(41, 51):
    emp_id = f"A{n:05d}"
    w = requests.post(f"{HR}/{emp_id}/terminate").json()   # HR: status TERMINATED
    r = requests.post(f"{ORG}/api/v1/users/{w['email']}/lifecycle/deactivate", headers=H)
    print(emp_id, w["email"], "HR terminated, Okta deactivate:", r.status_code)
    time.sleep(0.5)