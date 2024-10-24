from sqlalchemy.types import TypeDecorator, String

class CustomEnumType(TypeDecorator):
    impl = String

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enumtype):
            # Enum의 value(국문)를 저장
            return value.value
        elif isinstance(value, str):
            return value
        return None

    def process_result_value(self, value, dialect):
        if value:
            # Enum의 value를 통해 영문으로 변환
            return self.enumtype(value)
        return None
