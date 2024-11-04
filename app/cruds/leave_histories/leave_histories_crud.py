from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.users import Status
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.branches.user_leaves_days import UserLeavesDays
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import (
    LeaveHistories,
    LeaveHistoriesCreate,
    LeaveHistoriesUpdate,
)
from app.models.users.users_model import Users
from datetime import date, datetime


async def get_leave_info(
    branch_id: int, year: int, current_user_id: int, db: AsyncSession
):
    """
    현재 사용자의 연차 일수 정보를 조회합니다.
    올해 1월 1일부터 12월 31까지 1년동안의 연차 일수를 조회합니다.
    """
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    leave_query = (
        select(UserLeavesDays)
        .where(
            UserLeavesDays.user_id == current_user_id,
            UserLeavesDays.branch_id == branch_id,
            UserLeavesDays.deleted_yn == "N",
            UserLeavesDays.created_at >= start_date,
            UserLeavesDays.created_at <= end_date,
        )
        .order_by(UserLeavesDays.created_at.desc())
    )
    result = await db.execute(leave_query)
    return result.scalar_one_or_none()


async def get_user_info(current_user_id: int, db: AsyncSession):
    """
    현재 사용자의 정보를 조회합니다.
    """
    user_query = select(Users).where(Users.id == current_user_id)
    user_result = await db.execute(user_query)
    return user_result.scalar_one_or_none()


async def fetch_leave_histories(
    current_user: Users,
    db: AsyncSession,
    search,
    date_start_day,
    date_end_day,
    branch_id,
    part_id,
    search_name,
    search_phone,
    page,
    size,
):
    """
    연차 신청 목록을 조회합니다.
    """
    base_query = select(LeaveHistories).where(
        LeaveHistories.deleted_yn == "N",
        LeaveHistories.application_date >= date_start_day,
        LeaveHistories.application_date <= date_end_day,
    )

    if current_user.role == "사원":
        base_query = base_query.where(LeaveHistories.user_id == current_user.id)

    if branch_id:
        base_query = base_query.join(
            Branches, LeaveHistories.branch_id == Branches.id
        ).where(Branches.id == branch_id)
    if part_id:
        base_query = base_query.join(Parts, LeaveHistories.part_id == Parts.id).where(
            Parts.id == part_id
        )
    if search_name:
        base_query = base_query.join(Users).where(Users.name.ilike(f"%{search_name}%"))
    if search_phone:
        base_query = base_query.join(Users).where(
            Users.phone_number.ilike(f"%{search_phone}%")
        )
    if search.kind:
        base_query = base_query.join(LeaveHistories.leave_category).where(
            LeaveCategory.name.ilike(f"%{search.kind}%")
        )
    if search.status:
        base_query = base_query.where(LeaveHistories.status.ilike(f"%{search.status}%"))

    skip = (page - 1) * size
    stmt = (
        base_query.order_by(LeaveHistories.created_at.desc()).offset(skip).limit(size)
    )

    result = await db.execute(stmt)
    leave_histories = result.scalars().all()

    count_query = base_query.with_only_columns(func.count())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one()

    return leave_histories, total_count


async def fetch_user_details(db: AsyncSession, leave_history):
    """
    연차 신청 목록에서 회원의 상세 정보를 조회합니다.
    """
    user_result = await db.execute(
        select(Users, Branches, Parts)
        .join(Branches, Users.branch_id == Branches.id)
        .join(Parts, Users.part_id == Parts.id)
        .where(Users.id == leave_history.user_id)
    )
    user, branch, part = user_result.first()

    category_query = select(LeaveCategory).where(
        LeaveCategory.id == leave_history.leave_category_id
    )
    category_result = await db.execute(category_query)
    leave_category = category_result.scalar_one_or_none()

    return user, branch, part, leave_category


async def fetch_approved_leave_data(
    db: AsyncSession,
    search,
    date_start_day,
    date_end_day,
    branch_id,
    part_id,
    search_name,
    search_phone,
):
    """
    연차 전체 승인 목록을 조회합니다.
    """
    base_query = (
        select(Users, Branches, Parts)
        .join(Branches, Users.branch_id == Branches.id)
        .join(Parts, Users.part_id == Parts.id)
        .where(Users.deleted_yn == "N")
    )

    if branch_id:
        base_query = base_query.where(Branches.id == branch_id)
    if part_id:
        base_query = base_query.where(Parts.id == part_id)
    if search_name:
        base_query = base_query.where(Users.name.ilike(f"%{search_name}%"))
    if search_phone:
        base_query = base_query.where(Users.phone_number.ilike(f"%{search_phone}%"))

    users_result = await db.execute(base_query)
    users = users_result.all()

    formatted_data = []
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1).date()

    for user, branch, part in users:
        unpaid_days_result = await db.execute(
            select(func.sum(LeaveHistories.decreased_days).label("total_unpaid_days"))
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
            .where(
                LeaveHistories.user_id == user.id,
                LeaveCategory.is_paid == False,
                LeaveHistories.status == "approved",
                LeaveHistories.deleted_yn == "N",
                LeaveHistories.application_date >= year_start,
                LeaveHistories.application_date <= date_end_day,
            )
        )
        total_unpaid_days = unpaid_days_result.scalar() or 0

        paid_days_result = await db.execute(
            select(func.sum(LeaveHistories.decreased_days).label("total_paid_days"))
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
            .where(
                LeaveHistories.user_id == user.id,
                LeaveCategory.is_paid == True,
                LeaveHistories.status == "approved",
                LeaveHistories.deleted_yn == "N",
                LeaveHistories.application_date >= year_start,
                LeaveHistories.application_date <= date_end_day,
            )
        )
        total_paid_days = paid_days_result.scalar() or 0

        increased_days_result = await db.execute(
            select(
                func.sum(LeaveHistories.increased_days).label("total_increased_days")
            ).where(
                LeaveHistories.user_id == user.id,
                LeaveHistories.deleted_yn == "N",
                LeaveHistories.application_date >= year_start,
                LeaveHistories.application_date <= date_end_day,
            )
        )
        total_increased_days = increased_days_result.scalar() or 0

        total_leave_days_result = await db.execute(
            select(UserLeavesDays.increased_days)
            .where(UserLeavesDays.user_id == user.id, UserLeavesDays.deleted_yn == "N")
            .order_by(UserLeavesDays.created_at.desc())
            .limit(1)
        )
        yearly_total_leave_days = total_leave_days_result.scalar() or 0

        leave_history_data = {
            "user_id": user.id,
            "user_name": user.name,
            "user_phone": user.phone_number,
            "user_gender": user.gender,
            "user_hire_date": user.hire_date,
            "user_resignation_date": user.resignation_date,
            "branch_id": branch.id,
            "branch_name": branch.name,
            "part_id": part.id,
            "part_name": part.name,
            "decreased_days": float(total_paid_days),
            "unpaid": float(total_unpaid_days),
            "increased_days": float(total_increased_days),
            "total_leave_days": float(yearly_total_leave_days),
            "can_use_days": float(yearly_total_leave_days - total_paid_days),
        }
        formatted_data.append(leave_history_data)

    total_count = len(formatted_data)
    return formatted_data, total_count


