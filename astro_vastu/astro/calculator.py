"""占星計算器 — 封裝 pyswisseph 與 Fallback 邏輯。

使用 pyswisseph 以恆星黃道 (sidereal zodiac) 搭配 Lahiri 歲差
計算精確吠陀占星命盤。若 pyswisseph 未安裝，
自動切換至簡化推估方法並清楚提示使用者。

參考：https://github.com/kentang2017/kinastro

典型用法::

    from astro_vastu.astro.calculator import AstroCalculator

    calc = AstroCalculator(use_astro=True)
    result = calc.compute(
        birth_date="1990-05-15",
        birth_time="08:30",
        birth_place="臺北",
        latitude=25.033,
        longitude=121.565,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from astro_vastu.astro.mappings import (
    MOON_SIGNS_BY_MONTH,
    PLANET_DIRECTION,
    PLANET_NAMES_EN,
    PLANET_ZH,
    ZODIAC_ZH,
)
from astro_vastu.exceptions import AstroCalculationError
from astro_vastu.utils.time_utils import longitude_to_utc_offset

# ---------- pyswisseph 動態匯入 ----------
_SWE_AVAILABLE: bool = False
try:
    import swisseph as swe  # type: ignore[import-untyped]

    _SWE_AVAILABLE = True
except ImportError:
    pass

# ---------- 恆星黃道十二星座 (英文名稱，對應 ZODIAC_ZH 鍵) ----------
_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ---------- 九曜 pyswisseph 對應 ----------
_SWE_PLANETS: dict[str, int] = {}
if _SWE_AVAILABLE:
    _SWE_PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
    }


def is_swe_available() -> bool:
    """檢查 pyswisseph 庫是否可用。"""
    return _SWE_AVAILABLE


@dataclass
class AstroResult:
    """占星計算結果。

    Attributes:
        lagna_sign: 上升星座英文名稱。
        moon_sign: 月亮星座英文名稱。
        planet_info: 九曜行星位置資訊列表。
        used_vedastro: 是否使用了精確占星計算（pyswisseph）。
        messages: 計算過程中的提示訊息。
    """

    lagna_sign: str = ""
    moon_sign: str = ""
    planet_info: list[dict[str, str]] = field(default_factory=list)
    used_vedastro: bool = False
    messages: list[str] = field(default_factory=list)


class AstroCalculator:
    """占星計算器，封裝 pyswisseph 與 Fallback 邏輯。

    Args:
        use_astro: 是否啟用占星計算。若為 ``False``，直接使用 Fallback。
    """

    def __init__(self, use_astro: bool = True) -> None:
        self._use_astro = use_astro

    def compute(
        self,
        birth_date: str,
        birth_time: str,
        birth_place: str,
        latitude: float,
        longitude: float,
        utc_offset: Optional[str] = None,
    ) -> AstroResult:
        """執行占星計算。

        Args:
            birth_date: 出生日期，格式 ``YYYY-MM-DD``。
            birth_time: 出生時間，格式 ``HH:MM``。
            birth_place: 出生地點名稱。
            latitude: 出生地緯度。
            longitude: 出生地經度。
            utc_offset: UTC 偏移量（如 ``"+08:00"``）。若未提供，自動估算。

        Returns:
            :class:`AstroResult` 包含計算結果與狀態訊息。
        """
        if utc_offset is None:
            utc_offset = longitude_to_utc_offset(longitude)

        result = AstroResult()

        if self._use_astro and _SWE_AVAILABLE:
            try:
                self._compute_swe(
                    result, birth_date, birth_time,
                    latitude, longitude, utc_offset,
                )
                return result
            except Exception as exc:
                result.messages.append(
                    f"⚠️  pyswisseph 計算失敗：{exc}\n"
                    "      將使用簡化推估方法作為替代。"
                )

        if self._use_astro and not _SWE_AVAILABLE:
            result.messages.append(
                "⚠️  pyswisseph 庫未安裝。請執行以下命令安裝：\n"
                "      pip install pyswisseph\n"
                "      安裝後即可獲得精確的吠陀占星計算。"
            )
            result.messages.append(
                "📌 目前使用簡化推估方法（僅供參考，精度有限）。"
            )

        self._compute_fallback(result, birth_date, birth_time)
        return result

    # ------------------------------------------------------------------
    # pyswisseph 精確計算（參考 kinastro 印度占星模組）
    # ------------------------------------------------------------------
    def _compute_swe(
        self,
        result: AstroResult,
        birth_date: str,
        birth_time: str,
        latitude: float,
        longitude: float,
        utc_offset: str,
    ) -> None:
        """使用 pyswisseph 進行精確吠陀計算（Lahiri Ayanamsa）。"""
        swe.set_ephe_path("")
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # 解析日期時間
        year, month, day = (int(x) for x in birth_date.split("-"))
        hour, minute = (int(x) for x in birth_time.split(":"))

        # 解析 UTC 偏移
        offset_sign = 1 if utc_offset.startswith("+") else -1
        offset_parts = utc_offset.lstrip("+-").split(":")
        tz_hours = offset_sign * (
            int(offset_parts[0]) + int(offset_parts[1]) / 60.0
        )

        # 計算 Julian Day（轉為 UTC）
        decimal_hour = hour + minute / 60.0 - tz_hours
        jd = swe.julday(year, month, day, decimal_hour)

        # 計算恆星黃道宮位（Placidus 宮位制）
        cusps, ascmc = swe.houses_ex(
            jd, latitude, longitude, b"P", swe.FLG_SIDEREAL,
        )
        ascendant = ascmc[0] % 360.0

        # Lagna（上升星座）
        result.lagna_sign = _SIGNS[int(ascendant / 30.0) % 12]

        # 九曜行星位置
        for p_name in PLANET_NAMES_EN:
            if p_name in _SWE_PLANETS:
                res, _ = swe.calc_ut(
                    jd, _SWE_PLANETS[p_name], swe.FLG_SIDEREAL,
                )
                lon = res[0] % 360.0
                sign = _SIGNS[int(lon / 30.0) % 12]
            elif p_name == "Rahu":
                res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
                lon = res[0] % 360.0
                sign = _SIGNS[int(lon / 30.0) % 12]
            elif p_name == "Ketu":
                res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
                lon = (res[0] + 180.0) % 360.0
                sign = _SIGNS[int(lon / 30.0) % 12]
            else:
                sign = "—"

            # 取得月亮星座
            if p_name == "Moon":
                result.moon_sign = sign

            result.planet_info.append({
                "行星": PLANET_ZH.get(p_name, p_name),
                "所在星座": ZODIAC_ZH.get(sign, sign),
                "Vastu 方位": PLANET_DIRECTION.get(p_name, "—"),
                "力量": "—",
            })

        result.used_vedastro = True
        result.messages.append(
            "✅ 已使用 pyswisseph 進行精確吠陀計算（Lahiri Ayanamsa）。"
        )

    # ------------------------------------------------------------------
    # Fallback 簡化推估
    # ------------------------------------------------------------------
    def _compute_fallback(
        self, result: AstroResult, birth_date: str, birth_time: str
    ) -> None:
        """使用簡化方法推估命盤（Fallback）。"""
        result.lagna_sign = self._fallback_lagna(birth_time)

        month = int(birth_date.split("-")[1])
        result.moon_sign = MOON_SIGNS_BY_MONTH[(month - 1) % 12]

        for p_name in PLANET_NAMES_EN:
            result.planet_info.append({
                "行星": PLANET_ZH.get(p_name, p_name),
                "所在星座": "（需 pyswisseph 精確計算）",
                "Vastu 方位": PLANET_DIRECTION.get(p_name, "—"),
                "力量": "—",
            })

        result.used_vedastro = False

    # ------------------------------------------------------------------
    # 輔助方法
    # ------------------------------------------------------------------
    @staticmethod
    def _fallback_lagna(birth_time: str) -> str:
        """根據出生時間粗略推估上升星座（Fallback）。

        極度簡化：每 2 小時一個星座，從日出約 06:00 開始為 Aries。
        """
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        ]
        hour = int(birth_time.split(":")[0])
        index = ((hour - 6) % 24) // 2
        return signs[index % 12]
