resource "okta_group" "dept_marketing" {
  name        = "dept-marketing"
  description = "Birthright: Marketing department"
}

resource "okta_group_rule" "marketing_birthright" {
  name              = "Marketing birthright"
  status            = "ACTIVE"
  group_assignments = [okta_group.dept_marketing.id]
  expression_type   = "urn:okta:expression:1.0"
  expression_value  = "user.department==\"Marketing\" and user.employmentStatus==\"ACTIVE\""
}