from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from dataclasses import dataclass

@dataclass
class BreakTime:
    start: datetime
    end: datetime
    
    @property
    def duration(self) -> timedelta:
        return self.end - self.start
    
    @property
    def hours(self) -> float:
        return self.duration.total_seconds() / 3600

class AttendanceRecord(ABC):
    def __init__(self, clock_in: datetime, clock_out: datetime, is_holiday: bool, break_times: list[BreakTime] = None):
        self._clock_in = clock_in
        self._clock_out = clock_out
        self._break_times = break_times or []
        self._work_hours = 0
        self._calibrated_work_hours = 0
        self.calculate_work_hours()  # 초기화 시 바로 계산
        
    @property
    def total_break_hours(self) -> float:
        """총 휴게시간을 시간 단위로 반환"""
        return sum(break_time.hours for break_time in self._break_times)
        
    def _calculate_total_hours(self) -> float:
        """총 근무 시간 계산 (휴게시간 제외)"""
        total_seconds = (self._clock_out - self._clock_in).total_seconds()
        break_seconds = sum(break_time.duration.total_seconds() for break_time in self._break_times)
        return (total_seconds - break_seconds) / 3600

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
        """실제 근무 시간과 보정된 근무 시간을 계산"""
        pass

    def get_calibrated_work_hours(self) -> float:
        """보정된 근무 시간을 반환"""
        return self._calibrated_work_hours

    def get_clock_in(self) -> datetime:
        return self._clock_in

    def get_clock_out(self) -> datetime:
        return self._clock_out

    def get_work_hours(self) -> float:
        return self._work_hours

    def _get_night_period(self) -> tuple[datetime, datetime]:
        """야간 근무 시간대 계산"""
        night_start = self._clock_in.replace(hour=22, minute=0, second=0, microsecond=0)
        night_end = (self._clock_in + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        return (night_start, night_end)

class NormalAttendanceRecord(AttendanceRecord):
    """일반 근무 기록"""
    def calculate_work_hours(self):
        self._work_hours = self._calculate_total_hours()
        self._calibrated_work_hours = self._work_hours
        
    def get_calibrated_work_hours(self) -> float:
        return self._calibrated_work_hours

class OvertimeAttendanceRecord(AttendanceRecord):
    """연장 근무 기록"""
    def calculate_work_hours(self):
        self._work_hours = self._calculate_total_hours()
        self._calibrated_work_hours = self._work_hours * 1.5  # 연장 근무는 1.5배
        
    def get_calibrated_work_hours(self) -> float:
        return self._calibrated_work_hours

class NightAttendanceRecord(AttendanceRecord):
    """야간 근무 기록"""
    def calculate_work_hours(self):
        self._work_hours = self._calculate_total_hours()
        self._calibrated_work_hours = self._work_hours * 1.5  # 야간 근무는 1.5배
        
    def get_calibrated_work_hours(self) -> float:
        return self._calibrated_work_hours

class HolidayAttendanceRecord(AttendanceRecord):
    """휴일 근무 기록"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        self._work_hours = total_hours
        
        # 8시간 이하는 1.5배, 초과분은 2.0배
        if total_hours <= 8:
            self._calibrated_work_hours = total_hours * 1.5
        else:
            self._calibrated_work_hours = (8 * 1.5) + ((total_hours - 8) * 2.0)

class HolidayNightAttendanceRecord(AttendanceRecord):
    """휴일 야간 근무 기록"""
    def calculate_work_hours(self):
        total_hours = self._calculate_total_hours()
        self._work_hours = total_hours
        
        # 8시간 이하는 2.0배, 초과분은 2.5배 (야간 0.5 추가)
        if total_hours <= 8:
            self._calibrated_work_hours = total_hours * 2.0
        else:
            self._calibrated_work_hours = (8 * 2.0) + ((total_hours - 8) * 2.5)