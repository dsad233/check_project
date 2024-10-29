from enum import Enum

class PartAutoAnnualLeaveGrant(str, Enum):
    """
    회원 관리 시, 자동 연차 부여 기준 관리를 위한 Enum
    """
    MANUAL_GRANT = "수동부여"
    ACCOUNTING_BASED_GRANT = "회계기준 부여"
    ENTRY_DATE_BASED_GRANT = "입사일 기준 부여"
    CONDITIONAL_GRANT = "조건별 부여"
