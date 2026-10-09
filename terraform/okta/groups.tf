# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "00g18jw801hfW5d2u698"
resource "okta_group" "globex_guests" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "globex-guests"
}

# __generated__ by Terraform from "00g18cnttjbMIHegD698"
resource "okta_group" "dept_finance" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "dept-finance"
}

# __generated__ by Terraform from "0pr18cozraeggTkYx698"
resource "okta_group_rule" "finance_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"Finance\" and user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.dept_finance.id]
  name                  = "Finance birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "00g18cnsomefBMm0t698"
resource "okta_group" "dept_sales" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "dept-sales"
}

# __generated__ by Terraform from "00g18fjigvqXMcowP698"
resource "okta_group" "lab_test_users" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "lab-test-users"
}

# __generated__ by Terraform from "00g18cnrm2f6fOLZe698"
resource "okta_group" "dept_engineering" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "dept-engineering"
}

# __generated__ by Terraform from "0pr18cp0njm1mUocT698"
resource "okta_group_rule" "support_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"Support\" and user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.dept_support.id]
  name                  = "Support birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "0pr18cp0wnqNtEy1J698"
resource "okta_group_rule" "sales_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"Sales\""
  group_assignments     = [okta_group.dept_sales.id]
  name                  = "Sales birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "0pr18cnqq7xdFrVOv698"
resource "okta_group_rule" "all_active_employees_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.birthright_all.id]
  name                  = "All active employees birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "0pr18cp1ynjgq35aF698"
resource "okta_group_rule" "remote_us_location" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"Remote-US\" and user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.loc_remote_us.id]
  name                  = "Remote US location"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "00g18cnurgnldRbvt698"
resource "okta_group" "loc_remote_us" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "loc-remote-us"
}

# __generated__ by Terraform from "00g18cnq0ovWmpDo1698"
resource "okta_group" "dept_support" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "dept-support"
}

# __generated__ by Terraform from "00g18cnt2m67iAfjL698"
resource "okta_group" "dept_hr" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "dept-hr"
}

# __generated__ by Terraform from "00g18cns325itAblN698"
resource "okta_group" "birthright_all" {
  custom_profile_attributes = jsonencode({})
  description               = null
  name                      = "birthright-all"
}

# __generated__ by Terraform from "0pr18cp1nn9ln0Wwt698"
resource "okta_group_rule" "hr_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"HR\" and user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.dept_hr.id]
  name                  = "HR birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}

# __generated__ by Terraform from "0pr18cnqq1hHGUv0f698"
resource "okta_group_rule" "engineering_birthright" {
  expression_type       = "urn:okta:expression:1.0"
  expression_value      = "user.department==\"Engineering\" and user.employmentStatus==\"ACTIVE\""
  group_assignments     = [okta_group.dept_engineering.id]
  name                  = "Engineering birthright"
  remove_assigned_users = null
  status                = "ACTIVE"
  users_excluded        = null
}
