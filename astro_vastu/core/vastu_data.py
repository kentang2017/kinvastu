"""Vastu Shastra 靜態方位資料。

提供八大方位與十六方位的完整 Vastu 資訊，支援從內建資料或
外部 JSON 檔案載入，方便未來更新傳統內容。

典型用法::

    from astro_vastu.core.vastu_data import get_directions_8, get_directions_16

    data_8 = get_directions_8()
    data_16 = get_directions_16()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from astro_vastu.exceptions import DataLoadError

# ---------- 內建預設資料路徑 ----------
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DEFAULT_JSON = _DATA_DIR / "vastu_directions.json"


def _load_json(path: Path | str | None = None) -> dict[str, Any]:
    """從 JSON 檔案載入 Vastu 方位資料。

    Args:
        path: JSON 檔案路徑。若為 ``None`` 則使用內建預設檔案。

    Returns:
        包含 ``directions_8`` 與 ``directions_sub8`` 鍵的字典。

    Raises:
        DataLoadError: 檔案不存在或 JSON 解析失敗。
    """
    target = Path(path) if path is not None else _DEFAULT_JSON
    if not target.exists():
        raise DataLoadError(f"Vastu 資料檔案不存在：{target}")
    try:
        with open(target, encoding="utf-8") as fh:
            return json.load(fh)  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError) as exc:
        raise DataLoadError(f"載入 Vastu 資料失敗：{exc}") from exc


# ---------- 快取 ----------
_cache: dict[str, Any] | None = None


def _ensure_loaded(path: Path | str | None = None) -> dict[str, Any]:
    """確保資料已載入並快取。"""
    global _cache
    if _cache is None:
        _cache = _load_json(path)
    return _cache


def get_directions_8(path: Path | str | None = None) -> list[dict[str, str]]:
    """取得八大方位 Vastu 資料。

    Args:
        path: 可選的自訂 JSON 路徑。

    Returns:
        八大方位資料列表（每個方位為一個字典）。
    """
    data = _ensure_loaded(path)
    return list(data["directions_8"])


def get_directions_sub8(path: Path | str | None = None) -> list[dict[str, str]]:
    """取得額外 8 個子方位資料（供 16 方位版本使用）。

    Args:
        path: 可選的自訂 JSON 路徑。

    Returns:
        8 個子方位資料列表。
    """
    data = _ensure_loaded(path)
    return list(data["directions_sub8"])


def get_directions_16(path: Path | str | None = None) -> list[dict[str, str]]:
    """取得完整 16 方位資料（主方位與子方位順時針穿插排列）。

    排列順序：E, ENE, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW, N, NNE, NE

    Args:
        path: 可選的自訂 JSON 路徑。

    Returns:
        16 方位資料列表。
    """
    main_8 = get_directions_8(path)
    sub_8 = get_directions_sub8(path)
    merged: list[dict[str, str]] = []
    for i in range(8):
        merged.append(main_8[i])
        merged.append(sub_8[i])
    return merged


def reload(path: Path | str | None = None) -> None:
    """清除快取並重新載入資料。

    Args:
        path: 可選的自訂 JSON 路徑。
    """
    global _cache
    _cache = None
    _ensure_loaded(path)
