from app.core.database import Base
from sqlalchemy.orm import relationship

from app.models.closed_days.closed_days_model import ClosedDays
from app.models.commutes.commutes_model import Commutes
from app.models.users.overtimes_model import Overtimes

# models.py에서 정의된 모델들
from .users.users_model import Users
from .parts.parts_model import Parts
from .parts.user_salary import UserSalary
from .branches.branches_model import Branches

# policies/branchpolicies.py에서 정의된 모델들
from .parts.salary_policies_model import SalaryPolicies
from .branches.work_policies_model import WorkPolicies
from .branches.commute_policies_model import CommutePolicies
from .branches.overtime_policies_model import OverTimePolicies
from .branches.auto_overtime_policies_model import AutoOvertimePolicies
from .branches.holiday_work_policies_model import HolidayWorkPolicies
from .branches.allowance_policies_model import AllowancePolicies
from .salary.salary_bracket_model import SalaryBracket
from .branches.document_policies_model import DocumentPolicies
from .branches.rest_days_model import RestDays
from .users.leave_histories_model import LeaveHistories
from .branches.leave_categories_model import LeaveCategory
from .branches.leave_excluded_parts_model import LeaveExcludedPart

from .branches.auto_annual_leave_grant_model import AutoAnnualLeaveGrant
from .branches.auto_annual_leave_approval_model import AutoAnnualLeaveApproval

# parts
from .parts.hour_wage_template_model import HourWageTemplate

# Users.salary = relationship("UserSalary", back_populates="user")

# 일 대 다 관계
Branches.auto_overtime_policies = relationship("AutoOvertimePolicies", back_populates="branch")
Branches.commute_policies = relationship("CommutePolicies", back_populates="branch")
Branches.document_policies = relationship("DocumentPolicies", back_populates="branch")
Branches.holiday_work_policies = relationship("HolidayWorkPolicies", back_populates="branch")
Branches.leave_categories = relationship("LeaveCategory", back_populates="branch")
Branches.overtime_policies = relationship("OverTimePolicies", back_populates="branch")
Branches.rest_days = relationship("RestDays", back_populates="branch")
Branches.parts = relationship("Parts", back_populates="branch")
Branches.users = relationship("Users", back_populates="branch")
Branches.closed_days = relationship("ClosedDays", back_populates="branch")
Branches.leave_histories = relationship("LeaveHistories", back_populates="branch")
Branches.work_policies = relationship("WorkPolicies", back_populates="branch")
Branches.allowance_policies = relationship("AllowancePolicies", back_populates="branch")
Branches.hour_wage_templates = relationship("HourWageTemplate", back_populates="branch")
Branches.auto_annual_leave_grant = relationship("AutoAnnualLeaveGrant", back_populates="branch", uselist=False)
Branches.auto_annual_leave_approval = relationship("AutoAnnualLeaveApproval", back_populates="branch", uselist=False)

LeaveCategory.leave_histories = relationship("LeaveHistories", back_populates="leave_category")

Parts.salary_policies = relationship("SalaryPolicies", back_populates="part")
Parts.users = relationship("Users", back_populates="part")
Parts.hour_wage_templates = relationship("HourWageTemplate", back_populates="part")
Parts.leave_excluded_parts = relationship("LeaveExcludedPart", back_populates="part")

Users.leave_histories = relationship("LeaveHistories", back_populates="user")
Users.applied_overtimes = relationship("Overtimes", foreign_keys=[Overtimes.applicant_id], back_populates="applicant")
Users.managed_overtimes = relationship("Overtimes", foreign_keys=[Overtimes.manager_id], back_populates="manager")
Users.salaries = relationship("UserSalary", back_populates="user", uselist=False)

Parts.salaries = relationship("UserSalary", back_populates="part")
Branches.salaries = relationship("UserSalary", back_populates="branch")

LeaveCategory.leave_excluded_parts = relationship("LeaveExcludedPart", back_populates="leave_category")

Branches.closed_days = relationship("ClosedDays", back_populates="branch")
Parts.closed_days = relationship("ClosedDays", back_populates="part")

Branches.attendance = relationship("Attendance", back_populates="branch")
Parts.attendance = relationship("Attendance", back_populates="part")
Users.attendance = relationship("Attendance", back_populates="users")
# 다 대 일 관계
LeaveHistories.user = relationship("Users", back_populates="leave_histories")
LeaveHistories.leave_category = relationship("LeaveCategory", back_populates="leave_histories")

Users.branch = relationship("Branches", back_populates="users")
Users.part = relationship("Parts", back_populates="users")
Users.commutes = relationship("Commutes", back_populates="users")

Commutes.users = relationship("Users", back_populates="commutes")

Parts.branch = relationship("Branches", back_populates="parts")

WorkPolicies.branch = relationship("Branches", back_populates="work_policies")
SalaryPolicies.part = relationship("Parts", back_populates="salary_policies")
AllowancePolicies.branch = relationship("Branches", back_populates="allowance_policies")

RestDays.branch = relationship("Branches", back_populates="rest_days")
OverTimePolicies.branch = relationship("Branches", back_populates="overtime_policies")
LeaveCategory.branch = relationship("Branches", back_populates="leave_categories")
HolidayWorkPolicies.branch = relationship("Branches", back_populates="holiday_work_policies")
DocumentPolicies.branch = relationship("Branches", back_populates="document_policies")
CommutePolicies.branch = relationship("Branches", back_populates="commute_policies")
AutoOvertimePolicies.branch = relationship("Branches", back_populates="auto_overtime_policies")
ClosedDays.branch = relationship("Branches", back_populates="closed_days")

Overtimes.applicant = relationship("Users", foreign_keys=[Overtimes.applicant_id], back_populates="applied_overtimes")
Overtimes.manager = relationship("Users", foreign_keys=[Overtimes.manager_id], back_populates="managed_overtimes")

LeaveHistories.branch = relationship("Branches", back_populates="leave_histories")

HourWageTemplate.branch = relationship("Branches", back_populates="hour_wage_templates")
HourWageTemplate.part = relationship("Parts", back_populates="hour_wage_templates")

UserSalary.user = relationship("Users", back_populates="salaries")
UserSalary.part = relationship("Parts", back_populates="salaries")
UserSalary.branch = relationship("Branches", back_populates="salaries")

LeaveExcludedPart.part = relationship("Parts", back_populates="leave_excluded_parts")
LeaveExcludedPart.leave_category = relationship("LeaveCategories", back_populates="leave_excluded_parts")

ClosedDays.branch = relationship("Branches", back_populates="closed_days")
ClosedDays.part = relationship("Parts", back_populates="closed_days")

LeaveExcludedPart.leave_category = relationship("LeaveCategory", back_populates="leave_excluded_parts")

AutoAnnualLeaveGrant.branch = relationship("Branches", back_populates="auto_annual_leave_grant")
AutoAnnualLeaveApproval.branch = relationship("Branches", back_populates="auto_annual_leave_approval")

ClosedDays.branch = relationship("Branches", back_populates="closed_days")
ClosedDays.part = relationship("Parts", back_populates="closed_days")
