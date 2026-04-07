"""占星計算器 — 封裝 VedAstro 與 Fallback 邏輯。

VedAstro 為可選依賴。若未安裝或 API 呼叫失敗，
自動切換至簡化推估方法並清楚提示使用者。

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
from typing import Any, Optional

from astro_vastu.astro.mappings import (
    MOON_SIGNS_BY_MONTH,
    PLANET_DIRECTION,
    PLANET_NAMES_EN,
    PLANET_ZH,
    ZODIAC_ZH,
)
from astro_vastu.exceptions import AstroCalculationError
from astro_vastu.utils.time_utils import format_vedastro_time, longitude_to_utc_offset

# ---------- VedAstro 動態匯入 ----------
_VEDASTRO_AVAILABLE: bool = False
try:
    from vedastro import (  # type: ignore[import-untyped]
        Calculate,
        GeoLocation,
        PlanetName,
        Time,
    )

    _VEDASTRO_AVAILABLE = True
except ImportError:
    pass


def is_vedastro_available() -> bool:
    """檢查 VedAstro 庫是否可用。"""
    return _VEDASTRO_AVAILABLE


@dataclass
class AstroResult:
    """占星計算結果。

    Attributes:
        lagna_sign: 上升星座英文名稱。
        moon_sign: 月亮星座英文名稱。
        planet_info: 九曜行星位置資訊列表。
        used_vedastro: 是否使用了 VedAstro 精確計算。
        messages: 計算過程中的提示訊息。
    """

    lagna_sign: str = ""
    moon_sign: str = ""
    planet_info: list[dict[str, str]] = field(default_factory=list)
    used_vedastro: bool = False
    messages: list[str] = field(default_factory=list)


class AstroCalculator:
    """占星計算器，封裝 VedAstro 與 Fallback 邏輯。

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

        if self._use_astro and _VEDASTRO_AVAILABLE:
            try:
                self._compute_vedastro(
                    result, birth_date, birth_time, birth_place,
                    latitude, longitude, utc_offset,
                )
                return result
            except Exception as exc:
                result.messages.append(
                    f"⚠️  VedAstro API 呼叫失敗：{exc}\n"
                    "      將使用簡化推估方法作為替代。"
                )

        if self._use_astro and not _VEDASTRO_AVAILABLE:
            result.messages.append(
                "⚠️  VedAstro 庫未安裝。請執行以下命令安裝：\n"
                "      pip install vedastro\n"
                "      安裝後即可獲得精確的吠陀占星計算。"
            )
            result.messages.append(
                "📌 目前使用簡化推估方法（僅供參考，精度有限）。"
            )

        self._compute_fallback(result, birth_date, birth_time)
        return result

    # ------------------------------------------------------------------
    # VedAstro 精確計算
    # ------------------------------------------------------------------
    def _compute_vedastro(
        self,
        result: AstroResult,
        birth_date: str,
        birth_time: str,
        birth_place: str,
        latitude: float,
        longitude: float,
        utc_offset: str,
    ) -> None:
        """使用 VedAstro 進行精確吠陀計算。"""
        geo = GeoLocation(birth_place, longitude, latitude)
        time_str = format_vedastro_time(birth_date, birth_time, utc_offset)
        birth_time_obj = Time(time_str, geo)

        # Lagna
        lagna_result = Calculate.LagnaSignName(birth_time_obj)
        result.lagna_sign = self._match_sign(str(lagna_result).strip())

        # Moon sign
        moon_result = Calculate.MoonSignName(birth_time_obj)
        result.moon_sign = self._match_sign(str(moon_result).strip())

        # 九曜行星
        planets = [
            PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
            PlanetName.Mercury, PlanetName.Jupiter,
            PlanetName.Venus, PlanetName.Saturn,
            PlanetName.Rahu, PlanetName.Ketu,
        ]
        for p_obj, p_name in zip(planets, PLANET_NAMES_EN):
            try:
                sign_result = Calculate.PlanetRasiD1Sign(p_obj, birth_time_obj)
                matched_sign = self._match_sign(str(sign_result).strip())

                strength_str = "—"
                try:
                    strength_result = Calculate.PlanetPowerPercentage(
                        p_obj, birth_time_obj
                    )
                    strength_str = str(strength_result).strip()
                except Exception:
                    pass

                result.planet_info.append({
                    "行星": PLANET_ZH.get(p_name, p_name),
                    "所在星座": ZODIAC_ZH.get(matched_sign, matched_sign),
                    "Vastu 方位": PLANET_DIRECTION.get(p_name, "—"),
                    "力量": strength_str,
                })
            except Exception:
                result.planet_info.append({
                    "行星": PLANET_ZH.get(p_name, p_name),
                    "所在星座": "（計算中出現問題）",
                    "Vastu 方位": PLANET_DIRECTION.get(p_name, "—"),
                    "力量": "—",
                })

        result.used_vedastro = True
        result.messages.append(
            "✅ 已使用 VedAstro 庫進行精確吠陀計算（Lahiri Ayanamsa）。"
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
                "所在星座": "（需 VedAstro 精確計算）",
                "Vastu 方位": PLANET_DIRECTION.get(p_name, "—"),
                "力量": "—",
            })

        result.used_vedastro = False

    # ------------------------------------------------------------------
    # 輔助方法
    # ------------------------------------------------------------------
    @staticmethod
    def _match_sign(raw: str) -> str:
        """從 VedAstro 回傳值中比對星座英文名稱。"""
        for zn in ZODIAC_ZH:
            if zn.lower() in raw.lower():
                return zn
        return raw

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
