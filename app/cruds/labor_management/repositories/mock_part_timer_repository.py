from datetime import datetime
from typing import List

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request import PartTimerCommuteHistoryCorrectionRequestDTO
from app.api.routes.labor_management.dto.part_timer_commute_history_correction_response import PartTimerCommuteHistoryCorrectionResponseDTO
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryDTO, PartTimerWorkHistorySummaryDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

class MockPartTimerRepository(IPartTimerRepository):
    _instance = None

    @classmethod
    def get_instance(self):
        if not self._instance:
            self._instance = MockPartTimerRepository()
        return self._instance
    
    def __init__(self):
        self.dummy_part_timer_summaries: List[PartTimerSummaryResponseDTO] = [
            PartTimerSummaryResponseDTO(
                user_id=5001,
                gender="남자",
                branch_name="서울 본원",
                user_name="앨리스",
                part_name="피부과 의사",
                work_days=3,
                hospital_work_hours=44,
                holiday_work_hours=16,
                total_work_hours=60.0,
                total_wage=440024.0,
                phone_number="01012345678",
                branch_id=1,
                part_id=1
            ),
            PartTimerSummaryResponseDTO(
                user_id=5002,
                gender="남자",
                branch_name="서울 본원",
                user_name="밥",
                part_name="간호사",
                work_days=3,
                hospital_work_hours=20,
                holiday_work_hours=0,
                total_work_hours=20.0,
                total_wage=400000.0,
                phone_number="01023456789",
                branch_id=1,
                part_id=2
            ),
            PartTimerSummaryResponseDTO(
                user_id=5003,
                gender="남자",
                branch_name="부산 지점",
                user_name="찰리",
                part_name="피부과 의사",
                work_days=3,
                hospital_work_hours=20,
                holiday_work_hours=0,
                total_work_hours=20.0,
                total_wage=600000.0,
                phone_number="01034567890",
                branch_id=2,
                part_id=3
            ),
            PartTimerSummaryResponseDTO(
                user_id=5004,
                gender="남자",
                branch_name="서울 본원",
                user_name="데이비드",
                part_name="피부과 의사",
                work_days=2,
                hospital_work_hours=20,
                holiday_work_hours=0,
                total_work_hours=20.0,
                total_wage=200000.0,
                phone_number="01045678901",
                branch_id=1,
                part_id=1
            ),
            PartTimerSummaryResponseDTO(
                user_id=5005,
                gender="남자",
                branch_name="대구 지점",
                user_name="에바",
                part_name="피부과 의사",
                work_days=2,
                hospital_work_hours=10,
                holiday_work_hours=0,
                total_work_hours=10.0,
                total_wage=200000.0,
                phone_number="01056789012",
                branch_id=3,
                part_id=5
            ),
            PartTimerSummaryResponseDTO(
                user_id=5006,
                gender="여자",
                branch_name="서울 본원",
                user_name="피오나",
                part_name="간호사",
                work_days=3,
                hospital_work_hours=24,
                holiday_work_hours=8,
                total_work_hours=32.0,
                total_wage=320000.0,
                phone_number="01067890123",
                branch_id=1,
                part_id=2
            ),
            PartTimerSummaryResponseDTO(
                user_id=5007,
                gender="남자",
                branch_name="부산 지점",
                user_name="조지",
                part_name="피부과 의사",
                work_days=4,
                hospital_work_hours=32,
                holiday_work_hours=0,
                total_work_hours=32.0,
                total_wage=640000.0,
                phone_number="01078901234",
                branch_id=2,
                part_id=3
            ),
            PartTimerSummaryResponseDTO(
                user_id=5008,
                gender="여자",
                branch_name="대구 지점",
                user_name="헬렌",
                part_name="간호사",
                work_days=2,
                hospital_work_hours=16,
                holiday_work_hours=4,
                total_work_hours=20.0,
                total_wage=200000.0,
                phone_number="01089012345",
                branch_id=3,
                part_id=6
            ),
            PartTimerSummaryResponseDTO(
                user_id=5009,
                gender="남자",
                branch_name="서울 본원",
                user_name="이안",
                part_name="피부과 의사",
                work_days=3,
                hospital_work_hours=30,
                holiday_work_hours=10,
                total_work_hours=40.0,
                total_wage=400000.0,
                phone_number="01090123456",
                branch_id=1,
                part_id=1
            ),
            PartTimerSummaryResponseDTO(
                user_id=5010,
                gender="여자",
                branch_name="부산 지점",
                user_name="제인",
                part_name="간호사",
                work_days=3,
                hospital_work_hours=24,
                holiday_work_hours=8,
                total_work_hours=32.0,
                total_wage=320000.0,
                phone_number="01001234567",
                branch_id=2,
                part_id=4
            )
        ]
        self.dummy_part_timer_work_histories = {
            5001: [
                PartTimerWorkHistoryDTO(
                    commute_id=1001,
                    part_name="피부과 의사",
                    task="진료",
                    work_start_time=datetime(2024, 10, 1, 9, 0),
                    work_end_time=datetime(2024, 10, 1, 18, 0),
                    work_start_set_time=datetime.now(),
                    work_end_set_time=datetime.now(),
                    working_hours=8.0,
                    rest_minutes=60,
                    total_wage=100000.0,
                    created_at=datetime(2023, 5, 1, 18, 0)
                ),
                PartTimerWorkHistoryDTO(
                    commute_id=1003,
                    part_name="피부과 의사",
                    task="진료",
                    work_start_time=datetime(2024, 10, 3, 9, 0),
                    work_end_time=datetime(2024, 10, 3, 18, 0),
                    work_start_set_time=datetime.now(),
                    work_end_set_time=datetime.now(),
                    working_hours=8.0,
                    rest_minutes=60,
                    total_wage=100000.0,
                    created_at=datetime(2023, 5, 3, 18, 0)
                ),
                PartTimerWorkHistoryDTO(
                    commute_id=1004,
                    part_name="피부과 의사",
                    task="진료",
                    work_start_time=datetime(2024, 10, 4, 9, 0),
                    work_end_time=datetime(2024, 10, 4, 18, 0),
                    work_start_set_time=datetime.now(),
                    work_end_set_time=datetime.now(),
                    working_hours=8.0,
                    rest_minutes=60,
                    total_wage=100000.0,
                    created_at=datetime(2023, 5, 4, 18, 0)
                ),
                PartTimerWorkHistoryDTO(
                    commute_id=1005,
                    part_name="피부과 의사",
                    task="진료",
                    work_start_time=datetime(2024, 10, 5, 9, 0),
                    work_end_time=datetime(2024, 10, 5, 18, 0),
                    work_start_set_time=datetime.now(),
                    work_end_set_time=datetime.now(),
                    working_hours=8.0,
                    rest_minutes=60,
                    total_wage=100000.0,
                    created_at=datetime(2023, 5, 5, 18, 0)
                )
            ],
            5002: [
                PartTimerWorkHistoryDTO(
                    commute_id=1002,
                    part_name="간호사",
                    task="간호",
                    work_start_time=datetime(2024, 10, 2, 9, 0),
                    work_end_time=datetime(2024, 10, 2, 18, 0),
                    work_start_set_time=datetime.now(),
                    work_end_set_time=datetime.now(),
                    working_hours=8.0,
                    rest_minutes=60,
                    total_wage=80000.0,
                    created_at=datetime(2023, 5, 2, 18, 0)
                )
            ]
        }
        self.user_id = 5001

    async def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return self.dummy_part_timer_summaries

    async def get_part_timer_work_histories(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryDTO]:
        return [
            history for history in self.dummy_part_timer_work_histories[user_id]
            if history.work_start_time.year == year and history.work_start_time.month == month
        ]
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return [
            summary for summary in self.dummy_part_timer_summaries
            if summary.branch_id == branch_id
        ]
    
    async def get_all_part_timers_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return [
            summary for summary in self.dummy_part_timer_summaries
            if summary.branch_id == branch_id and summary.part_id == part_id
        ]

    async def get_part_timer_work_history_summary_by_user_id(self, user_id: int, year: int, month: int) -> PartTimerSummaryResponseDTO | None:
        for summary in self.dummy_part_timer_summaries:
            if summary.user_id == user_id and year == 2024 and month == 10:
                return PartTimerWorkHistorySummaryDTO(
                    total_work_days=summary.work_days,
                    total_work_hours=summary.total_work_hours,
                    total_hospital_work_hours=summary.hospital_work_hours,
                    total_holiday_work_hours=summary.holiday_work_hours,
                    total_wage=summary.total_wage
                )
        return None
    
    async def get_part_timer_by_user_info(self, year: int, month: int, user_name: str | None, phone_number: str | None, branch_id: int, part_id: int) -> List[PartTimerSummaryResponseDTO]:
        # 실제로는 특정 날짜안에서의 아래 로직 진행
        if user_name and phone_number:
            return [
                summary for summary in self.dummy_part_timer_summaries
                if summary.user_name == user_name
                and summary.phone_number == phone_number
                and summary.branch_id == branch_id
                and summary.part_id == part_id
            ]
        elif user_name:
            return [
                summary for summary in self.dummy_part_timer_summaries
                if summary.user_name == user_name
                and summary.branch_id == branch_id
                and summary.part_id == part_id
            ]
        elif phone_number:
            return [
                summary for summary in self.dummy_part_timer_summaries
                if summary.phone_number == phone_number
                and summary.branch_id == branch_id
                and summary.part_id == part_id
            ]
        return []

    async def update_part_timer_work_history(self, commute_id: int, correction_data: PartTimerCommuteHistoryCorrectionRequestDTO) -> PartTimerCommuteHistoryCorrectionResponseDTO:        
        result = PartTimerCommuteHistoryCorrectionResponseDTO()
        result.commute_id = commute_id
        target: PartTimerWorkHistoryDTO = [
            history for history in self.dummy_part_timer_work_histories[self.user_id]
            if history.commute_id == commute_id
        ][0]

        # correction_data에서 None이 아닌 값만 추출해서 result에 덮어씌우기 + 데이터 변경
        if correction_data.part_id:
            result.part_id = correction_data.part_id
        if correction_data.work_start_time:
            result.work_start_time = correction_data.work_start_time
            target.work_start_time = correction_data.work_start_time
        if correction_data.work_end_time:
            result.work_end_time = correction_data.work_end_time
            target.work_end_time = correction_data.work_end_time
        if correction_data.rest_minutes:
            result.rest_minutes = correction_data.rest_minutes
            target.rest_minutes = correction_data.rest_minutes

        return result
    
    async def exist_part_timer_work_history(self, commute_id: int) -> bool:
        return commute_id in [history.commute_id for history in self.dummy_part_timer_work_histories[self.user_id]]
    
    