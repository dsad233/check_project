from typing import List
from pydantic import BaseModel

class PartTimerSummaryResponseDTO(BaseModel):
    user_id: int
    gender: str
    branch_name: str
    user_name: str
    part_name: str
    work_days: int
    hospital_work_hours: int
    holiday_work_hours: int
    total_work_hours: float
    total_wage: float
    
    @classmethod
    def get_part_timer_summaries_response(cls, part_timer_summary, part_timer_work_hour_and_total_wage) -> List["PartTimerSummaryResponseDTO"]:
        hour_wage_dict = { item.user_id: item for item in part_timer_work_hour_and_total_wage }
        return [
            cls(
                user_id=summary.user_id,
                gender=summary.gender,
                branch_name=summary.branch_name,
                user_name=summary.user_name,
                part_name=summary.part_name,
                work_days=summary.work_count,
                total_work_hours=hour_wage_dict[summary.user_id].total_work_hours,
                hospital_work_hours=hour_wage_dict[summary.user_id].regular_work_hours,
                holiday_work_hours=hour_wage_dict[summary.user_id].holiday_work_hours,
                total_wage=hour_wage_dict[summary.user_id].total_wage
            )
            for summary in part_timer_summary
        ]
