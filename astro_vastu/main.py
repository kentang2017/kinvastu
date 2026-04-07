"""示範入口 — 保留原 ``main()`` 功能。

可直接執行此模組來展示 Vastu 表格與個人化推薦範例::

    python -m astro_vastu.main
"""

from __future__ import annotations

from astro_vastu.core.vastu_table import detailed_vastu_table
from astro_vastu.personalized import personalized_astro_vastu


def main() -> None:
    """主程式入口：展示 Vastu 表格與個人化推薦範例。"""
    print("\n" + "★" * 64)
    print("  歡迎使用 astro_vastu — 超級進階 Astro-Vastu 模組 v2.0.0")
    print("★" * 64)

    # --- 1. 顯示八大方位 Vastu 表格 ---
    print("\n\n【第一部分】八大方位 Vastu Shastra 詳解表\n")
    detailed_vastu_table(directions=8)

    # --- 2. 個人化 Astro-Vastu 推薦範例 ---
    print("\n\n【第二部分】個人化 Astro-Vastu 命盤推薦範例\n")
    personalized_astro_vastu(
        name="王小明",
        birth_date="1990-05-15",
        birth_time="08:30",
        birth_place="Taipei",
        latitude=25.033,
        longitude=121.565,
    )


if __name__ == "__main__":
    main()
