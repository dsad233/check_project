from datetime import datetime
from typing import Optional
from .attendance_classifier import AttendanceClassifier, AttendanceType
from .attendance_record import (
    AttendanceRecord,
    NormalAttendanceRecord,
    OvertimeAttendanceRecord,
    NightAttendanceRecord,
    HolidayAttendanceRecord,
    HolidayNightAttendanceRecord,
    ComplexAttendanceRecord
)

class AttendanceRecordFactory:
    classifier: AttendanceClassifier = AttendanceClassifier()

    # TODO: 하나의 출퇴근 기록으로 여러 근무 타입을 반환하도록 변경
    def create_attendance_record(
        self, 
        clock_in: datetime, 
        clock_out: datetime,
        is_holiday: bool
    ) -> AttendanceRecord:
        """
        출퇴근 기록과 휴일 여부를 기반으로 적절한 AttendanceRecord 객체를 생성
        """
        attendance_type = self.classifier.classify(clock_in, clock_out, is_holiday)
        
        record_map = {
            AttendanceType.NORMAL: NormalAttendanceRecord,
            AttendanceType.NORMAL_OVERTIME: OvertimeAttendanceRecord,
            AttendanceType.NORMAL_NIGHT: NightAttendanceRecord,
            AttendanceType.NORMAL_OVERTIME_NIGHT: ComplexAttendanceRecord,
            AttendanceType.HOLIDAY: HolidayAttendanceRecord,
            AttendanceType.HOLIDAY_NIGHT: HolidayNightAttendanceRecord,
            AttendanceType.NIGHT: NightAttendanceRecord
        }
        
        record_class = record_map.get(attendance_type)
        if not record_class:
            raise ValueError(f"Unknown work type: {attendance_type}")
            
        return record_class(clock_in, clock_out, is_holiday) 