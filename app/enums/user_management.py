from enum import Enum

class Status(str, Enum):
    """
    상태 구성용 영문 Enum
    """

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

class DocumentSendStatus(str, Enum):
    """
    문서 전달 상태 구성용 영문 Enum
    """

    PENDING = "PENDING"
    APPROVE = "APPROVE"
    REJECT = "REJECT"

class ContractStatus(str, Enum):
    """
    계약서 상태 구성용 영문 Enum
    """


    PENDING = "PENDING"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CANCEL = "CANCEL"

class ContractType(str, Enum):
    """

    """

    WORK = "WORK"
    SALARY = "SALARY"
    PART_TIME = "PART_TIME"
