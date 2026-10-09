# Runbook: Globex Identity Cutover to Acme Okta

| | |
| --- | --- |
| **Scenario** | Acme acquires Globex. Globex workforce identities move from Globex's Auth0 tenant into Acme's Okta org. |
| **Owner** | IAM Engineering (lab: Wes) |
| **Approvers** | Acme IAM lead, Acme HR operations, Globex IT lead, Help desk manager |
| **Status** | Phases 1 and 2 executed in the lab. Phase 3 (password migration and waves) is designed and pending trial license capacity. |

> Lab note: all people, emails and passwords in this lab are fake (`.test` domains). Values in angle brackets, such as `<date>`, are filled in per wave.

---

## 1. Purpose and scope

Move every Globex employee onto a single Acme identity in Okta, with no forced password resets, no loss of access to apps they need, and a full audit trail of every identity decision.

**In scope**

- Globex workforce users in Auth0 (30 in the lab).
- Day-one access to designated Acme apps through federation.
- Identity matching against Acme HR, linking of confirmed duplicates.
- Password migration from Auth0 to Okta using the Okta password import inline hook.
- Decommissioning of the Globex Auth0 tenant.

**Out of scope**

- Customer (CIAM) identities.
- Migrating Globex application entitlements one for one. Globex-era access is re-requested and reviewed, not copied.

## 2. Architecture by phase

| Phase | How Globex users sign in | Source of truth for the person |
| --- | --- | --- |
| **1. Day one (federation)** | Okta routing rule sends `@globex-lab.test` users to Auth0. Okta creates a JIT account in group `globex-guest`. | Globex Auth0 |
| **2. Reconciliation** | Unchanged from Phase 1 | Decisions recorded per person; linked identities carry `globexId` and `secondEmail` |
| **3. Migration** | Migrated users sign in to Okta directly. Okta verifies their old password against Auth0 once, through the password import hook, then stores it. | Acme HR service |
| **4. Decommission** | All users on Okta. Auth0 routing removed. | Acme HR service |

## 3. Roles and contacts

| Role | Responsibility during cutover |
| --- | --- |
| IAM engineer (change lead) | Runs each step, owns go/no-go and rollback calls |
| HR operations | Confirms identity matches in the review bucket, owns worker records |
| Globex IT lead | Confirms Auth0 health, communicates with Globex staff |
| Help desk | Handles user tickets using the script in section 10 |
| Security operations | Watches sign-in anomalies in the Okta System Log |

## 4. Prerequisites (complete 5 business days before each wave)

- [ ] **License capacity confirmed.** Count activated users in Okta and compare with the plan's limit. Leave headroom of at least 10 percent above the wave size. (See lesson 12.1.)
- [ ] **Routing rule** `Globex users to Auth0` active and above the default rule.
- [ ] **Identity provider** `Globex (Auth0)` active, with JIT into `globex-guest`.
- [ ] **Authentication policies** reviewed for `globex-guest`: app sign-on, Okta account management, authenticator enrollment, global session. (See lesson 12.3.)
- [ ] **Matching complete.** `match.py` run, every review case decided in `decisions.csv`, `apply_links.py` run, `link_log.csv` archived.
- [ ] **Password import hook** deployed over HTTPS, health endpoint returns 200, response time under 1 second.
- [ ] **Auth0 password grant** enabled for the verification client only.
- [ ] **Wave list** approved (section 6).
- [ ] **Communications** sent: 5 days and 1 day before the wave (section 10).
- [ ] **Help desk briefed** and the ticket category `Globex migration` created.
- [ ] **Rollback rehearsed** with one test user.

## 5. Identity matching rules (Phase 2)

| Bucket | Rule | Action |
| --- | --- | --- |
| Exact | Same normalized first name, last name and department | Auto-link, approver recorded as `auto: exact rule` |
| Review | Same normalized name, different department or multiple candidates | HR confirms with manager, location or hire date before linking |
| New | No name match | Hired into Acme HR with a `G` employee ID |

**Policies**

- Never merge on name alone without a recorded decision.
- Do not union access. Acme birthright comes from Acme group rules. Globex-era access is re-requested.
- If the matched Acme account is offboarded, treat the person as a **rehire**: HR decides whether to reactivate the original identity.
- Every decision is logged with who approved it and when (`link_log.csv`).

**Lab result:** 30 Globex users, 10 planted duplicates. Matching found 10 of 10 (2 exact, 8 review) and 20 new. Linking applied 3 links; 7 were flagged as rehire cases because their Acme accounts had been offboarded.

## 6. Wave plan

| Wave | Size | Who | Go to next wave when |
| --- | --- | --- | --- |
| Pilot | 2 | One new user, one linked duplicate | Both sign in with their old password, no tickets |
| Wave 1 | 3 to 4 | Mixed departments | Sign-in success rate at least 95 percent, no P1 tickets |
| Wave 2 | Remaining | Everyone else | Same criteria |

