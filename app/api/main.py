from fastapi import APIRouter

from app.api.routes.auth import auth
from app.api.routes.branches import branches
from app.api.routes.callback.webhook_callback import webhook_callback
from app.api.routes.commutes import commutes
from app.api.routes.labor_management import part_timer
from app.api.routes.leave_category import leave_category
from app.api.routes.leave_histories import leave_histories
from app.api.routes.closed_days import closed_days
from app.api.routes.overtimes import overtimes
from app.api.routes.overtime_manager import overtime_manager
from app.api.routes.parts import parts
from app.api.routes.parts_policy import parts_policy
from app.api.routes.personnel_record_category import personnel_record_category
from app.api.routes.salary_bracket import salary_bracket
from app.api.routes.users import users, user_management
from app.api.routes.users.user_management_contract import user_management_contract
from app.api.routes.users.user_management_document import user_management_document
from app.api.routes.users.user_management_work_contract import user_management_work_contract
from app.api.routes.work_policies import work_policies
from app.api.routes.hour_wage_template import hour_wage_template
from app.api.routes.attendance import attendance
from app.api.routes.commutes_manager import commutes_manager
from app.api.routes.leave_policies import leave_policies
from app.api.routes.menu_management import menu_management
from app.api.routes.minimum_wage_policies import minimum_wage_policies
from app.api.routes.salary_template import salary_template
from app.api.routes.salary_policies import salary_policies
from app.api.routes.modusign import document, template, webhook
from app.api.routes.salary_policies import salary_policies
from app.api.routes.db_monitor.db_connections_monitor import router as monitor_router
from enum import Enum
from app.api.routes.public.public_users import router as public_users_router

class APIPrefix(str, Enum):
    PUBLIC = "/public"
    ADMIN = "/admin"
    EMPLOYEE = "/employee"
    MSO = "/mso"
    # 등등등

class APITags(str, Enum):
    PUBLIC = "Public"
    ADMIN = "Admin"
    EMPLOYEE = "Employee"
    MSO = "MSO"

#메인 라우터
app = APIRouter()

# 공통 라우터
public_router = APIRouter()
public_router.include_router(auth.router, prefix="/auth", tags=["Auth : 로그인/로그아웃"])
public_router.include_router(monitor_router, tags=["Monitoring : DB 모니터링"])
public_router.include_router(webhook_callback.router, prefix="/callback", tags=["Callback"])
public_router.include_router(
    public_users_router,  # 변경된 부분
    prefix="/users",
    tags=["Users/me: 공통 -  FE에서 사용자 정보 가져오는 API"]
)
@public_router.get("/healthcheck", summary="healthcheck", tags=["default: healthcheck"])
def health_check():
    return {"status": "healthy"}


#관리자 라우터 (admin)
admin_router = APIRouter(prefix="/admin")

admin_router.include_router(users.router, prefix="/users", tags=["Users: 사용자 관련 "])
admin_router.include_router(commutes.router, prefix="/commutes", tags=["Commutes: 출/퇴근/근태 기록"])
admin_router.include_router(overtimes.router, prefix="/overtimes", tags=["Overtimes: 초과 근무 생성, 조회, 승인, 반려"])
admin_router.include_router(overtime_manager.router, prefix="/branches", tags=["Overtimes_Manager: 초과 근무 관리 (월간/주간, 지점/파트별)"])
admin_router.include_router(closed_days.router, prefix="/branches", tags=["Closed Days: 휴무일 관련"])

admin_router.include_router(branches.router, prefix="/branches", tags=["Branches: 지점 관련"]) # TODO) 지점 관련 연차 관련 따로 분리하면 좋을듯함
admin_router.include_router(parts.router, prefix="/branches/{branch_id}/parts", tags=["Parts: 부서 관련 CRUD "])
admin_router.include_router(leave_category.router, prefix="/branches/{branch_id}/leave-categories", tags=["Leave_categories: 휴무 카테고리 CRUD"])
admin_router.include_router(leave_histories.router, prefix='/branches', tags=['Leave_Histories: 연차 CRUD, 승인/반려'])
admin_router.include_router(work_policies.router, prefix='/branches/{branch_id}/work-policies', tags=['Work_policies: 근무정책 조회/수정'])
admin_router.include_router(hour_wage_template.router, prefix='/branches/{branch_id}/hour-wage-templates', tags=['Hour_wage_templates: 시급 템플릿 CRUD'])
admin_router.include_router(parts_policy.router, prefix="/branches/{branch_id}/parts-policies", tags=["Parts_policies: 파트 근무 정책/파트 급여 정책 관련"])



admin_router.include_router(salary_bracket.router, prefix='/salary-bracket', tags=['Salary Bracket: 급여 구간 CRUD'])
admin_router.include_router(user_management_document.router, prefix='/user-management/document', tags=['User_Management_Document: 문서 관련(발송/승인/반려/취소) '])
admin_router.include_router(user_management_contract.router, prefix='/user-management/contract', tags=['User_Management_Contract: 계약 CRUD, 계약 메일 발송'])
admin_router.include_router(user_management_work_contract.router, prefix='/user-management/work-contract', tags=['User_Management_Work_Contract: 근로 계약 CRUD'])
admin_router.include_router(user_management.router, prefix='/user-management', tags=['User_Management: 사용자 CRUD, 본인 정보/관리자 정보'])

admin_router.include_router(attendance.router, prefix="/branches", tags=["Attendance | Admin Only: 근태 조회"])
admin_router.include_router(commutes_manager.router, prefix="/branches", tags=["commutes_manager | Admin Only: 직원들 출퇴근 현황 "])
admin_router.include_router(part_timer.router, prefix="/labor-management", tags=["Part_timer | Admin Only : 파트타이머 관련"])

admin_router.include_router(leave_policies.router, prefix='/branches/{branch_id}/leave-policies', tags=['Leave_Policies: 자동 휴무 정책 관련'])
admin_router.include_router(menu_management.router, prefix='/menu-management', tags=['Menu_Management : 메뉴 권한 수정'])
admin_router.include_router(minimum_wage_policies.router, prefix='/minimum-wage-policies', tags=['Minimum_Wage_Policies: 최저 시급 정책'])
admin_router.include_router(salary_template.router, prefix='/branches/{branch_id}/salary-templates', tags=['Salary_Templates: 급여 템플릿'])
admin_router.include_router(salary_policies.router, prefix='/branches/{branch_id}/salary-policies', tags=['Salary_Policies: 전체 급여 정책'])
admin_router.include_router(webhook.router, prefix='/modusign-webhook', tags=['Modusign_Webhook'])
admin_router.include_router(document.router, prefix='/modusign-document', tags=['Modusign_Document'])
admin_router.include_router(template.router, prefix='/modusign-template', tags=['Modusign_Template'])
admin_router.include_router(personnel_record_category.router, prefix='/branches/{branch_id}/personnel-record-categories', tags=['Personnel_Record_Categories'])


# 일반 사원 접근 라우터 (employee)
employee_router = APIRouter(prefix="/employee", tags=["Employee"])

# MSO 전용
mso_router = APIRouter(prefix="/mso", tags=["MSO"])
	# 추후 추가 가능

app.include_router(public_router)
app.include_router(admin_router)
app.include_router(employee_router)
app.include_router(mso_router)
