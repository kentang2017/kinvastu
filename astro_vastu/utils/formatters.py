"""格式化工具 — 表格、文字換行等。

提供 Astro-Vastu 專案通用的格式化功能。
"""

from __future__ import annotations

import pandas as pd
from tabulate import tabulate

from astro_vastu.config import settings


def build_planet_table(planet_data: list[dict[str, str]]) -> str:
    """將行星資料列表格式化為美觀表格字串。

    Args:
        planet_data: 行星資訊字典列表，每個字典應包含
            ``行星``、``所在星座``、``Vastu 方位``、``力量`` 等鍵。

    Returns:
        使用 tabulate 格式化的表格字串。
    """
    df = pd.DataFrame(planet_data)
    return tabulate(
        df,
        headers="keys",
        tablefmt=settings.table_format,
        showindex=False,
        stralign="left",
    )


def build_recommendation_table(details: dict[str, str]) -> str:
    """將 Vastu 建議字典格式化為表格字串。

    Args:
        details: 建議項目與說明的字典。

    Returns:
        格式化的表格字串。
    """
    data = [{"建議項目": key, "詳細說明": value} for key, value in details.items()]
    df = pd.DataFrame(data)
    return tabulate(
        df,
        headers="keys",
        tablefmt=settings.table_format,
        showindex=False,
        stralign="left",
    )
