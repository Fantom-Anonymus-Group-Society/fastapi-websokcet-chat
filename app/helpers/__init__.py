from datetime import datetime


def covert_datetime_to_string(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')
