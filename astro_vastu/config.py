"""專案層級設定。

集中管理 Astro-Vastu 專案的全域設定值，
包含表格寬度、預設方位數、語言等。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AppSettings:
    """應用程式全域設定。

    Attributes:
        default_directions: 預設方位數（8 或 16）。
        wrap_width: 表格欄位文字換行寬度。
        table_format: tabulate 使用的表格格式。
        language: 使用者介面語言（目前僅支援 ``zh-TW``）。
        use_astro: 是否啟用吠陀占星模組。
        fallback_notice: 當使用 fallback 時顯示的提示文字。
    """

    default_directions: int = 8
    wrap_width: int = 30
    table_format: str = "fancy_grid"
    language: str = "zh-TW"
    use_astro: bool = True
    fallback_notice: str = (
        "⚠️  簡化估計模式 — 建議安裝占星庫（pip install pyswisseph）取得精確結果"
    )


# 全域預設設定實例
settings = AppSettings()