async def get_user_by_id(user_id: int, db: AsyncSession):
    """
    현재 사용자의 정보를 조회합니다.
    """
    user_query = select(Users).where(Users.id == user_id, Users.deleted_yn == "N")
    user_result = await db.execute(user_query)
    return user_result.scalar_one_or_none()


async def create_leave_history_record(
    leave_create: LeaveHistoriesCreate,
    branch_id: int,
    decreased_days: float,
    start_date: date,
    end_date: date,
    current_user: Users,
    db: AsyncSession,
):
    """
    연차 신청을 합니다.
    """
    create = LeaveHistories(
        branch_id=branch_id,
        part_id=current_user.part_id,
        user_id=current_user.id,
        leave_category_id=leave_create.leave_category_id,
        decreased_days=decreased_days,
        increased_days=0.00,
        start_date=start_date,
        end_date=end_date,
        application_date=datetime.now().date(),
        applicant_description=leave_create.applicant_description or None,
        status=Status.PENDING,
    )
    db.add(create)
    await db.flush()
    await db.refresh(create)
    return create.id

async def get_user_leaves_days_record(user_id: int, db: AsyncSession):
    """
    현재 사용자의 연차 일수 정보를 조회합니다.
    """
    existing_leave_days = await db.execute(
        select(UserLeavesDays)
        .where(
            UserLeavesDays.user_id == user_id,
            UserLeavesDays.deleted_yn == "N",
        )
        .order_by(UserLeavesDays.created_at.desc())
    )
    return existing_leave_days.scalar_one_or_none()



async def create_user_leaves_days_record(
    user_id: int, branch_id: int, current_user: Users, db: AsyncSession
):
    """
    현재 사용자의 연차 일수 정보를 생성합니다.
    """
    user_leaves_days = UserLeavesDays(
        user_id=user_id,
        branch_id=branch_id,
        part_id=current_user.part_id,
        increased_days=0.00,
        decreased_days=0.00,
        deleted_yn="N",
    )
    db.add(user_leaves_days)
    await db.flush()

async def get_leave_history_by_id(leave_id: int, db: AsyncSession):
    """
    현재 사용자의 연차 신청 정보를 조회합니다.
    """
    query = select(LeaveHistories).where(
        LeaveHistories.id == leave_id, LeaveHistories.deleted_yn == "N"
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_user_leaves_days(leave_days_record, decreased_days, db: AsyncSession):
    """
    현재 사용자의 연차 일수 정보를 업데이트합니다.
    """
    leave_days_record.decreased_days += decreased_days
    leave_days_record.total_leave_days -= decreased_days
    leave_days_record.updated_at = datetime.now()


async def update_user_total_leave_days(user_id: int, decreased_days, db: AsyncSession):
    """
    현재 사용자의 연차 일수 정보를 업데이트합니다.
    """
    await db.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(
            total_leave_days=Users.total_leave_days - decreased_days,
            updated_at=datetime.now(),
        )
    )


async def update_leave_history_status(
    leave_history, leave_approve, current_user, status, db: AsyncSession
):
    """
    연차 승인/반려를 합니다.
    """
    leave_history.status = status
    leave_history.admin_description = leave_approve.admin_description
    leave_history.manager_id = current_user.id
    leave_history.manager_name = current_user.name
    leave_history.approve_date = datetime.now()
    leave_history.updated_at = datetime.now()

async def get_leave_history_by_id_and_branch(
    leave_id: int, branch_id: int, db: AsyncSession
):
    """
    현재 사용자의 연차 신청 정보를 조회합니다.
    """
    query = select(LeaveHistories).where(
        LeaveHistories.id == leave_id,
        LeaveHistories.branch_id == branch_id,
        LeaveHistories.deleted_yn == "N",
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_leave_history(
    leave_history, leave_update: LeaveHistoriesUpdate, db: AsyncSession
):
    """
    연차 수정을 합니다.
    """
    if leave_update.leave_category_id:
        leave_history.leave_category_id = leave_update.leave_category_id
    if leave_update.date:
        leave_history.application_date = leave_update.date
    if leave_update.applicant_description:
        leave_history.applicant_description = leave_update.applicant_description


async def delete_leave_history(leave_history: LeaveHistories, db: AsyncSession):
    """
    연차 삭제를 합니다.
    """
    leave_history.deleted_yn = "Y"
