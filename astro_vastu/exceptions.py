"""自訂例外類別。

提供 Astro-Vastu 專案中使用的所有自訂例外，
讓呼叫端可以精確捕捉並處理不同類型的錯誤。
"""

from __future__ import annotations


class AstroVastuError(Exception):
    """Astro-Vastu 專案的基底例外。"""


class InvalidDateError(AstroVastuError):
    """出生日期格式或範圍無效。"""


class InvalidTimeError(AstroVastuError):
    """出生時間格式或範圍無效。"""


class InvalidCoordinateError(AstroVastuError):
    """經緯度數值超出合法範圍。"""


class AstroCalculationError(AstroVastuError):
    """占星計算過程發生錯誤。"""


class DataLoadError(AstroVastuError):
    """資料檔案載入失敗。"""
