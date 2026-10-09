# Design: HR-Driven Joiner and Leaver Lifecycle

| | |
| --- | --- |
| **Status** | Implemented in the lab |
| **Components** | HR service (Java, Spring Boot), Okta Users API, Okta Workflows, Okta group rules, SCIM app |
| **Author** | Wes (Brian Dunn) |

## Problem

When accounts are created and removed by hand, new hires wait for access, movers keep access from old roles, and leavers keep working credentials after their last day. The identity provider ends up as a second, drifting copy of HR data, and nobody can say with certainty who should have access to what.

## Goals and non-goals

**Goals**

- HR is the single source of truth for who works here, where, and in what role.
- No administrator creates, changes or removes workforce accounts by hand.
- New hires have birthright access on their start date, not before.
- Termination removes access everywhere downstream automatically, with sessions cleared immediately.
- Every lifecycle action is observable and debuggable after the fact.

**Non-goals**

- Request-based access (approvals for non-birthright apps).
- Replacing a real HCM connector. The lab's HR service stands in for Workday or similar.

## Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| **A. HR pushes changes to the Okta Users API** | Simple, near real time, HR owns timing | HR system must handle Okta errors and rate limits |
| B. Okta Workflows polls HR on a schedule | No HR-side code | Polling delay, more Workflows executions to pay for and debug |
| C. Native HCM connector (Workday to Okta) | Production standard, supported | Requires licensing not available in the lab |

## Decision

**Option A**, with a clear split of responsibility: **HR decides when, Okta decides how.** The HR service owns the start date and employment status; Okta Workflows owns the activation and termination logic; Okta group rules own birthright access. Option C is how this maps to production: the same attributes and rules would be fed by the native connector instead of the HR service.

## How it works

### Joiner

1. HR hires a worker. The HR service creates the Okta user **Staged**, with `employeeNumber`, `department`, `workLocation` and `employmentStatus = PENDING`. Nothing works before day one.
2. A scheduled job in the HR service marks workers `ACTIVE` once their start date arrives and pushes the profile change to Okta.
3. The **Joiner** workflow fires on *User Okta Profile Updated*, reads the **target** user, and continues only if `employmentStatus` is `ACTIVE` **and** the account is still `STAGED`. It then activates the account without sending email.
4. **Group rules** grant birthright access from profile attributes:
    - `dept-*` groups: `user.department == "<Dept>" and user.employmentStatus == "ACTIVE"`
    - `loc-remote-us`: location plus active status
    - `birthright-all`: active status only
5. Apps assigned to those groups, including the SCIM app, provision the user automatically.

### Mover

Department changes in HR update the profile; the rules re-evaluate and swap department groups automatically. A manual-access review flow for movers was designed but deferred.

### Leaver

1. HR terminates the worker; the profile changes to `employmentStatus = TERMINATED`.
2. **Status-gated rules remove birthright groups immediately**, which unassigns apps; the SCIM app receives `active: false`.
3. The **Leaver** workflow:
    - suspends the account if it is `ACTIVE` (users who never activated skip this branch),
    - clears sessions and OAuth tokens,
    - waits a hold period (5 minutes in the lab, 7 days in production, so HR can reverse a mistaken termination),
    - deactivates the account.

### Supporting scripts

- **Reconciliation** compares HR with Okta and repairs drift after partial failures.
- **Backfill** activates existing users when automation first goes live, since event-driven flows only react to new changes.

## Verified results

- New hire: Staged, then Active on start date, then in `dept-*`, `loc-*` and `birthright-all`, with no console clicks.
- Termination: groups removed, SCIM account set inactive, sessions cleared, account deactivated after the hold period.

## Lessons learned

1. **Actor versus target.** Workflows event cards expose both the actor (who made the change) and the user who was changed. The first build mapped the actor, so the flow read the admin account behind the HR service's API token. Saved execution data showed the wrong user ID immediately.
2. **Gate access on employment status, not just department.** Without the status condition, a terminated Sales rep stays in `dept-sales` until deactivation. With it, access ends the moment HR says so, and the Leaver flow no longer needs group-removal steps.
3. **A 403 is not always a permission problem.** An activation that failed with HTTP 403 turned out to be the trial's active-user cap (`user_activation_failure_due_to_limit`). Read the error body, not just the status code.
4. **Know how the platform counts licenses.** The trial capped activated users at 10 and did not release a seat on deactivation or deletion. The dataset and test plan were sized around that.
5. **Deactivated users reject updates.** After deactivation, Okta returns `E0000038` for profile changes, so the HR service must skip or log updates for terminated workers rather than fail.
6. **Provisioned users cannot be suspended.** Users who never set a password are `PROVISIONED`; the Leaver flow branches so they go straight to cleanup.

## Risks and what changes at production scale

| Risk | Production approach |
| --- | --- |
| Okta API rate limits during bulk HR changes | Queue and throttle pushes; retry with backoff on 429 |
| Missed or duplicated events | Idempotent flows (the Joiner checks current status first); scheduled reconciliation as a safety net |
| Rehires | Reactivate the existing identity after HR confirmation instead of creating a second account |
| Mistaken terminations | Hold period before deactivation; documented reversal procedure |
| Admin API token as a single powerful secret | Scoped OAuth service app with least-privilege scopes, rotated, stored in a secrets manager |
| Audit questions | System Log retention plus an HR-side change log keyed by employee ID |
