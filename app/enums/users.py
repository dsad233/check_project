from enum import Enum

class Role(str, Enum):
    """
    전체 역할 구성용 Enum
    """

    MSO = "MSO 최고권한"
    SUPER_ADMIN = "최고관리자"
    INTEGRATED_ADMIN = "통합관리자"
    ADMIN = "관리자"
    EMPLOYEE = "사원"
    RESIGNED = "퇴사자"
    ON_LEAVE = "휴직자"


class MenuPermissions(str, Enum):
    """
    전체 권한 구성용 Enum
    """
    
    PT_MANAGEMENT = "P.T관리"
    CONTRACT_MANAGEMENT_WITH_PT = "계약관리(P.T)포함"
    LEAVE_MANAGEMENT = "휴무관리"
    OT_MANAGEMENT = "O.T관리"
    HR_MANAGEMENT = "인사관리"
    WORK_MANAGEMENT = "근로관리"
    PAYROLL_SETTLEMENT = "급여정산"
    DOCUMENT_SETTINGS_MANAGEMENT = "문서설정관리"
    LEAVE_OF_ABSENCE_MANAGEMENT = "휴직관리"
    ATTENDANCE_RECORD_MANAGEMENT = "출퇴근기록관리"


class Gender(str, Enum):
    """
    성별 구분용 Enum
    """

    MALE = "남자"
    FEMALE = "여자"


class OverTimeHours(str, Enum):
    """
    초과 근무 기준 관리용 Enum
    """

    THIRTY_MINUTES = "30"
    SIXTY_MINUTES = "60"  
    NINETY_MINUTES = "90"
    ONE_HUNDRED_TWENTY_MINUTES = "120"


class Status(str, Enum):
    """
    상태 구성용 영문 Enum
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# TODO : 영문 Status, 국문 Status 중 택 1하여, 하나로 통합 관리
class StatusKor(str, Enum):
    """
    상태 구성용 국문 Enum
    """
    
    PENDING = "확인중" 
    APPROVED = "승인"
    REJECTED = "반려"


class Weekday(str, Enum):
    """
    평일 구성용 Enum
    """

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "satruday"
    SUNDAY = "sunnday"

