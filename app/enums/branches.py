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

class BranchHistoryType(str, Enum):
    """
    브랜치 히스토리 타입 구분을 위한 Enum
    """
    AUTO_ANNUAL_LEAVE_GRANT = "AUTO_ANNUAL_LEAVE_GRANT"


class AnnualLeaveDaysByYear(Enum):
   YEAR_1 = (1, 15)   # 1년 근속: 15일
   YEAR_2 = (2, 15)   # 2년 근속: 15일
   YEAR_3 = (3, 16)   # 3년 근속: 16일
   YEAR_4 = (4, 16)   # 4년 근속: 16일
   YEAR_5 = (5, 17)   # 5년 근속: 17일
   YEAR_6 = (6, 17)   # 6년 근속: 17일
   YEAR_7 = (7, 18)   # 7년 근속: 18일
   YEAR_8 = (8, 18)   # 8년 근속: 18일
   YEAR_9 = (9, 19)   # 9년 근속: 19일
   YEAR_10 = (10, 19) # 10년 근속: 19일
   YEAR_11 = (11, 20) # 11년 근속: 20일
   YEAR_12 = (12, 20) # 12년 근속: 20일
   YEAR_13 = (13, 21) # 13년 근속: 21일
   YEAR_14 = (14, 21) # 14년 근속: 21일
   YEAR_15 = (15, 22) # 15년 이상: 22일
   YEAR_16 = (16, 22) # 16년 이상: 22일
   YEAR_17 = (17, 23) # 17년 이상: 23일
   YEAR_18 = (18, 23) # 18년 이상: 23일
   YEAR_19 = (19, 24) # 19년 이상: 24일
   YEAR_20 = (20, 24) # 20년 이상: 24일
   YEAR_21 = (21, 25) # 21년 이상: 25일

   @classmethod
   def get_leave_days(cls, request: int) -> int:
       """근속 년수에 따른 연차 일수 반환"""
       if request < 1:
           return 0
       
       if request >= 21:
           return cls.YEAR_21.value[1]
           
       for enum in cls:
           if enum.value[0] == request:
               return enum.value[1]
               
       return cls.YEAR_1.value[1]  # 기본값

