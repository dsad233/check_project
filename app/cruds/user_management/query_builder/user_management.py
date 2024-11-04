# query_builder/user_management.py
from dataclasses import dataclass
from typing import Optional, Any

from sqlalchemy import Select, select, func, case, literal_column, distinct, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload

from app.models.commutes.commutes_model import Commutes
from app.models.parts.parts_model import Parts
from app.models.parts.user_salary import UserSalary
from app.models.users.users_model import Users


@dataclass
class UserSearchFilter:
    name: Optional[str] = None
    phone: Optional[str] = None
    branch_id: Optional[int] = None
    part_id: Optional[int] = None
    status: Optional[str] = None
    admin_id: Optional[int] = None


@dataclass
class PaginationParams:
    page: int = 1
    record_size: int = 10


async def build_user_query(
        filter: UserSearchFilter,
) -> Select:
    """기본 쿼리와 필터 조건 구성"""
    user_alias = aliased(Users)

    query = (
        select(
            user_alias,
            func.max(Commutes.updated_at).label('last_activity'),
            func.max(UserSalary.monthly_salary).label('monthly_salary'),
            func.max(UserSalary.annual_salary).label('annual_salary')
        )
        .options(
            joinedload(user_alias.parts),
            joinedload(user_alias.branch)
        )
        .outerjoin(Commutes, user_alias.id == Commutes.user_id)
        .outerjoin(UserSalary, user_alias.id == UserSalary.user_id)
        .group_by(user_alias.id)
    )

    # 상태 필터
    if filter.status:
        query = apply_status_filter(query, user_alias, filter.status)

    # 검색 조건
    if filter.name:
        query = query.filter(user_alias.name.ilike(f"%{filter.name}%"))
    if filter.phone:
        query = query.filter(user_alias.phone_number.ilike(f"%{filter.phone}%"))
    if filter.branch_id:
        query = query.filter(user_alias.branch_id == filter.branch_id)
    if filter.part_id:
        query = query.filter(user_alias.parts.any(Parts.id == filter.part_id))

    # 정렬
    query = apply_ordering(query, user_alias, filter.admin_id)

    return query


def apply_status_filter(query: Select, user_alias: Any, status: str) -> Select:
    """상태 필터 적용"""
    status_filters = {
        "퇴사자": [user_alias.deleted_yn == "N", user_alias.role == "퇴사자"],
        "휴직자": [user_alias.deleted_yn == "N", user_alias.role == "휴직자"],
        "재직자": [user_alias.deleted_yn == "N", ~user_alias.role.in_(["퇴사자", "휴직자"])],
        "삭제회원": [user_alias.deleted_yn == "Y"]
    }

    if filters := status_filters.get(status):
        return query.filter(*filters)
    return query


def apply_ordering(query: Select, user_alias: Any, admin_id: Optional[int]) -> Select:
    """정렬 조건 적용"""
    return query.order_by(
        case(
            (user_alias.id == admin_id, literal_column("0")),
            else_=literal_column("1")
        ),
        user_alias.id
    )


async def get_total_count(
        session: AsyncSession,
        base_query: Select
) -> int:
    """총 레코드 수 조회"""
    count_query = (
        select(func.count(distinct(Users.id)))
        .select_from(base_query.subquery())
    )
    result = await session.execute(count_query)
    return result.scalar_one()


async def fetch_users(
        session: AsyncSession,
        query: Select,
        pagination: PaginationParams
) -> list[Row[tuple[Any, ...] | Any]]:
    """페이지네이션이 적용된 쿼리 실행"""
    paginated_query = query.offset(
        (pagination.page - 1) * pagination.record_size
    ).limit(pagination.record_size)

    result = await session.execute(paginated_query)
    return list(result.unique().all())
