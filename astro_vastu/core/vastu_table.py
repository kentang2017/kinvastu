"""Vastu 方位表格產生器。

提供 ``detailed_vastu_table()`` 函數，支援 8 / 16 方位輸出，
可輸出至 console 或回傳 pandas DataFrame。

典型用法::

    from astro_vastu.core.vastu_table import detailed_vastu_table

    detailed_vastu_table(directions=8)
    df = detailed_vastu_table(directions=16, output="dataframe")
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Optional

import pandas as pd
from tabulate import tabulate

from astro_vastu.config import settings
from astro_vastu.core.brahmasthan import BRAHMASTHAN_INFO
from astro_vastu.core.vastu_data import get_directions_8, get_directions_16

if TYPE_CHECKING:
    from pathlib import Path


def detailed_vastu_table(
    directions: int = 8,
    *,
    output: str = "console",
    wrap_width: Optional[int] = None,
    data_path: Optional[Path | str] = None,
) -> Optional[pd.DataFrame]:
    """產生超詳細的 Vastu Shastra 方位表格。

    Args:
        directions: 顯示 ``8`` 大方位或 ``16`` 方位版本（含子方位）。
            預設為 8。
        output: 輸出模式。
            ``"console"``（預設）：列印至終端。
            ``"dataframe"``：回傳 ``pandas.DataFrame``。
        wrap_width: 文字換行寬度。若為 ``None``，使用全域設定值。
        data_path: 可選的自訂 JSON 資料路徑。

    Returns:
        當 ``output="dataframe"`` 時回傳 ``pd.DataFrame``，否則回傳 ``None``。

    Raises:
        ValueError: 若 ``directions`` 不是 8 或 16。
    """
    if directions not in (8, 16):
        raise ValueError("directions 參數僅接受 8 或 16。")

    if directions == 16:
        data = get_directions_16(data_path)
    else:
        data = get_directions_8(data_path)

    df = pd.DataFrame(data)

    # 輸出 DataFrame 模式：直接回傳（不做文字換行）
    if output == "dataframe":
        return df

    # Console 模式：加上換行美化
    _wrap = wrap_width if wrap_width is not None else settings.wrap_width
    display_df = df.copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda x: "\n".join(textwrap.wrap(str(x), _wrap))
        )

    title = f"🕉️  Vastu Shastra {'十六' if directions == 16 else '八大'}方位詳解表"
    separator = "═" * 60
    print(f"\n{separator}")
    print(f"  {title}")
    print(f"{separator}\n")

    print(
        tabulate(
            display_df,
            headers="keys",
            tablefmt=settings.table_format,
            showindex=False,
            stralign="left",
        )
    )

    # 附加中央 Brahmasthan 說明
    print(f"\n{BRAHMASTHAN_INFO}")
    return None
