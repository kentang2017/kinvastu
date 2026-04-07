"""個人化 Astro-Vastu 命盤分析。

提供 ``personalized_astro_vastu()`` 函數，結合吠陀占星命盤
產生個人化的 Vastu Shastra 居家建議報告。

典型用法::

    from astro_vastu.personalized import personalized_astro_vastu

    personalized_astro_vastu(
        name="王小明",
        birth_date="1990-05-15",
        birth_time="08:30",
        birth_place="臺北",
        latitude=25.033,
        longitude=121.565,
    )
"""

from __future__ import annotations

from typing import Optional

from astro_vastu.astro.calculator import AstroCalculator
from astro_vastu.astro.mappings import (
    LAGNA_FACING,
    LAGNA_RULER,
    LAGNA_VASTU_DETAILS,
    MOON_ELEMENT_TIPS,
    PLANET_DIRECTION,
    PLANET_ZH,
    SIGN_ELEMENT,
    ZODIAC_ZH,
)
from astro_vastu.utils.formatters import build_planet_table, build_recommendation_table
from astro_vastu.utils.time_utils import (
    resolve_utc_offset,
    validate_coordinates,
    validate_date,
    validate_time,
)


def personalized_astro_vastu(
    name: str,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    latitude: float,
    longitude: float,
    utc_offset: Optional[str] = None,
    *,
    use_astro: bool = True,
    timezone: Optional[str] = None,
) -> None:
    """根據個人出生資料，結合吠陀占星命盤產生個人化 Vastu 建議。

    優先使用 VedAstro 庫計算精確命盤。若 VedAstro 未安裝或 API 呼叫失敗，
    將使用簡化的 fallback 推估方法並清楚提示使用者。

    Args:
        name: 使用者姓名。
        birth_date: 出生日期，格式 ``YYYY-MM-DD``。
        birth_time: 出生時間，格式 ``HH:MM``（24 小時制）。
        birth_place: 出生地點名稱（用於顯示）。
        latitude: 出生地緯度。
        longitude: 出生地經度（東經為正）。
        utc_offset: UTC 偏移量，例如 ``"+08:00"``。
            若未提供，將根據時區或經度自動估算。
        use_astro: 是否啟用占星計算。若為 ``False``，直接使用 Fallback。
        timezone: IANA 時區名稱（如 ``"Asia/Taipei"``），
            可精確處理夏令時間。

    Raises:
        InvalidDateError: 日期格式或範圍無效。
        InvalidTimeError: 時間格式或範圍無效。
        InvalidCoordinateError: 經緯度超出合法範圍。

    Example::

        personalized_astro_vastu(
            name="王小明",
            birth_date="1990-05-15",
            birth_time="08:30",
            birth_place="臺北",
            latitude=25.033,
            longitude=121.565,
        )
    """
    # ---- 輸入驗證 ----
    dt = validate_date(birth_date)
    validate_time(birth_time)
    validate_coordinates(latitude, longitude)

    # ---- 解析時區 ----
    resolved_offset = resolve_utc_offset(
        longitude, utc_offset=utc_offset, tz_name=timezone, dt=dt,
    )

    # ---- 報告標題 ----
    separator = "═" * 64
    print(f"\n{separator}")
    print("  🪐 個人化 Astro-Vastu 命盤分析報告")
    print(separator)
    print(f"  姓名：{name}")
    print("  出生日期：***（已遮蔽）")
    print("  出生時間：***（已遮蔽）")
    print(f"  出生地點：{birth_place}")
    print(f"  UTC 偏移：{resolved_offset}")
    print(separator)

    # ---- 占星計算 ----
    calculator = AstroCalculator(use_astro=use_astro)
    result = calculator.compute(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        latitude=latitude,
        longitude=longitude,
        utc_offset=resolved_offset,
    )

    # 顯示計算訊息
    for msg in result.messages:
        print(f"\n  {msg}")
    if result.messages:
        print()

    # ---- 命盤摘要 ----
    lagna_zh = ZODIAC_ZH.get(result.lagna_sign, result.lagna_sign)
    moon_zh = ZODIAC_ZH.get(result.moon_sign, result.moon_sign)
    lagna_element = SIGN_ELEMENT.get(result.lagna_sign, "未知")

    print(f"  🔮 上升星座（Lagna / Ascendant）：{lagna_zh}")
    print(f"  🌙 月亮星座（Moon Rāśi）：{moon_zh}")
    print(f"  🜂 上升元素屬性：{lagna_element}象")
    print()

    # ---- 行星位置表 ----
    print("  📊 九曜行星位置與 Vastu 對應：\n")
    if result.planet_info:
        print(build_planet_table(result.planet_info))
    print()

    # ---- 個人化 Vastu 建議 ----
    print(separator)
    print("  🏠 個人化 Vastu Shastra 建議")
    print(separator)

    facing = LAGNA_FACING.get(result.lagna_sign, "東方 — 通用推薦方位")
    print(f"\n  🧭 房屋推薦朝向：{facing}\n")

    details = LAGNA_VASTU_DETAILS.get(
        result.lagna_sign, LAGNA_VASTU_DETAILS["Aries"]
    )
    print(build_recommendation_table(details))

    # ---- 月亮星座建議 ----
    moon_element = SIGN_ELEMENT.get(result.moon_sign, "未知")
    print(f"\n  🌙 月亮星座額外建議（基於月亮在 {moon_zh} 的位置）：\n")
    print(f"      {MOON_ELEMENT_TIPS.get(moon_element, '請參考一般 Vastu 建議。')}")

    # ---- 綜合能量分析 ----
    print(f"\n{separator}")
    print("  ⚡ 綜合能量分析與特別提醒")
    print(separator)

    ruler = LAGNA_RULER.get(result.lagna_sign, "Jupiter")
    ruler_direction = PLANET_DIRECTION.get(ruler, "東北")
    ruler_zh = PLANET_ZH.get(ruler, "")

    energy_notes: list[str] = [
        f"1. 您的上升星座為 {lagna_zh}，Vastu 上最重要的方位是"
        f"「{ruler_direction}」（{ruler_zh} 主宰方位）。",
        "2. 東北方（Īśānya）無論任何命盤都必須保持潔淨開闊，"
        "這是宇宙正能量的入口。",
        "3. 中央 Brahmasthan 區域切勿放置重物或設置柱子，"
        "以免阻斷能量流通。",
        "4. 床頭朝向以南方為最佳（頭南腳北），"
        "可順應地球磁場，有助安眠。",
        "5. 財位（北方）建議放置保險箱或財務相關物品，"
        "面向北方工作有助財運。",
    ]

    for note in energy_notes:
        print(f"\n  {note}")

    print(f"\n{separator}")

    if not result.used_vedastro:
        print("\n  💡 溫馨提示：以上結果基於簡化推估。")
        print("     建議安裝 VedAstro（pip install vedastro）以獲得")
        print("     精確的吠陀占星計算與更準確的個人化建議。")

    print("\n  🙏 Om Vastu Devaya Namah | 願 Vastu 之神保佑您的居所平安吉祥 🙏")
    print(f"{separator}\n")
