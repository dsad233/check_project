from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

class AttendanceRecord(ABC):
    def __init__(self, clock_in: datetime, clock_out: datetime, is_holiday: bool):
        self._clock_in = clock_in
        self._clock_out = clock_out
        self._work_hours = 0
        self._calibrated_work_hours = 0

    @property
    def week_number(self) -> int:
        """해당 근무일의 주차를 반환"""
        return self._clock_in.isocalendar()[1]
    
    @property
    def clock_in_date(self) -> date:
        """근무일을 반환"""
        return self._clock_in.date()

    @abstractmethod
    def calculate_work_hours(self):
        """근무 시간을 계산하는 추상 메서드"""
        pass

    @abstractmethod
    def get_calibrated_work_hours(self) -> float:
        """보정된 근무 시간을 반환"""
        pass

    def get_clock_in(self) -> datetime:
        return self._clock_in

    def get_clock_out(self) -> datetime:
        return self._clock_out

    def get_work_hours(self) -> float:
        return self._work_hours

    def _calculate_total_hours(self) -> float:
        """총 근무 시간 계산"""
        return (self._clock_out - self._clock_in).total_seconds() / 3600

    def _get_night_period(self) -> tuple[datetime, datetime]:
        """야간 근무 시간대 계산"""
        night_start = self._clock_in.replace(hour=22, minute=0, second=0, microsecond=0)
        night_end = (self._clock_in + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        return (night_start, night_end)

class NormalAttendanceRecord(AttendanceRecord):
    """일반 근무 기록 (8시간 이하)"""
    def calculate_work_hours(self):
        self._work_hours = self._calculate_total_hours()

class OvertimeAttendanceRecord(AttendanceRecord):
    """연장 근무 기록 (8시간 초과)"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        self._work_hours = min(total_hours, 8)
        self._overtime_hours = max(0, total_hours - 8) * 1.5

class NightAttendanceRecord(AttendanceRecord):
    """야간 근무 기록"""
    def calculate_work_hours(self):
        night_start, night_end = self._get_night_period()
        total_hours = self._calculate_total_hours()
        
        # 야간 시간대에 포함된 시간 계산
        if self._clock_in >= night_start:
            night_hours = (min(self._clock_out, night_end) - self._clock_in).total_seconds() / 3600
        else:
            night_hours = (min(self._clock_out, night_end) - night_start).total_seconds() / 3600
            
        self._work_hours = total_hours
        self._night_hours = night_hours * 1.5

class ComplexAttendanceRecord(AttendanceRecord):
    """연장 + 야간 근무 기록"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        night_start, night_end = self._get_night_period()

        # 기본 근무 시간
        self._work_hours = min(total_hours, 8)
        
        # 연장 근무 시간
        overtime = max(0, total_hours - 8)
        self._overtime_hours = overtime * 1.5

        # 야간 근무 시간
        if self._clock_out >= night_start:
            night_hours = (self._clock_out - night_start).total_seconds() / 3600
            self._night_hours = night_hours * 0.5  # 야간 가산 0.5 추가 (연장 1.5 + 야간 0.5 = 2.0)

class HolidayAttendanceRecord(AttendanceRecord):
    """휴일 근무 기록"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        
        if total_hours <= 8:
            self._holiday_hours = total_hours * 1.5
        else:
            self._holiday_hours = 8 * 1.5  # 8시간까지는 1.5배
            self._overtime_hours = (total_hours - 8) * 2.0  # 8시간 초과는 2.0배

class HolidayNightAttendanceRecord(AttendanceRecord):
    """휴일 + 야간 근무 기록"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        night_start, night_end = self._get_night_period()

        # 8시간 이하
        if total_hours <= 8:
            self._holiday_hours = total_hours * 2.0  # 휴일(1.5) + 야간(0.5)
        else:
            self._holiday_hours = 8 * 2.0  # 8시간까지는 2.0배
            self._overtime_hours = (total_hours - 8) * 2.5  # 8시간 초과는 2.5배 (휴일 2.0 + 야간 0.5)

        # 야간 시간 계산 (야간 수당 계산을 위해)
        if self._clock_out >= night_start:
            night_hours = (self._clock_out - night_start).total_seconds() / 3600
            self._night_hours = night_hours 