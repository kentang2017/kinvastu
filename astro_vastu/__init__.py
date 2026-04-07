"""
astro_vastu — 超級進階 Astro-Vastu 模組 v2.0.0
================================================

結合 Vastu Shastra（建築風水）與 Vedic Jyotish（吠陀占星），
提供八大方位 / 十六方位的 Vastu 詳解表格，
以及根據個人命盤的個人化居家風水建議。

📦 安裝依賴::

    pip install pandas tabulate
    pip install vedastro        # 可選：精確吠陀占星計算

📖 快速開始::

    from astro_vastu import detailed_vastu_table, personalized_astro_vastu

    # 顯示八方位 Vastu 表格
    detailed_vastu_table(directions=8)

    # 個人化 Astro-Vastu 推薦
    personalized_astro_vastu(
        name="王小明",
        birth_date="1990-05-15",
        birth_time="08:30",
        birth_place="臺北",
        latitude=25.033,
        longitude=121.565,
    )

📚 參考經典：
    - Mayamata（摩耶論）
    - Manasara（摩那薩羅）
    - Brihat Samhita（大合集論）
    - Vastu Ratnakara（Vastu 寶鑑）
    - Brihat Parashara Hora Shastra（帕拉夏拉大時論）
"""

from __future__ import annotations

__version__ = "2.0.0"
__author__ = "KinVastu 團隊"
__license__ = "MIT"

# ---------- 相容性重新匯出 ----------
# 讓 from astro_vastu import detailed_vastu_table 等舊有呼叫方式繼續有效
from astro_vastu.core.vastu_table import detailed_vastu_table  # noqa: F401
from astro_vastu.personalized import personalized_astro_vastu  # noqa: F401
from astro_vastu.main import main  # noqa: F401

__all__ = [
    "__version__",
    "detailed_vastu_table",
    "personalized_astro_vastu",
    "main",
]
