from functools import wraps
from typing import List
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.users import Role, MenuPermissions
from sqlalchemy import select, and_

from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users, user_menus, user_parts

ROLE_LEVELS = {
    Role.MSO: 0,
    Role.SUPER_ADMIN: 1,
    Role.INTEGRATED_ADMIN: 10,
    Role.ADMIN: 20,
    Role.EMPLOYEE: 30,
    Role.ON_LEAVE: 40,
    Role.RESIGNED: 50,
}

def available_higher_than(minimum_role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                request = next((v for v in kwargs.values() if isinstance(v, Request)), None)

            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")

            user = request.state.user

            if not user.role:
                raise HTTPException(status_code=401, detail="권한 정보가 없습니다.")

            if ROLE_LEVELS[user.role] <= ROLE_LEVELS[minimum_role]:
                return await func(*args, **kwargs)

            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return wrapper
    return decorator



def check_menu_permission(required_menu: MenuPermissions):
    """
        특정 메뉴에 대한 접근 권한을 확인하는 데코레이터
            사용할 때 의존성 주입
            - db: AsyncSession = Depends(get_db),
            - current_user: Users = Depends(get_current_user)

        역할별 권한:
        ***주의) 데이터 조회 시 MSO 제외 하고는 branch_id 필터링 필요합니다. 해당 지점만 관리 가능하기 때문에***
        ***파트 관리자의 경우 브랜치, 파트 필터링 둘 다 필요합니다.***
        - MSO, SUPER_ADMIN, INTEGRATED_ADMIN: 모든 메뉴 접근 가능
        - ADMIN(파트관리자): 자신의 파트에 해당하는 메뉴만 접근 가능
        - MSO를 제외한 모든 역할은 자신의 지점 데이터만 조회 가능
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Depends를 통해 주입된 db 세션과 current_user를 찾음
            db = kwargs.get('db')
            current_user = kwargs.get('current_user')

            if not db or not current_user:
                raise HTTPException(
                    status_code=500,
                    detail="Database session or current user not found"
                )

            # MSO와 SUPER_ADMIN, INTEGRATED_ADMIN은 모든 메뉴 접근 가능
            if current_user.role in [Role.MSO, Role.SUPER_ADMIN, Role.INTEGRATED_ADMIN]:
                return await func(*args, **kwargs)


            # 파트 관리자일 경우
            if current_user.role == Role.ADMIN:
                # 1. 사용자의 파트 확인
                if not current_user.part_id:
                    raise HTTPException(
                        status_code=403,
                        detail="파트 정보가 없는 관리자는 메뉴에 접근할 수 없습니다."
                    )

                #2. 해당 파트에 속한 메뉴 권한 조히
                query = select(user_menus).where(
                    and_(
                        user_menus.c.user_id == current_user.id,
                        user_menus.c.menu_name == required_menu,
                        user_menus.c.is_permitted == True,
                        user_menus.c.part_id == current_user.part_id
                    )
                )
                result = await db.execute(query)
                permission = result.first()

                if not permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"해당 파트의 {required_menu.value} 메뉴에 대한 접근 권한이 없습니다."
                    )
                return await func(*args, **kwargs)

            if current_user.role in [Role.EMPLOYEE, Role.ON_LEAVE, Role.RESIGNED]:
                raise  HTTPException(
                    status_code=403,
                    detail="해당 메뉴에 대한 접근 권한이 없습니다."
                )

            #그 외 예상치 못한 ROLE
            raise HTTPException(
                status_code=403,
                detail= "알 수 없는 권한: 해당 메뉴에 접근이 불가능합니다."
            )

        return wrapper
    return decorator

async def check_part_in_branch(db: AsyncSession, part_id: int, branch_id: int) -> bool:
    """파트가 해당 지점에 속하는지 확인"""
    query = select(Parts).where(
        and_(
            Parts.id == part_id,
            Parts.branch_id == branch_id,
            Parts.deleted_yn == "N"
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None



async def can_manage_user_permissions(current_user: Users, target_user: Users, db: AsyncSession, part_id: int = None) -> bool:
    """사용자가 다른 사용자의 권한을 관리할 수 있는지 확인하는 메서드"""
    if not current_user.role or not target_user.role:
        return False

    current_level = ROLE_LEVELS[current_user.role]
    target_level = ROLE_LEVELS[target_user.role]

    # 1. MSO 관련 로직 먼저 체크
    if target_user.role == Role.MSO:
        # MSO만 다른 MSO의 권한을 관리할 수 있음
        if current_user.role != Role.MSO:
            raise HTTPException(
                status_code=403,
                detail="MSO 관련 권한은 오직 MSO만 관리할 수 있습니다."
            )
    # MSO는 모든 지점의 모든 사용자 관리 가능
    if current_user.role == Role.MSO:
        if part_id and not await check_part_in_branch(db, part_id, target_user.branch_id):
            raise HTTPException(
                status_code=400,
                detail=f"파트 ID {part_id}는 해당 사용자가 속한 지점에 존재하지 않습니다."
            )
        return True

    # 2. 지점 확인 (MSO를 제외한 모든 관리자급)
    if current_user.role in [Role.SUPER_ADMIN, Role.INTEGRATED_ADMIN, Role.ADMIN]:
        if current_user.branch_id != target_user.branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 사용자의 권한은 관리할 수 없습니다.")

    # 파트가 해당 지점에 속하는지 확인
    if part_id and not await check_part_in_branch(db, part_id, target_user.branch_id):
        raise HTTPException(
            status_code=400,
            detail=f"파트 ID {part_id}는 해당 사용자가 속한 지점에 존재하지 않습니다."
        )

    # 3. 역할별 권한 체크
    # 최고 관리자 (MSO를 제외한 모든 권한 관리 가능)
    if current_user.role == Role.SUPER_ADMIN:
        return True

    # 통합 관리자
    # 자기 지점의, 자신보다 숫자가 같거나 높은 레벨 권한을 관리하려고 하면 Error
    if current_user.role == Role.INTEGRATED_ADMIN:
        if target_level <= current_level:
            raise HTTPException(
                status_code=403,
                detail="통합 관리자는 같은 레벨, 보다 높은 권한을 가진 사용자의 권한은 수정할 수 없습니다."
            )
        return True

    raise HTTPException(
        status_code=403,
        detail="해당 파트 관리 권한이 없습니다."
    )


async def get_branch_filters(current_user: Users) -> List:
    """지점 기반 필터링 조건 생성

    Args:
        current_user: 현재 요청한 사용자

    Returns:
        List: 필터링 조건 리스트
    """
    conditions = [Users.deleted_yn == "N"]  # 기본 조건

    current_level = ROLE_LEVELS[current_user.role]

    # MSO가 아닌 경우 지점 필터링 추가
    if current_level > ROLE_LEVELS[Role.MSO]:
        conditions.append(Users.branch_id == current_user.branch_id)

    return conditions


async def get_part_branch_filters(current_user: Users) -> List:
    """지점과 파트 기반 필터링 조건 생성

    Args:
        current_user: 현재 요청한 사용자

    Returns:
        List: 필터링 조건 리스트

    Note:
        - MSO: 모든 지점/파트 데이터 조회 가능
        - SUPER_ADMIN/INTEGRATED_ADMIN: 자신의 지점 데이터 조회 가능
        - ADMIN: 자신의 지점의 특정 파트 데이터만 조회 가능
    """
    conditions = []
    current_level = ROLE_LEVELS[current_user.role]

    # 기본 조건
    conditions.append(Users.deleted_yn == "N")

    # MSO가 아닌 경우 지점 필터링
    if current_level > ROLE_LEVELS[Role.MSO]:
        conditions.append(Users.branch_id == current_user.branch_id)

    # ADMIN인 경우 파트 필터링
    if current_level == ROLE_LEVELS[Role.ADMIN]:
        if not current_user.part_id:
            raise HTTPException(
                status_code=403,
                detail="파트 정보가 없는 관리자는 조회할 수 없습니다."
            )
        conditions.append(Users.part_id == current_user.part_id)

    # 권한에 따른 조회 가능한 사용자 제한
    if current_level > ROLE_LEVELS[Role.INTEGRATED_ADMIN]:
        excluded_roles = [Role.MSO.value, Role.SUPER_ADMIN.value, Role.INTEGRATED_ADMIN.value]
        conditions.append(Users.role.notin_(excluded_roles))

    return conditions