Wave sizes in the lab are constrained by the trial's active user limit. In production, size waves by help desk capacity and license headroom.

## 7. Go/no-go checklist (morning of each wave)

| Check | Owner | Go? |
| --- | --- | --- |
| License headroom covers this wave | IAM | |
| Password hook healthy (200, under 1 second) | IAM | |
| Auth0 tenant healthy, no incidents | Globex IT | |
| Okta System Log clear of unexplained failures in the last 24 hours | Security ops | |
| Help desk staffed for the wave window | Help desk | |
| Rollback steps rehearsed | IAM | |

All rows must be **Go**. Any **No-go** postpones the wave.

## 8. Cutover steps (per wave)

| # | Step | Expected time | Verification |
| --- | --- | --- | --- |
| 1 | Freeze: announce the start in the change channel | 2 min | Message posted |
| 2 | For each user in the wave, remove any stranded JIT account that never activated | 5 min | No wave user in `STAGED` state |
| 3 | Create or update each user in Okta with the password hook credential (`credentials.password.hook.type = default`) | 5 to 10 min | API returns 200 per user |
| 4 | Set `migrated = true` on each wave user | 2 min | Attribute visible on profile |
| 5 | Confirm the routing rule for migrated users (Okta sign-in) sits above `Globex users to Auth0` | 2 min | Rule order checked |
| 6 | Pilot sign-in: one wave user signs in with their old Globex password | 5 min | Hook log shows `VERIFIED`; user lands in the Acme Portal |
| 7 | Second sign-in by the same user | 2 min | Hook **not** called; Okta now owns the password |
| 8 | Notify the rest of the wave | 2 min | Email sent |
| 9 | Monitor sign-ins and tickets for 1 hour | 60 min | Success rate tracked in section 9 |

## 9. Verification and tracking

Track every wave in `migration/waves.md`:

| Wave | Date | Users | Signed in | Success rate | Tickets | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Pilot | `<date>` | 2 | | | | |

Evidence to capture per wave: hook log excerpt (usernames and verdicts only, never passwords), Okta System Log export filtered to the wave, screenshot of `globex-guest` membership.

## 10. Rollback

**Trigger:** sign-in success below 90 percent after 1 hour, the password hook failing or timing out, or any P1 incident tied to the wave.

**Steps**

1. Set `migrated = false` for every user in the wave. The `Globex users to Auth0` routing rule applies again, so users return to signing in at Auth0.
2. Leave migrated Okta accounts in place. Their next sign-in goes through Auth0 again.
3. Post the rollback in the change channel and email the wave.
4. Open a post-incident review before rescheduling.

Rollback is safe because Phase 3 never deletes or changes the Auth0 account until decommission.

## 11. Communications

**User email: 5 days before**

> Subject: Your sign-in is moving to Acme on `<date>`
>
> On `<date>`, you will start signing in to Acme apps with Acme's sign-in page. Use your current Globex email and password. You do not need to reset anything. After your first sign-in, your password is managed by Acme.

**Help desk script**

1. Confirm the user's wave and date.
2. If sign-in fails, check the Okta System Log for the user and note the `reason` field.
3. Common reasons: password typo (ask the user to retry), account stuck in `STAGED` (escalate to IAM), MFA enrollment prompt (expected for most users; walk them through Okta Verify).
4. Never ask for or record a password.

## 12. Lessons from the lab (design inputs)

1. **Know how your vendor counts licenses.** The Okta trial capped activated users at 10 and did not release a seat when a user was deactivated or deleted. JIT accounts consume seats at first sign-in, so a day-one federation can hit a license wall. Check capacity and counting rules before cutover.
2. **Failed JIT activations leave stranded accounts.** When activation failed, the half-created account (`PENDING_ACTIVATION`) blocked every later attempt until it was removed. Step 2 of the cutover cleans these up.
3. **An MFA prompt can come from four policies.** App sign-on, Okta account management, authenticator enrollment and global session policies all evaluate at sign-in. "Optional" enrollment is overridden when an app policy requires a factor the user lacks. The System Log's `policy.evaluate_sign_on` events name the exact policy and rule.
4. **Federation works independently of activation.** System Log evidence showed the routing rule, Auth0 federation (`authenticationProvider: FEDERATION`) and JIT creation all succeeding before the license limit blocked activation.
5. **Matching needs a human in the loop.** 8 of 10 real duplicates landed in the review bucket because departments differed. Auto-linking on name alone would have been fast and wrong.

## 13. Decommission (after the final wave)

1. Confirm every Globex user has signed in to Okta at least once, or received a password reset path.
2. Remove the `Globex users to Auth0` routing rule.
3. Move users from `globex-guest` to standard Acme department groups (driven by Acme HR).
4. Disable the Auth0 database connection for the federation client.
5. Keep Auth0 read-only for 30 days; export the user list for records.
6. Delete the Auth0 tenant and revoke the Management API and federation client secrets.
7. Archive `decisions.csv`, `link_log.csv` and `waves.md` with the change record.
