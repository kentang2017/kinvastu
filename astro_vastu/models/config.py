"""資料模型 — 配置類別與出生資料結構。

使用 ``dataclass`` 定義出生資料與計算配置的結構化模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BirthData:
    """出生資料模型。

    Attributes:
        name: 姓名。
        birth_date: 出生日期，格式 ``YYYY-MM-DD``。
        birth_time: 出生時間，格式 ``HH:MM``。
        birth_place: 出生地點名稱。
        latitude: 出生地緯度。
        longitude: 出生地經度。
        utc_offset: UTC 偏移量（如 ``"+08:00"``）。
        timezone: IANA 時區名稱（如 ``"Asia/Taipei"``）。
    """

    name: str
    birth_date: str
    birth_time: str
    birth_place: str
    latitude: float
    longitude: float
    utc_offset: Optional[str] = None
    timezone: Optional[str] = None


@dataclass
class VastuReportConfig:
    """Vastu 報告配置。

    Attributes:
        use_astro: 是否使用占星計算。
        directions: 方位數（8 或 16）。
        show_brahmasthan: 是否顯示 Brahmasthan 說明。
        mask_sensitive_data: 是否遮蔽敏感個人資料。
    """

    use_astro: bool = True
    directions: int = 8
    show_brahmasthan: bool = True
    mask_sensitive_data: bool = True
