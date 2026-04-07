"""時間與時區處理工具。

使用 ``zoneinfo``（Python 3.9+）處理精確時區與夏令時間，
並提供 VedAstro 格式化、UTC 偏移估算等功能。
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo, available_timezones

from astro_vastu.exceptions import InvalidDateError, InvalidTimeError


def validate_date(date_str: str) -> datetime:
    """驗證並解析出生日期。

    Args:
        date_str: 日期字串，格式 ``YYYY-MM-DD``。

    Returns:
        解析後的 ``datetime`` 物件。

    Raises:
        InvalidDateError: 格式或範圍無效。
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise InvalidDateError(
            f"日期格式無效：'{date_str}'。請使用 YYYY-MM-DD 格式。"
        )
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise InvalidDateError(f"日期無效：'{date_str}'。{exc}") from exc

    if dt.year < 1800 or dt.year > 2200:
        raise InvalidDateError(
            f"年份超出範圍：{dt.year}。請輸入 1800–2200 之間的年份。"
        )
    return dt


def validate_time(time_str: str) -> tuple[int, int]:
    """驗證並解析出生時間。

    Args:
        time_str: 時間字串，格式 ``HH:MM``（24 小時制）。

    Returns:
        ``(hour, minute)`` 整數元組。

    Raises:
        InvalidTimeError: 格式或範圍無效。
    """
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        raise InvalidTimeError(
            f"時間格式無效：'{time_str}'。請使用 HH:MM（24 小時制）格式。"
        )
    parts = time_str.split(":")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23):
        raise InvalidTimeError(f"小時超出範圍：{hour}（需 0–23）。")
    if not (0 <= minute <= 59):
        raise InvalidTimeError(f"分鐘超出範圍：{minute}（需 0–59）。")
    return hour, minute


def validate_coordinates(latitude: float, longitude: float) -> None:
    """驗證經緯度是否在合法範圍。

    Args:
        latitude: 緯度（-90 至 90）。
        longitude: 經度（-180 至 180）。

    Raises:
        InvalidCoordinateError: 超出合法範圍。
    """
    from astro_vastu.exceptions import InvalidCoordinateError

    if not (-90 <= latitude <= 90):
        raise InvalidCoordinateError(
            f"緯度超出範圍：{latitude}（需 -90 至 90）。"
        )
    if not (-180 <= longitude <= 180):
        raise InvalidCoordinateError(
            f"經度超出範圍：{longitude}（需 -180 至 180）。"
        )


def longitude_to_utc_offset(longitude: float) -> str:
    """根據經度估算 UTC 偏移量。

    每 15° 經度對應 1 小時。此為簡化估算，
    實際時區可能因國家政策而異。

    Args:
        longitude: 經度（東經為正，西經為負）。

    Returns:
        UTC 偏移量字串，如 ``"+08:00"``。
    """
    offset_hours = round(longitude / 15)
    sign = "+" if offset_hours >= 0 else "-"
    abs_hours = abs(offset_hours)
    return f"{sign}{abs_hours:02d}:00"


def resolve_utc_offset(
    longitude: float,
    utc_offset: Optional[str] = None,
    tz_name: Optional[str] = None,
    dt: Optional[datetime] = None,
) -> str:
    """解析 UTC 偏移量，優先使用 IANA 時區名稱。

    優先順序：
    1. 明確提供的 ``utc_offset``。
    2. 使用 ``tz_name``（IANA 時區）在指定日期計算精確偏移。
    3. 根據經度簡化估算。

    Args:
        longitude: 經度。
        utc_offset: 直接指定的 UTC 偏移量。
        tz_name: IANA 時區名稱（如 ``"Asia/Taipei"``）。
        dt: 日期時間物件，用於計算夏令時。

    Returns:
        UTC 偏移量字串。
    """
    if utc_offset is not None:
        return utc_offset

    if tz_name is not None and tz_name in available_timezones():
        ref_dt = dt or datetime.now(tz=timezone.utc)
        tz = ZoneInfo(tz_name)
        aware = ref_dt.replace(tzinfo=tz) if ref_dt.tzinfo is None else ref_dt.astimezone(tz)
        offset = aware.utcoffset()
        if offset is not None:
            total_seconds = int(offset.total_seconds())
            sign = "+" if total_seconds >= 0 else "-"
            abs_seconds = abs(total_seconds)
            hours = abs_seconds // 3600
            minutes = (abs_seconds % 3600) // 60
            return f"{sign}{hours:02d}:{minutes:02d}"

    return longitude_to_utc_offset(longitude)


def format_vedastro_time(
    birth_date: str, birth_time: str, utc_offset: str
) -> str:
    """格式化為 VedAstro 接受的時間字串。

    VedAstro Time 格式：``"HH:MM DD/MM/YYYY +HH:MM"``

    Args:
        birth_date: 出生日期，格式 ``YYYY-MM-DD``。
        birth_time: 出生時間，格式 ``HH:MM``。
        utc_offset: UTC 偏移量，例如 ``"+08:00"``。

    Returns:
        VedAstro 格式的時間字串。
    """
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    return f"{dt.strftime('%H:%M')} {dt.strftime('%d/%m/%Y')} {utc_offset}"
