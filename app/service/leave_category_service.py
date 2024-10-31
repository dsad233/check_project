from app.schemas.leave_category_schemas import LeaveCategoryDto
from app.cruds.leave_categories import leave_categories_crud, leave_excluded_parts_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.leave_category_schemas import LeaveCategoryWithExcludedPartsDto
from app.cruds.parts import parts_crud
from app.schemas.parts_schemas import PartIdWithName
from app.models.branches.leave_categories_model import LeaveCategory
from app.exceptions.exceptions import BadRequestError, NotFoundError


async def get_filtered_leave_categories(
    *,
    session: AsyncSession,
    branch_id: int,
    user_id: int
) -> list[LeaveCategoryDto]:
    """휴무 제외파트 필터링 후 휴무 카테고리 조회"""
    leave_categories = await leave_categories_crud.find_all_with_excluded_parts(
        session=session, branch_id=branch_id)
    result = []
    for leave_category in leave_categories:
        if user_id in [excluded_part.part_id for excluded_part in leave_category.excluded_parts]:
            continue
        result.append(LeaveCategoryDto.model_validate(leave_category))
    return result


async def get_all_leave_categories(*, 
    session: AsyncSession,
    branch_id: int
) -> list[LeaveCategoryDto]:
    """휴무 카테고리 조회"""
    leave_categories = await leave_categories_crud.find_all_by_branch_id(
        session=session, branch_id=branch_id
    )
    if not leave_categories:
        return []
    return [LeaveCategoryDto.model_validate(leave_category) for leave_category in leave_categories]


async def get_all_with_excluded_parts(*,
    session: AsyncSession,
    branch_id: int
) -> list[LeaveCategoryWithExcludedPartsDto]:
    """휴무 카테고리, 제외파트 조회"""
    leave_categories = await leave_categories_crud.find_all_by_branch_id(
        session=session, branch_id=branch_id
    )
    result = []
    # 제외 부서 id와 이름 추가
    for leave_category in leave_categories:
        # 해당 휴무의 제외 부서 전체 조회
        excluded_parts = await leave_excluded_parts_crud.find_all_by_leave_category_id(
            session=session, leave_category_id=leave_category.id
        )
        # 제외 부서가 가지는 part_id로 이름 추출
        excluded_parts_data = [(
            PartIdWithName.model_validate(await parts_crud.find_by_id(
                session=session, part_id=excluded_part.part_id
            ))
        ) for excluded_part in excluded_parts]
        result.append(LeaveCategoryWithExcludedPartsDto(
            excluded_parts=excluded_parts_data,
            leave_category=LeaveCategoryDto.model_validate(leave_category)
        ))
    return result


async def create_leave_category(*,
    session: AsyncSession,
    branch_id: int,
    request: LeaveCategoryWithExcludedPartsDto
) -> LeaveCategoryWithExcludedPartsDto:
    """휴무 카테고리, 제외파트 생성"""
    leave_category = await leave_categories_crud.find_by_name_and_branch_id(session=session, branch_id=branch_id, name=request.leave_category.name)
    if leave_category:
        raise BadRequestError(detail=f"{branch_id}번 지점의 휴가 카테고리 이름 {request.leave_category.name}이(가) 이미 존재합니다.")
    
    leave_category = await leave_categories_crud.create(
        session=session, branch_id=branch_id, request=LeaveCategory(branch_id=branch_id, **request.leave_category.model_dump())
    )
    leave_category_id = leave_category.id
    create_excluded_part_ids = [part.id for part in request.excluded_parts]
    if create_excluded_part_ids:
        await leave_excluded_parts_crud.create_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=create_excluded_part_ids
        )
    return request


async def update_leave_category(*,
    session: AsyncSession,
    branch_id: int,
    leave_category_id: int,
    request: LeaveCategoryWithExcludedPartsDto
) -> bool:
    """휴무 카테고리, 제외파트 수정"""
    # 기존 정책 조회
    leave_category = await leave_categories_crud.find_by_id_and_branch_id(
        session=session, branch_id=branch_id, leave_id=leave_category_id
    )
    if leave_category is None:
        raise NotFoundError(f"{branch_id}번 지점의 {leave_category_id}번 휴가 카테고리가 존재하지 않습니다.")
    
    if leave_category.name != request.leave_category.name:
        duplicate_leave_category = await leave_categories_crud.find_by_name_and_branch_id(session=session, branch_id=branch_id, name=request.leave_category.name)
        if duplicate_leave_category is not None:
            raise BadRequestError(detail=f"{branch_id}번 지점의 휴가 카테고리 이름 {request.leave_category.name}이(가) 이미 존재합니다.")
    
    await leave_categories_crud.update(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id, request=LeaveCategory(branch_id=branch_id, **request.leave_category.model_dump(exclude_unset=True)), old=leave_category
    )
    # 해당 휴무의 제외 부서 전체 조회
    excluded_parts = await leave_excluded_parts_crud.find_all_by_leave_category_id(
        session=session, leave_category_id=leave_category_id
    )
    
    saved_part_ids = set([excluded_part.part_id for excluded_part in excluded_parts])
    request_part_ids = set([part.id for part in request.excluded_parts])
    #삭제하거나 추가할 부서 id 추출
    part_ids_to_delete = saved_part_ids - request_part_ids
    part_ids_to_create = request_part_ids - saved_part_ids

    if part_ids_to_delete:
        await leave_excluded_parts_crud.delete_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=part_ids_to_delete
        )
    if part_ids_to_create:
        await leave_excluded_parts_crud.create_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=part_ids_to_create
        )
    return True


async def delete_leave_category(*,
    session: AsyncSession,
    branch_id: int,
    leave_category_id: int
) -> bool:
    """휴무 카테고리 삭제"""
    leave_category = await leave_categories_crud.find_by_id_and_branch_id(
        session=session, branch_id=branch_id, leave_id=leave_category_id
    )
    if leave_category is None:
        raise NotFoundError(f"{branch_id}번 지점의 {leave_category_id}번 휴가 카테고리를 찾을 수 없습니다.")
    
    return await leave_categories_crud.delete(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id
    )