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

    優先使用 pyswisseph 計算精確命盤（Lahiri Ayanamsa 恆星黃道）。
    若 pyswisseph 未安裝或計算失敗，
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
    print(f"  出生日期：{birth_date}")
    print("  出生時間：***（已遮蔽保護隱私）")
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
    recommended_facing = LAGNA_FACING.get(
        result.lagna_sign, "東方 — 通用推薦方位",
    )

    energy_notes: list[str] = [
        f"1. 您的上升星座為 {lagna_zh}，主宰行星為"
        f"{ruler_zh}，Vastu 上最重要的方位是"
        f"「{ruler_direction}」。推薦房屋朝向為「{recommended_facing.split('—')[0].strip()}」。",
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
        print("     建議安裝 pyswisseph（pip install pyswisseph）以獲得")
        print("     精確的吠陀占星計算與更準確的個人化建議。")

    print("\n  🙏 Om Vastu Devaya Namah | 願 Vastu 之神保佑您的居所平安吉祥 🙏")
    print(f"{separator}\n")


# ─── 房間配置建議 ─────────────────────────────────────────

# 上升星座 → 最佳房間擺設建議
_ROOM_PLACEMENT: dict[str, list[dict[str, str]]] = {
    "Aries": [
        {"房間": "🚪 大門", "最佳方位": "東方 / 東北方", "說明": "迎接晨曦火象能量", "補救": "門上掛銅鈴"},
        {"房間": "🛏️ 主臥室", "最佳方位": "南方 / 西南方", "說明": "穩固主人能量場", "補救": "使用暖色系寢具"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 火神方位最佳", "補救": "面東烹飪"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置水晶"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 財神方位", "補救": "放置綠色植物"},
        {"房間": "📚 書房", "最佳方位": "東方 / 北方", "說明": "知識與清晰思維", "補救": "面東或面北坐"},
    ],
    "Taurus": [
        {"房間": "🚪 大門", "最佳方位": "北方 / 東方", "說明": "穩定財運能量", "補救": "門口放盆栽"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "土象需穩固根基", "補救": "使用天然石材裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "使用陶瓷餐具"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "擺放銅製燈具"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "金星增添財運", "補救": "放置保險箱"},
        {"房間": "📚 書房", "最佳方位": "西方", "說明": "金星方位增進美感", "補救": "使用木質書桌"},
    ],
    "Gemini": [
        {"房間": "🚪 大門", "最佳方位": "北方", "說明": "水星方位促進溝通", "補救": "門口保持明亮"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西方 / 西南方", "說明": "穩定風象能量", "補救": "避免過多風鈴"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "保持通風"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置水晶球"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "水星加持智慧理財", "補救": "放置綠色植物"},
        {"房間": "📚 書房", "最佳方位": "北方", "說明": "水星方位最佳", "補救": "面北學習"},
    ],
    "Cancer": [
        {"房間": "🚪 大門", "最佳方位": "西北方 / 北方", "說明": "月亮主宰方位", "補救": "門口放銀色裝飾"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方 / 西方", "說明": "穩固水象根基", "補救": "使用淺色系寢具"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "火元素平衡水象", "補救": "面東烹飪"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "淨化水象情緒波動", "補救": "每日清晨淨化"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "月亮加持直覺理財", "補救": "放置白色花卉"},
        {"房間": "📚 書房", "最佳方位": "東方", "說明": "晨光帶來清新思路", "補救": "使用暖色照明"},
    ],
    "Leo": [
        {"房間": "🚪 大門", "最佳方位": "東方", "說明": "太陽方位最吉祥", "補救": "門上放太陽符號"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "穩固權威能量", "補救": "使用金色裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "火象雙重加持", "補救": "使用銅製鍋具"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置太陽 Yantra"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "面北工作"},
        {"房間": "📚 書房", "最佳方位": "東方", "說明": "太陽帶來榮耀", "補救": "面東學習"},
    ],
    "Virgo": [
        {"房間": "🚪 大門", "最佳方位": "北方", "說明": "水星主宰方位", "補救": "門口保持整潔"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方 / 南方", "說明": "穩定土象根基", "補救": "使用天然材質"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "保持廚房整潔"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "每日清晨冥想"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "水星精算能力", "補救": "放置計算機或帳簿"},
        {"房間": "📚 書房", "最佳方位": "北方", "說明": "水星促進分析力", "補救": "面北工作"},
    ],
    "Libra": [
        {"房間": "🚪 大門", "最佳方位": "西方 / 北方", "說明": "金星社交方位", "補救": "門口放花卉"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "金星和諧能量", "補救": "使用粉色系裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "使用銅製器具"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置蓮花或水晶"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "放置美術品"},
        {"房間": "📚 書房", "最佳方位": "東南方 / 西方", "說明": "金星帶來美感", "補救": "使用柔和照明"},
    ],
    "Scorpio": [
        {"房間": "🚪 大門", "最佳方位": "南方 / 東方", "說明": "火星主宰方位", "補救": "門口放紅色物品"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "穩固深層轉化", "補救": "使用深色寢具"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "面東烹飪"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "轉化深層能量", "補救": "定期淨化空間"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "放置暗色保險箱"},
        {"房間": "📚 書房", "最佳方位": "南方", "說明": "火星帶來專注力", "補救": "使用紅色文具"},
    ],
    "Sagittarius": [
        {"房間": "🚪 大門", "最佳方位": "東北方", "說明": "木星最吉祥方位", "補救": "門口放黃色花卉"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "平衡火象活力", "補救": "使用黃色系裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "保持明亮"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "木星雙重加持", "補救": "放置 Guru Yantra"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "面北冥想財運"},
        {"房間": "📚 書房", "最佳方位": "東北方", "說明": "木星智慧方位", "補救": "放置經典書籍"},
    ],
    "Capricorn": [
        {"房間": "🚪 大門", "最佳方位": "西方 / 南方", "說明": "土星穩固方位", "補救": "使用深色門框"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "土星紀律能量", "補救": "使用深色系裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "使用石材檯面"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置黑色石頭"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "放置鐵製保險箱"},
        {"房間": "📚 書房", "最佳方位": "西方", "說明": "土星增強紀律", "補救": "面西學習"},
    ],
    "Aquarius": [
        {"房間": "🚪 大門", "最佳方位": "西方 / 北方", "說明": "風象流動空間", "補救": "保持門口通風"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方 / 西方", "說明": "穩固根基", "補救": "使用深色系裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "Agni 方位", "補救": "保持通風"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性能量入口", "補救": "放置風鈴"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "使用科技理財"},
        {"房間": "📚 書房", "最佳方位": "西方 / 北方", "說明": "土星與風象結合", "補救": "保持空間開闊"},
    ],
    "Pisces": [
        {"房間": "🚪 大門", "最佳方位": "東北方", "說明": "木星靈性入口", "補救": "門口放水晶"},
        {"房間": "🛏️ 主臥室", "最佳方位": "西南方", "說明": "平衡水象情緒", "補救": "使用海洋色系裝飾"},
        {"房間": "🍳 廚房", "最佳方位": "東南方", "說明": "火元素平衡水象", "補救": "面東烹飪"},
        {"房間": "🙏 祈禱室", "最佳方位": "東北方", "說明": "靈性天賦綻放處", "補救": "每日冥想"},
        {"房間": "💰 財位", "最佳方位": "北方", "說明": "Kubera 永恆方位", "補救": "放置水晶球"},
        {"房間": "📚 書房", "最佳方位": "東方 / 東北方", "說明": "靈感與直覺方位", "補救": "放置薰香"},
    ],
}


def room_placement_recommendations(
    lagna_sign: str,
) -> list[dict[str, str]]:
    """根據上升星座回傳最佳房間配置建議。

    Args:
        lagna_sign: 上升星座英文名稱。

    Returns:
        房間配置建議列表，每項包含房間、最佳方位、說明、補救。
    """
    return list(_ROOM_PLACEMENT.get(lagna_sign, _ROOM_PLACEMENT["Aries"]))
