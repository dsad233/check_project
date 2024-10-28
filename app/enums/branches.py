from enum import Enum

class RestDayType(str, Enum):
    """
    휴무일 테이블에서 휴무일 구분을 위한 Enum 
    """
    NATIONAL_HOLIDAY = "공휴일" 
    WEEKEND = "주말"

class LeaveResetOption(str, Enum):
    """
    기본-연차 세팅 시, 연차 이월 정책 구분을 위한 Enum
    """
    RESET = "초기화"
    ROLLOVER = "다음해로 이월"

class LeaveGrantOption(str, Enum):
    """
    기본-연차 세팅 시, 연차 자동 부여 정책 구분을 위한 Enum
    """
    SAME_YEAR_GRANT = "당해년도 일괄 부여"
    ONE_PER_MONTH = "매 월 1개씩 부여"

class DecimalRoundingPolicy(str, Enum):
    """
    기본-연차 세팅 시, 연차의 소숫점 관리 정책 구분을 위한 Enum
    """

    ROUND_UP_0_5 = "0.5 기준 올림"
    TRUNCATE = "절삭"
    ROUND_UP = "올림"
    ROUND = "반올림"

class TimeUnit(str, Enum):
    """
    기본-연차 세팅 시, 연차 자동 부여 정책 단위 구분을 위한 Enum
    """
    
    MONTH = "월"
    DAY = "일"
