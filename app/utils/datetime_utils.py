from datetime import datetime, date, time

class DatetimeUtil:
    @staticmethod
    def datetime_to_str(dt: datetime) -> str:
        """Convert datetime to string in yyyy-mm-dd HH:MM:SS format."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def date_to_str(d: date) -> str:
        """Convert date to string in yyyy-mm-dd format."""
        return d.strftime("%Y-%m-%d")

    @staticmethod
    def time_to_str(t: time) -> str:
        """Convert time to string in HH:MM:SS format."""
        return t.strftime("%H:%M:%S")

    @staticmethod
    def str_to_datetime(s: str) -> datetime:
        """Convert string in yyyy-mm-dd HH:MM:SS format to datetime."""
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def str_to_date(s: str) -> date:
        """Convert string in yyyy-mm-dd format to date."""
        return datetime.strptime(s, "%Y-%m-%d").date()

    @staticmethod
    def str_to_time(s: str) -> time:
        """Convert string in HH:MM:SS format to time."""
        return datetime.strptime(s, "%H:%M:%S").time()