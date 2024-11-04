from datetime import datetime
from typing import List
from .attendance_classifier import AttendanceType
from .attendance_record import (
    AttendanceRecord,
    BreakTime,
    NormalAttendanceRecord,
    OvertimeAttendanceRecord,
    NightAttendanceRecord,
    HolidayAttendanceRecord,
    HolidayNightAttendanceRecord
)
from .attendance_splitter import TimeSlot, AttendanceRecordSplitter

class AttendanceRecordFactory:
    def __init__(self, regular_end_hour: int):
        self.splitter = AttendanceRecordSplitter(regular_end_hour)
        
    def create_attendance_records(
        self,
        clock_in: datetime,
        clock_out: datetime,
        is_holiday: bool,
        break_times: list[BreakTime] = None
    ) -> List[AttendanceRecord]:
        """
        출퇴근 기록을 여러 개의 AttendanceRecord로 분할하여 생성
        """
        # 시간대별로 분할
        time_slots = self.splitter.split_attendance(clock_in, clock_out, is_holiday, break_times)
        
        # 각 슬롯을 해당하는 AttendanceRecord 객체로 변환
        records = []
        accumulated_hours = 0  # 누적 근무 시간 (초과 근무 판단용)
        
        for slot in time_slots:
            record = self._create_record_from_slot(
                slot, 
                is_holiday, 
                accumulated_hours,
                break_times
            )
            records.append(record)
            
            # 누적 시간 업데이트
            hours = (slot.end - slot.start).total_seconds() / 3600
            accumulated_hours += hours
            
        return records
    
    def _create_record_from_slot(
        self,
        slot: TimeSlot,
        is_holiday: bool,
        accumulated_hours: float,
        break_times: list[BreakTime]
    ) -> AttendanceRecord:
        """단일 TimeSlot을 적절한 AttendanceRecord 객체로 변환"""
        is_overtime = accumulated_hours >= 8
        
        # 슬롯에 해당하는 휴게시간만 필터링
        slot_break_times = [
            break_time for break_time in (break_times or [])
            if break_time.start >= slot.start and break_time.end <= slot.end
        ]
        
        record_map = {
            AttendanceType.NORMAL.value: NormalAttendanceRecord,
            AttendanceType.NIGHT.value: NightAttendanceRecord,
            AttendanceType.HOLIDAY.value: HolidayAttendanceRecord,
            AttendanceType.HOLIDAY_NIGHT.value: HolidayNightAttendanceRecord
        }
        
        # 초과근무인 경우 OvertimeAttendanceRecord로 변환
        if not is_holiday and is_overtime and slot.type == AttendanceType.NORMAL.value:
            record_class = OvertimeAttendanceRecord
        else:
            record_class = record_map.get(slot.type)
            
        if not record_class:
            raise ValueError(f"Unknown slot type: {slot.type}")
            
        return record_class(slot.start, slot.end, is_holiday, slot_break_times) 