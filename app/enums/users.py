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
    TEMPORARY = "임시생성"


class EmploymentStatus(str, Enum):
    """
    전체 근무 상태 구성용 Enum
    """
    PERMANENT = "정규직"
    TEMPORARY = "계약직"


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
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TimeOffType(str, Enum):
    """
    휴직 유형 구성용 Enum
    """

    PARENTAL = "육아"
    INDUSTRIAL_ACCIDENT = "산재"


class SchoolType(str, Enum):
    """학교 유형"""
    ELEMENTARY = "초등학교"
    MIDDLE = "중학교"
    HIGH = "고등학교"
    UNIVERSITY = "대학교"
    GRADUATE = "대학원"


class GraduationType(str, Enum):
    """졸업 상태"""
    GRADUATED = "졸업"
    EXPECTED = "졸업예정"
    IN_PROGRESS = "재학중"
    LEAVE = "휴학"
    DROPOUT = "중퇴"


class CareerContractType(str, Enum):
    """
    계약 유형
    """
    PERMANENT = "정규직"
    CONTRACT = "계약직"
    INTERN = "인턴"
    PART_TIME = "파트타임"

class UserStatus(str, Enum):
    """
    사용자 상태
    """
    ALL = "전체"
    ACTIVE = "재직자"
    RESIGNED = "퇴사자"
    ON_LEAVE = "휴직자"
    DELETED = "삭제회원"