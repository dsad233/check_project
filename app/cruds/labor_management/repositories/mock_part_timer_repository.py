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
        self.dummy_part_timer_work_history : List[PartTimerWorkHistoryResponseDTO] = [
            PartTimerWorkHistoryResponseDTO(
                commute_id=1001,
                part_name="피부과 의사",
                task="진료",
                work_start_time=datetime(2024, 10, 1, 9, 0),
                work_end_time=datetime(2024, 10, 1, 18, 0),
                work_start_set_time=datetime(2023, 5, 1, 9, 0),
                work_end_set_time=datetime(2023, 5, 1, 18, 0),
                working_hours=8.0,
                rest_minites=60,
                total_wage=100000.0,
                created_at=datetime(2023, 5, 1, 18, 0)
            ),
            PartTimerWorkHistoryResponseDTO(
                commute_id=1002,
                part_name="간호사",
                task="간호",
                work_start_time=datetime(2024, 10, 2, 9, 0),
                work_end_time=datetime(2024, 10, 2, 18, 0),
                work_start_set_time=datetime(2023, 5, 2, 9, 0),
                work_end_set_time=datetime(2023, 5, 2, 18, 0),
                working_hours=8.0,
                rest_minites=60,
                total_wage=80000.0,
                created_at=datetime(2023, 5, 2, 18, 0)
            ),
            PartTimerWorkHistoryResponseDTO(
                commute_id=1003,
                part_name="피부과 의사",
                task="진료",
                work_start_time=datetime(2024, 11, 3, 9, 0),
                work_end_time=datetime(2024, 11, 3, 18, 0),
                work_start_set_time=datetime(2023, 5, 3, 9, 0),
                work_end_set_time=datetime(2023, 5, 3, 18, 0),
                working_hours=8.0,
                rest_minites=60,
                total_wage=100000.0,
                created_at=datetime(2023, 5, 3, 18, 0)
            ),
            PartTimerWorkHistoryResponseDTO(
                commute_id=1004,
                part_name="피부과 의사",
                task="진료",
                work_start_time=datetime(2024, 11, 4, 9, 0),
                work_end_time=datetime(2024, 11, 4, 18, 0),
                work_start_set_time=datetime(2023, 5, 4, 9, 0),
                work_end_set_time=datetime(2023, 5, 4, 18, 0),
                working_hours=8.0,
                rest_minites=60,
                total_wage=100000.0,
                created_at=datetime(2023, 5, 4, 18, 0)
            ),
            PartTimerWorkHistoryResponseDTO(
                commute_id=1005,
                part_name="피부과 의사",
                task="진료",
                work_start_time=datetime(2024, 10, 5, 9, 0),
                work_end_time=datetime(2024, 10, 5, 18, 0),
                work_start_set_time=datetime(2023, 5, 5, 9, 0),
                work_end_set_time=datetime(2023, 5, 5, 18, 0),
                working_hours=8.0,
                rest_minites=60,
                total_wage=100000.0,
                created_at=datetime(2023, 5, 5, 18, 0)
            )
        ]

    def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return self.dummy_part_timer_summaries

    def get_part_timer_work_history(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryResponseDTO]:
        return [
            history for history in self.dummy_part_timer_work_history
            if history.work_start_time.year == year and history.work_start_time.month == month
        ]
    
    def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return [
            summary for summary in self.dummy_part_timer_summaries
            if summary.branch_name == "대구 지점" and summary["work_start_time"].year == year and summary["work_start_time"].month == month
        ]
    
    def get_all_part_timers_by_part_id(self, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return [
            summary for summary in self.dummy_part_timer_summaries
            if summary.branch_name == "대구 지점" and summary.part_name == "피부과 의사" and summary["work_start_time"].year == year and summary["work_start_time"].month == month
        ]