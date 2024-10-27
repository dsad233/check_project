from datetime import datetime
from typing import List
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryResponseDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

class MockPartTimerRepository(IPartTimerRepository):
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
                total_wage=440024.0
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
                total_wage=400000.0
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
                total_wage=600000.0
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
                total_wage=200000.0
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
                total_wage=200000.0
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
                total_wage=320000.0
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
                total_wage=640000.0
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
                total_wage=200000.0
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
                total_wage=400000.0
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
                total_wage=320000.0
            )
        ]
    def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return self.dummy_part_timer_summaries

