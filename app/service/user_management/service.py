import logging
from typing import Optional, List, Tuple

from fastapi import Depends, HTTPException
from sqlalchemy import select, func, delete, distinct, literal_column, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

from app.cruds.user_management.base_crud import UserManagementRepository
from app.cruds.user_management.query_builder.user_management import UserSearchFilter, PaginationParams, \
    build_user_query, get_total_count
from app.cruds.users.career_crud import add_bulk_career
from app.cruds.users.education_crud import add_bulk_education
from app.cruds.users.users_crud import find_by_email, add_user
from app.enums.users import Role
from app.models.commutes.commutes_model import Commutes
from app.models.parts.parts_model import Parts
from app.models.parts.user_salary import UserSalary
from app.models.users.career_model import Career
from app.models.users.education_model import Education
from app.models.users.users_model import Users, UserCreate, UserUpdate
from app.schemas.user_management.user_management_schemas import UserListDto, UserDTO

logger = logging.getLogger(__name__)


class UserManagementService:
    def __init__(self, repository: UserManagementRepository):
        self.repository = repository

    async def add_user(
            self,
            user_create: UserCreate,
            session: AsyncSession,
    ):
        # 1. education과 career 데이터 분리
        education_data = user_create.educations
        career_data = user_create.careers

        # 2. Users 모델용 데이터만 추출
        user_data = user_create.model_dump(exclude={'educations', 'careers'})

        # 3. 기존 사용자 확인
        existing_user = await find_by_email(session=session, email=user_data['email'])
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # 4. 사용자 생성
        user = Users(**user_data)
        created_user = await add_user(session=session, user=user)

        # 5. Education 데이터 생성
        if education_data:
            await add_bulk_education(session, created_user.id, education_data)

        # 6. Career 데이터 생성
        if career_data:
            await add_bulk_career(session, created_user.id, career_data)

        # 7. 변경사항 저장
        await session.flush()
        await session.commit()

        return created_user

    async def get_user(
            self,
            user_id: int,
    ):
        user = await self.repository.find_user_by_user_id(user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def get_users(
            self,
            session: AsyncSession,
            current_user_id: int,
            page: int,
            record_size: int,
            status: Optional[str] = None,
            name: Optional[str] = None,
            phone: Optional[str] = None,
            branch_id: Optional[int] = None,
            part_id: Optional[int] = None,
    ):

        search_filter = UserSearchFilter(
            name=name,
            phone=phone,
            branch_id=branch_id,
            part_id=part_id,
            status=status,
            admin_id=current_user_id
        )

        pagination = PaginationParams(page=page, record_size=record_size)
        base_query = await build_user_query(search_filter)
        total_count = await get_total_count(session, base_query)

        find_users = await self.repository.find_users(session=session, search_filter=search_filter, pagination=pagination)


    async def update_user_role(
            self,
            user_id: int,
            session: AsyncSession,
            role: Role = Role.EMPLOYEE,
    ) -> int:
        user = await self.get_user(user_id=user_id, session=session)
        user.role = role

        await session.flush()
        await session.commit()

        return user.id

    async def get_user_detail(
        self,
        *,
        db: AsyncSession,
        user_id: int,
        current_user: Users
    ) -> UserDTO:
        if not current_user:
            raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

        UserAlias = aliased(Users)

        # 요청된 사용자 정보 조회
        base_query = (
            select(UserAlias,
                   func.max(Commutes.updated_at).label('last_activity'),
                   func.max(UserSalary.monthly_salary).label('monthly_salary'),
                   func.max(UserSalary.annual_salary).label('annual_salary'))
            .options(
                joinedload(UserAlias.part),
                joinedload(UserAlias.branch),
                selectinload(UserAlias.educations),
                selectinload(UserAlias.careers)
            )
            .outerjoin(Commutes, UserAlias.id == Commutes.user_id)
            .outerjoin(UserSalary, UserAlias.id == UserSalary.user_id)
            .group_by(UserAlias.id)
            .where(UserAlias.id == user_id)
        )

        # 쿼리 실행
        result = await db.execute(base_query)
        user_data = result.unique().first()

        if not user_data:
            raise HTTPException(status_code=404, detail="요청한 사용자를 찾을 수 없거나 접근 권한이 없습니다.")

        user, last_activity, monthly_salary, annual_salary = user_data

        # DTO 변환
        return UserDTO.from_user_data(
            user=user,
            last_activity=last_activity,
            monthly_salary=monthly_salary,
            annual_salary=annual_salary
        )


    async def update_user(
        self,
        *,
        user_id: int,
        user_update: UserUpdate,
        session: AsyncSession,
        current_user: Users
    ) -> Users:
        try:
            # 사용자 조회
            query = (
                select(Users)
                .options(
                    joinedload(Users.educations),
                    joinedload(Users.careers),
                    joinedload(Users.part),
                    joinedload(Users.branch)
                )
                .where(Users.id == user_id)
            )
            result = await session.execute(query)
            user = result.unique().scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 업데이트할 데이터 준비
            update_dict = user_update.model_dump(exclude_unset=True)

            # educations와 careers 데이터 분리
            educations_data = update_dict.pop('educations', None)
            careers_data = update_dict.pop('careers', None)

            # 기본 사용자 정보 업데이트
            for field, value in update_dict.items():
                if hasattr(user, field) and not isinstance(value, (list, dict)):
                    setattr(user, field, value)

            # 교육 정보 업데이트
            if educations_data is not None:
                # 기존 교육 정보 삭제
                await session.execute(
                    delete(Education).where(Education.user_id == user_id)
                )
                await session.flush()  # 삭제 작업 즉시 반영

                # 새 교육 정보 추가
                for edu_data in educations_data:
                    new_education = Education(
                        user_id=user_id,
                        school_type=edu_data.get('school_type'),
                        school_name=edu_data.get('school_name'),
                        graduation_type=edu_data.get('graduation_type'),
                        major=edu_data.get('major'),
                        admission_date=edu_data.get('admission_date'),
                        graduation_date=edu_data.get('graduation_date')
                    )
                    session.add(new_education)

            # 경력 정보 업데이트
            if careers_data is not None:
                # 기존 경력 정보 삭제
                await session.execute(
                    delete(Career).where(Career.user_id == user_id)
                )
                await session.flush()  # 삭제 작업 즉시 반영

                # 새 경력 정보 추가
                for career_data in careers_data:
                    new_career = Career(
                        user_id=user_id,
                        company=career_data.get('company'),
                        contract_type=career_data.get('contract_type'),
                        start_date=career_data.get('start_date'),
                        end_date=career_data.get('end_date'),
                        job_title=career_data.get('job_title'),
                        department=career_data.get('department'),
                        position=career_data.get('position')
                    )
                    session.add(new_career)

            await session.commit()

            # 업데이트된 사용자 정보 다시 조회
            updated_user = await self.get_user_detail(
                db=session,
                user_id=user_id,
                current_user=current_user
            )

            return updated_user

        except HTTPException as http_exc:
            await session.rollback()
            raise http_exc
        except Exception as err:
            await session.rollback()
            logger.error(f"사용자 정보 업데이트 중 에러 발생: {str(err)}")
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


    async def update_user_permission(
            self,
            user_id: int,
            update_params: dict,
    ):
        ...

    # async def register_user(
    #         self,
    #         user: Users,
    #         session: AsyncSession
    # ):
    #     # Add user
    #     created_user = await self.add_user(session=session, user=user)
    #
    #     get_template_response = await modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)
    #
    #     signing_method = SigningMethod(
    #         type=SIGNINGMETHOD_OBJECT_TYPE.KAKAO,
    #         value=user.phone_number.replace("-", "")
    #     )
    #
    #     document_data = self.convert_template_response_to_document_data(
    #         template_response=get_template_response,
    #         signing_method=signing_method,
    #         user_name=created_user.name
    #     )
    #
    #     create_document_with_template_response = await modusign_document_service.create_document_with_template(
    #         document_data=document_data
    #     )
    #
    #     print(create_document_with_template_response)
    #
    #     return created_user
    #
    #
    # def convert_template_response_to_document_data(
    #         self,
    #         template_response: TemplateResponse,
    #         signing_method: SigningMethod,
    #         user_name: str
    # ) -> dict:
    #     return {
    #         "templateId": template_response.id,
    #         "document": {
    #             "title": template_response.title,
    #             "participantMappings": [
    #                 {
    #                     "signingMethod": signing_method.to_dict(),
    #                     "role": participant.role,
    #                     "name": user_name
    #                 }
    #                 for participant in template_response.participants
    #             ],
    #             "requesterInputMappings": [
    #                 {
    #                     "dataLabel": "USER_NAME",
    #                     "value": user_name
    #                 }
    #             ]
    #         }
    #     }



class UserQueryService:
    def __init__(self):
        self.UserAlias = aliased(Users)

    async def get_users_service(
        self,
        db: AsyncSession,
        current_user: Users,
        page: int,
        record_size: int,
        status: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        branch_id: Optional[int] = None,
        part_id: Optional[int] = None,
    ) -> Tuple[List[UserDTO], int]:
        """사용자 목록을 조회하는 서비스 메서드"""

        try:
            # 기본 쿼리 구성
            base_query = self._create_base_query()

            # 필터 적용
            query = await self._apply_filters(
                base_query,
                status,
                name,
                phone,
                branch_id,
                part_id
            )

            # 총 개수 계산
            total_count = await self._get_total_count(db, query)

            # 정렬 및 페이지네이션 적용
            query = self._apply_sorting_and_pagination(
                query,
                current_user.id,
                page,
                record_size
            )

            # 쿼리 실행 및 결과 처리
            users_data = await self._execute_query(db, query)

            return users_data, total_count

        except Exception as e:
            logger.error(f"사용자 목록 조회 중 에러 발생: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"사용자 목록을 조회하는 중 오류가 발생했습니다: {str(e)}"
            )

    def _create_base_query(self):
        """기본 쿼리 생성"""
        return (
            select(self.UserAlias,
                func.max(Commutes.updated_at).label('last_activity'),
                func.max(UserSalary.monthly_salary).label('monthly_salary'),
                func.max(UserSalary.annual_salary).label('annual_salary'))
            .options(joinedload(self.UserAlias.parts), joinedload(self.UserAlias.branch))
            .outerjoin(Commutes, self.UserAlias.id == Commutes.user_id)
            .outerjoin(UserSalary, self.UserAlias.id == UserSalary.user_id)
            .group_by(self.UserAlias.id)
        )

    async def _apply_filters(
        self,
        query,
        status: Optional[str],
        name: Optional[str],
        phone: Optional[str],
        branch_id: Optional[int],
        part_id: Optional[int]
    ):
        """필터 조건 적용"""
        if status:
            query = self._apply_status_filter(query, status)

        if name:
            query = query.filter(self.UserAlias.name.ilike(f"%{name}%"))
        if phone:
            query = query.filter(self.UserAlias.phone_number.ilike(f"%{phone}%"))
        if branch_id:
            query = query.filter(self.UserAlias.branch_id == branch_id)
        if part_id:
            query = query.filter(self.UserAlias.parts.any(Parts.id == part_id))

        return query

    def _apply_status_filter(self, query, status: str):
        """상태 필터 적용"""
        status_filters = {
            '퇴사자': (self.UserAlias.deleted_yn == "N", self.UserAlias.role == "퇴사자"),
            '휴직자': (self.UserAlias.deleted_yn == "N", self.UserAlias.role == "휴직자"),
            '재직자': (self.UserAlias.deleted_yn == "N", ~self.UserAlias.role.in_(["퇴사자", "휴직자"])),
            '전체': (self.UserAlias.deleted_yn == "N"),
            '삭제회원': (self.UserAlias.deleted_yn == "Y",)
        }

        if status in status_filters:
            return query.filter(*status_filters[status])
        return query

    async def _get_total_count(self, db: AsyncSession, query) -> int:
        """총 레코드 수 계산"""
        count_query = select(func.count(distinct(self.UserAlias.id))).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar_one()

    def _apply_sorting_and_pagination(
        self,
        query,
        current_user_id: int,
        page: int,
        record_size: int
    ):
        """정렬 및 페이지네이션 적용"""
        return query.order_by(
            case((self.UserAlias.id == current_user_id, literal_column("0")), else_=literal_column("1")),
            self.UserAlias.id
        ).offset((page - 1) * record_size).limit(record_size)

    async def _execute_query(self, db: AsyncSession, query) -> List[UserDTO]:
        """쿼리 실행 및 DTO 변환"""
        try:
            result = await db.execute(query)
            users_data = result.unique().all()

            return [
                UserListDto.from_orm(
                    user,
                    last_activity=last_activity,
                    monthly_salary=monthly_salary,
                    annual_salary=annual_salary
                )
                for user, last_activity, monthly_salary, annual_salary in users_data
            ]
        except Exception as e:
            logger.error(f"쿼리 실행 중 에러 발생: {str(e)}", exc_info=True)
            raise