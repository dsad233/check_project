from enum import Enum
from datetime import datetime, time, timedelta
from typing import Optional

class AttendanceType(Enum):
    NORMAL = "NORMAL"                    # 평일 근무
    NORMAL_OVERTIME = "NORMAL_OVERTIME"  # 평일 근무 + 연장
    NORMAL_NIGHT = "NORMAL_NIGHT"        # 평일 근무 + 야간
    NORMAL_OVERTIME_NIGHT = "NORMAL_OVERTIME_NIGHT"  # 평일 근무 + 연장 + 야간
    HOLIDAY = "HOLIDAY"                  # 휴일 근무
    HOLIDAY_NIGHT = "HOLIDAY_NIGHT"      # 휴일 근무 + 야간
    NIGHT = "NIGHT"                      # 야간 전용

class AttendanceClassifier:
    NIGHT_HOUR_START = 22    # 오후 10시
    NIGHT_HOUR_END = 6      # 오전 6시
    REGULAR_HOURS = 8       # 정규 근무시간

    # TODO: 하나의 출퇴근 기록으로 여러 근무 타입을 반환하도록 변경
    # -> 결국 각 수당을 구해야하기 때문, 하나로 뭉쳐놓으면 다시 계산해야함
    # -> 기본은 기본, 야간 수당은 야간끼리, 초과는 초과끼리, 휴일은 휴일끼리 묶어놔야 주당 최대 시간을 넘을 때 처리가 가능
    def classify(self, clock_in: datetime, clock_out: datetime, is_holiday: bool) -> AttendanceType:
        # 기본 판별 요소들
        work_hours = (clock_out - clock_in).total_seconds() / 3600
        is_overtime = work_hours > self.REGULAR_HOURS
        
        # 야간 관련 판별
        is_full_night = self._is_full_night_shift(clock_in, clock_out)
        clock_out_in_night = self._is_time_in_night_hours(clock_out)
        has_any_night_hours = self._has_any_night_hours(clock_in, clock_out)

        # 1. 전체 근무가 야간인 경우
        if is_full_night:
            return AttendanceType.NIGHT

        # 2. 휴일 근무인 경우
        if is_holiday:
            return AttendanceType.HOLIDAY_NIGHT if has_any_night_hours else AttendanceType.HOLIDAY

        # 3. 퇴근이 야간이고 초과근무인 경우
        if clock_out_in_night and is_overtime:
            return AttendanceType.NORMAL_OVERTIME_NIGHT

        # 4. 퇴근이 야간인 경우
        if clock_out_in_night:
            return AttendanceType.NORMAL_NIGHT

        # 5. 초과근무인 경우
        if is_overtime:
            return AttendanceType.NORMAL_OVERTIME

        # 6. 일반 근무
        return AttendanceType.NORMAL

    def _get_night_period(self, base_date: datetime) -> tuple[datetime, datetime]:
        """해당 날짜의 야간 시작과 종료 시각을 반환"""
        night_start = base_date.replace(hour=self.NIGHT_HOUR_START, minute=0, second=0, microsecond=0)
        night_end = (base_date + timedelta(days=1)).replace(hour=self.NIGHT_HOUR_END, minute=0, second=0, microsecond=0)
        return night_start, night_end

    def _is_time_in_night_hours(self, check_time: datetime) -> bool:
        """특정 시각이 야간 시간대에 포함되는지 확인"""
        night_start, night_end = self._get_night_period(check_time)
        return night_start <= check_time < night_end

    def _has_any_night_hours(self, clock_in: datetime, clock_out: datetime) -> bool:
        """출퇴근 시각 중 하나라도 야간 시간대에 포함되는지 확인"""
        return self._is_time_in_night_hours(clock_in) or \
               self._is_time_in_night_hours(clock_out)

    def _is_full_night_shift(self, clock_in: datetime, clock_out: datetime) -> bool:
        """전체 근무시간이 야간 시간대에 포함되는지 확인"""
        return self._is_time_in_night_hours(clock_in) and \
               self._is_time_in_night_hours(clock_out) 