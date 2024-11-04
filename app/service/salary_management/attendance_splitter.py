from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import List

from app.service.salary_management.attendance_classifier import AttendanceType
from app.service.salary_management.attendance_record import BreakTime

@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    type: str

class AttendanceRecordSplitter:
    NIGHT_START_HOUR = 22  # 야간 근무 시작 시각
    NIGHT_END_HOUR = 6    # 야간 근무 종료 시각
    REGULAR_HOURS = 8     # 정규 근무시간

    def __init__(self, regular_end_hour: int):  
        self.regular_end_hour = regular_end_hour
    
    def split_attendance(
        self, 
        clock_in: datetime, 
        clock_out: datetime, 
        is_holiday: bool,
        break_times: list[BreakTime] = None
    ) -> List[TimeSlot]:
        slots = []
        current_time = clock_in
        break_times = break_times or []
        
        while current_time < clock_out:
            next_boundary = self._get_next_time_boundary(current_time)
            end_time = min(next_boundary, clock_out)
            
            # 현재 시간 슬롯에 대한 휴게시간 처리
            actual_start = current_time
            actual_end = end_time
            
            for break_time in break_times:
                # 휴게시간이 현재 슬롯과 겹치는 경우
                if break_time.start <= actual_end and break_time.end >= actual_start:
                    # 휴게시간으로 인해 슬롯이 둘로 나뉘는 경우
                    if break_time.start > actual_start and break_time.end < actual_end:
                        slot_type = self._determine_slot_type(actual_start, break_time.start, is_holiday)
                        slots.append(TimeSlot(actual_start, break_time.start, slot_type))
                        slot_type = self._determine_slot_type(break_time.end, actual_end, is_holiday)
                        slots.append(TimeSlot(break_time.end, actual_end, slot_type))
                        continue
                    
                    # 휴게시간이 슬롯의 시작 부분을 잘라내는 경우
                    if break_time.start <= actual_start and break_time.end < actual_end:
                        actual_start = break_time.end
                    
                    # 휴게시간이 슬롯의 끝 부분을 잘라내는 경우
                    if break_time.start > actual_start and break_time.end >= actual_end:
                        actual_end = break_time.start
            
            # 유효한 근무시간이 있는 경우에만 슬롯 추가
            if actual_start < actual_end:
                slot_type = self._determine_slot_type(actual_start, actual_end, is_holiday)
                slots.append(TimeSlot(actual_start, actual_end, slot_type))
            
            current_time = end_time
        
        return slots 

    def _get_next_time_boundary(self, current_time: datetime) -> datetime:
        """다음 시간 경계를 반환"""
        current_hour = current_time.hour
        base_date = current_time.date()
        
        # 현재 시각이 야간 시간대(22:00 ~ 06:00)에 있는 경우
        if current_hour >= self.NIGHT_START_HOUR:
            # 다음날 06:00
            next_day = current_time.date() + timedelta(days=1)
            return datetime.combine(next_day, time(self.NIGHT_END_HOUR))
        elif current_hour < self.NIGHT_END_HOUR:
            # 당일 06:00
            return datetime.combine(base_date, time(self.NIGHT_END_HOUR))
        elif current_hour < self.regular_end_hour:
            # 당일 regular_end_hour
            return datetime.combine(base_date, time(self.regular_end_hour))
        elif current_hour < self.NIGHT_START_HOUR:
            # 당일 22:00
            return datetime.combine(base_date, time(self.NIGHT_START_HOUR))
        
        return current_time

    def _determine_slot_type(self, start: datetime, end: datetime, is_holiday: bool) -> str:
        """시간 슬롯의 타입을 결정"""
        if is_holiday:
            if self._is_night_time(start) or self._is_night_time(end):
                return AttendanceType.HOLIDAY_NIGHT.value
            return AttendanceType.HOLIDAY.value
        
        # 야간 시간대 체크
        is_night = self._is_night_time(start) or self._is_night_time(end)
        
        # 정규 근무시간(8시간) 초과 여부는 상위 로직에서 처리
        if is_night:
            return AttendanceType.NIGHT.value
        return AttendanceType.NORMAL.value

    def _is_night_time(self, dt: datetime) -> bool:
        """주어진 시각이 야간 시간대(22:00 ~ 06:00)에 속하는지 확인"""
        hour = dt.hour
        return hour >= self.NIGHT_START_HOUR or hour < self.NIGHT_END_HOUR