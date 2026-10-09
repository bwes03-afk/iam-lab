# Design: Okta as Code with Pull Request Review

| | |
| --- | --- |
| **Status** | Implemented in the lab |
| **Components** | Terraform (Okta provider 7.x), Amazon S3, GitHub Actions, GitHub OIDC, AWS IAM |
| **Author** | Wes (Brian Dunn) |

## Problem

Okta groups and group rules decide who gets access to what. When they are changed by clicking in the admin console, there is no preview of the effect, no second reviewer, and no reliable history of who changed access and why. Rebuilding the configuration in another org depends on memory and screenshots.

## Goals and non-goals

**Goals**

- Every access-defining object (groups, birthright rules) lives in version-controlled code.
- Every change is previewed before it happens and reviewed by someone else.
- The pipeline that previews changes holds no long-lived cloud credentials.
- The configuration can be rebuilt in a new Okta org from code.

**Non-goals (for now)**

- Okta Workflows flows, which the Terraform provider does not manage (they can be exported as flow packs).
- Fully automatic apply on merge.

## Options considered

| Decision | Options | Choice and reason |
| --- | --- | --- |
| How to manage config | Console plus documentation; custom API scripts; **Terraform** | Terraform: declarative, shows a plan before changing anything, widely used for Okta |
| Where state lives | Laptop; Terraform Cloud; **private S3 bucket** | S3: shared with CI, versioned for recovery, lockable, effectively free |
| How CI reaches AWS | Static access keys in GitHub secrets; **GitHub OIDC federation** | OIDC: short-lived credentials, nothing to leak or rotate |

## How it works

### Bringing existing config under code

1. An `imports.tf` file, generated from the Okta API, listed 16 existing objects (9 groups, 7 rules).
2. `terraform plan -generate-config-out` wrote matching code for all of them.
3. `terraform apply` imported them; a follow-up plan reported **No changes**, proving code and Okta matched.
4. Raw group IDs in rules were replaced with references (`[okta_group.dept_engineering.id]`), so rules read like the design and survive recreation in a new org.

### State

- Stored at `s3://iam-lab-tfstate-<account>/okta/terraform.tfstate`.
- Bucket versioning on, all public access blocked.
- `use_lockfile = true`, so two runs cannot change Okta at the same time.
- State is never committed to Git; the provider lock file is.

### Change flow

1. A change is made on a branch (example: a description update for `dept-marketing`).
2. A pull request triggers the **terraform-okta-plan** workflow:
    - GitHub issues an OIDC token for the job.
    - AWS exchanges it for short-lived credentials on role `github-terraform-okta`.
    - The job runs `terraform fmt -check`, `init`, `validate` and `plan`, and posts the plan to the run summary.
3. A reviewer reads the plan (`0 to add, 1 to change, 0 to destroy`), merges with a written approval note, and the change is applied from `main`.

### Least privilege

- **Trust policy:** only GitHub's OIDC provider, audience `sts.amazonaws.com`, and exact subjects for this repo's pull requests and `main` branch.
- **Permissions:** read and write only the `okta/` prefix of the state bucket. Nothing else in AWS.
- Secrets are never given to pull requests from forks.

## Lessons learned

1. **Federation debugged from the audit log.** The first CI run failed with `AccessDenied` on `AssumeRoleWithWebIdentity` even though the trust policy looked correct. CloudTrail showed GitHub presenting an ID-based subject, `repo:bwes03-afk@<owner-id>/iam-lab@<repo-id>:pull_request`, instead of the name-based one the policy expected. The policy now matches the immutable IDs, which also blocks repository rename and re-registration attacks.
2. **Only apply what is merged.** An apply from an unmerged `main` correctly found nothing to do. Applying from `main` after the merge is what keeps the reviewed code and Okta in step.
3. **Import before you write.** Generating code from the live org avoided hand-typing errors and proved parity with a clean plan before any change.
4. **Empty is not broken.** The new Marketing rule had no members because no worker had that department. Rule membership follows HR attributes, so a test hire is the right way to verify it.

## Accepted risks

| Risk | Why accepted in the lab | Production fix |
| --- | --- | --- |
| CI uses a full-admin Okta API token | A separate read-only admin user would consume one of the trial's 10 seats | Read-only admin for plan; OAuth service app with scoped, short-lived tokens |
| Apply is manual from a laptop | Keeps a human decision on every access change while learning | Apply job on `main` with a separate write role and a protected environment requiring approval |
| Changes made in the console bypass review | Workflows and some settings are still console-managed | Scheduled plan to detect drift; restrict console admin rights |

## Next steps

- Bring app assignments and authentication policies into Terraform.
- Add a nightly plan job that alerts on drift.
- Move the workflow's actions to their newest major versions.
