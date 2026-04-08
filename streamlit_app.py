"""
🕉️ Astro-Vastu Streamlit 互動介面
===================================

提供 Vastu Shastra 方位表格瀏覽與個人化 Astro-Vastu 命盤分析。

啟動方式::

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import streamlit as st
import pandas as pd

import streamlit.components.v1 as components

from astro_vastu.core.vastu_table import detailed_vastu_table
from astro_vastu.core.brahmasthan import BRAHMASTHAN_INFO
from astro_vastu.core.vastu_chart import render_vastu_mandala_html
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
from astro_vastu.personalized import room_placement_recommendations
from astro_vastu.utils.time_utils import (
    resolve_utc_offset,
    validate_coordinates,
    validate_date,
    validate_time,
)

# ─── 頁面設定 ─────────────────────────────────────────────
st.set_page_config(
    page_title="堅瓦斯圖 Kinvastu",
    page_icon="🕉️",
    layout="wide",
)

st.title("🕉️ 堅瓦斯圖 Kinvastu — 印度吠陀風水")
st.caption("結合 Vastu Shastra（印度建築風水）與 Vedic Jyotish（吠陀占星）")

# ─── 主要 Tab 導覽 ────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🏛️ Vastu 方位表格",
    "🪐 個人化 Astro-Vastu",
    "🔗 其他 Kin 系列工具",
])

# ─── 八方位 → 簡短代碼映射（用於「房屋朝向」選單） ──────
_FACING_OPTIONS: dict[str, str] = {
    "北方 (North)": "N",
    "東北 (North-East)": "NE",
    "東方 (East)": "E",
    "東南 (South-East)": "SE",
    "南方 (South)": "S",
    "西南 (South-West)": "SW",
    "西方 (West)": "W",
    "西北 (North-West)": "NW",
}

# ─── 方位代碼 → 元素 ─────────────────────────────────────
_DIRECTION_ELEMENT: dict[str, str] = {
    "N": "水", "NE": "空", "E": "火", "SE": "火",
    "S": "土", "SW": "土", "W": "水", "NW": "風",
}

# ─── Dosha（缺陷）檢測映射 ────────────────────────────────
# 上升元素與房屋朝向元素衝突 → Dosha
_ELEMENT_CONFLICTS: dict[tuple[str, str], str] = {
    ("火", "水"): "Jala-Agni Dosha — 水火衝突，可能影響健康與情緒",
    ("水", "火"): "Agni-Jala Dosha — 火水衝突，可能影響財運與穩定",
    ("風", "土"): "Pṛthvī-Vāyu Dosha — 土風衝突，可能影響溝通與決策",
    ("土", "風"): "Vāyu-Pṛthvī Dosha — 風土衝突，可能影響事業進展",
}

# ─── 元素 → 建議顏色 ─────────────────────────────────────
_ELEMENT_COLORS: dict[str, list[str]] = {
    "火": ["🔴 紅色", "🟠 橙色", "🟡 金色"],
    "土": ["🟤 棕色", "🟡 土黃色", "⬜ 米色"],
    "風": ["⚪ 白色", "🔵 淺藍色", "🟢 淺綠色"],
    "水": ["🔵 藍色", "⚪ 白色", "🟣 紫色"],
    "空": ["🟡 金色", "⬜ 象牙色", "🟣 淡紫色"],
}


def _compute_vastu_score(
    lagna_sign: str,
    house_facing_code: str,
    lagna_element: str,
) -> int:
    """計算 Vastu Compliance Score (0-100)。

    評分依據：
    - 朝向與上升星座推薦是否吻合 (40 分)
    - 元素和諧度 (30 分)
    - Brahmasthan 中央保護度 (固定 15 分，假設良好)
    - 東北方潔淨度 (固定 15 分，假設良好)
    """
    score = 0

    # 朝向匹配：檢查推薦朝向是否與實際一致
    recommended = LAGNA_FACING.get(lagna_sign, "")
    facing_map = {"N": "北", "NE": "東北", "E": "東", "SE": "東南",
                  "S": "南", "SW": "西南", "W": "西", "NW": "西北"}
    facing_zh = facing_map.get(house_facing_code, "")
    if facing_zh and facing_zh in recommended:
        score += 40
    elif any(kw in recommended for kw in ["通用", "次佳"]):
        score += 25
    else:
        score += 10

    # 元素和諧度
    facing_element = _DIRECTION_ELEMENT.get(house_facing_code, "")
    conflict = _ELEMENT_CONFLICTS.get((lagna_element, facing_element))
    if conflict is None:
        score += 30
    else:
        score += 10

    # 固定得分：Brahmasthan + 東北方
    score += 15 + 15

    return min(score, 100)


# ═══════════════════════════════════════════════════════════
#  Tab 1：Vastu 方位表格
# ═══════════════════════════════════════════════════════════
with tab1:
    st.header("🏛️ Vastu Shastra 方位詳解表")

    directions = st.radio(
        "選擇方位數量",
        [8, 16],
        horizontal=True,
        format_func=lambda x: f"{'八大' if x == 8 else '十六'}方位（{x} 方位）",
    )

    df = detailed_vastu_table(directions=directions, output="dataframe")

    if df is not None:
        # 加入 Emoji 方位指示
        _dir_emoji: dict[str, str] = {
            "East": "☀️", "South-East": "🔥", "South": "🛡️", "South-West": "⚓",
            "West": "🌊", "North-West": "💨", "North": "💰", "North-East": "🕉️",
            "East-NorthEast": "🌅", "East-SouthEast": "🔥", "South-SouthEast": "⚔️",
            "South-SouthWest": "🪨", "West-SouthWest": "📚", "West-NorthWest": "🧹",
            "North-NorthWest": "🤝", "North-NorthEast": "✨",
        }
        display_df = df.copy()

        # 在方向欄前加 Emoji
        if "方向 (Direction)" in display_df.columns:
            display_df["方向 (Direction)"] = display_df["方向 (Direction)"].apply(
                lambda x: next(
                    (f"{emoji} {x}" for key, emoji in _dir_emoji.items() if key in x),
                    x,
                )
            )

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # CSV 匯出
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 匯出 CSV",
            data=csv_data,
            file_name=f"vastu_{directions}_directions.csv",
            mime="text/csv",
        )

    # Brahmasthan 說明
    with st.expander("🙏 中央 — Brahmasthan（梵天位）說明", expanded=False):
        st.code(BRAHMASTHAN_INFO, language=None)

    # 補救提示
    with st.expander("💊 各方位補救措施速覽", expanded=False):
        _json_path = Path(__file__).resolve().parent / "astro_vastu" / "data" / "vastu_directions.json"
        try:
            with open(_json_path, encoding="utf-8") as fh:
                _raw = json.load(fh)
            remedy_rows = []
            for d in _raw.get("directions_8", []):
                remedies = d.get("remedies", [])
                if remedies:
                    remedy_rows.append({
                        "方位": d.get("方向 (Direction)", ""),
                        "補救措施": "；".join(remedies),
                    })
            if remedy_rows:
                st.dataframe(
                    pd.DataFrame(remedy_rows),
                    use_container_width=True,
                    hide_index=True,
                )
        except Exception:
            st.info("補救措施資料載入中⋯⋯")

# ═══════════════════════════════════════════════════════════
#  Tab 2：個人化 Astro-Vastu
# ═══════════════════════════════════════════════════════════
with tab2:
    st.header("🪐 個人化 Astro-Vastu 命盤分析")

    with st.form("birth_form"):
        st.subheader("📝 請輸入出生資料")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名", value="", placeholder="例如：王小明")
            birth_date = st.date_input(
                "出生日期",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date(2099, 12, 31),
            )
            birth_time = st.time_input("出生時間")
        with col2:
            birth_place = st.text_input("出生地點", value="", placeholder="例如：臺北")
            latitude = st.number_input("緯度", value=25.033, min_value=-90.0, max_value=90.0, format="%.3f")
            longitude = st.number_input("經度", value=121.565, min_value=-180.0, max_value=180.0, format="%.3f")

        col3, col4 = st.columns(2)
        with col3:
            timezone_str = st.text_input(
                "IANA 時區（可選）",
                value="",
                placeholder="例如：Asia/Hong_Kong",
                help="提供精確的 IANA 時區名稱可更準確處理夏令時。留空則根據經度估算。",
            )
        with col4:
            use_astro = st.checkbox("啟用精確吠陀占星計算", value=True)

        st.subheader("🏠 房屋主朝向")
        house_facing = st.selectbox(
            "選擇房屋大門主要朝向",
            options=list(_FACING_OPTIONS.keys()),
            index=0,
            help="房屋大門面向的方位。此資訊將用於產生個人化房屋風水診斷報告。",
        )

        submitted = st.form_submit_button("🔮 開始分析", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("請輸入姓名。")
            st.stop()
        if not birth_place.strip():
            st.error("請輸入出生地點。")
            st.stop()

        # ---- 格式化輸入 ----
        birth_date_str = birth_date.strftime("%Y-%m-%d")
        birth_time_str = birth_time.strftime("%H:%M")
        tz_name = timezone_str.strip() if timezone_str.strip() else None
        house_facing_code = _FACING_OPTIONS[house_facing]

        # ---- 驗證輸入 ----
        try:
            dt = validate_date(birth_date_str)
            validate_time(birth_time_str)
            validate_coordinates(latitude, longitude)
        except Exception as exc:
            st.error(f"輸入驗證失敗：{exc}")
            st.stop()

        # ---- 解析時區 ----
        resolved_offset = resolve_utc_offset(
            longitude, utc_offset=None, tz_name=tz_name, dt=dt,
        )

        # ---- 報告標題 ----
        st.divider()
        st.subheader("📋 個人化 Astro-Vastu 命盤分析報告")

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**姓名：** {name}")
            st.markdown(f"**出生地點：** {birth_place}")
            st.markdown(f"**房屋朝向：** {house_facing}")
        with info_col2:
            st.markdown(f"**出生日期：** {birth_date_str}")
            st.markdown("**出生時間：** ***（已遮蔽保護隱私）***")
            st.markdown(f"**UTC 偏移：** {resolved_offset}")

        # ---- 占星計算 ----
        calculator = AstroCalculator(use_astro=use_astro)
        result = calculator.compute(
            birth_date=birth_date_str,
            birth_time=birth_time_str,
            birth_place=birth_place,
            latitude=latitude,
            longitude=longitude,
            utc_offset=resolved_offset,
        )

        # 顯示計算訊息
        for msg in result.messages:
            st.info(msg)

        # ---- 命盤摘要 ----
        lagna_zh = ZODIAC_ZH.get(result.lagna_sign, result.lagna_sign)
        moon_zh = ZODIAC_ZH.get(result.moon_sign, result.moon_sign)
        lagna_element = SIGN_ELEMENT.get(result.lagna_sign, "未知")

        st.divider()
        st.subheader("🔮 命盤摘要")

        m1, m2, m3 = st.columns(3)
        m1.metric("上升星座（Lagna）", lagna_zh)
        m2.metric("月亮星座（Moon Rāśi）", moon_zh)
        m3.metric("上升元素屬性", f"{lagna_element}象")

        # ---- Vastu Compliance Score ----
        vastu_score = _compute_vastu_score(
            result.lagna_sign, house_facing_code, lagna_element,
        )

        st.divider()
        st.subheader("📊 Vastu Compliance Score")

        score_col1, score_col2 = st.columns([1, 2])
        with score_col1:
            if vastu_score >= 80:
                st.success(f"🏆 **{vastu_score} / 100**")
            elif vastu_score >= 60:
                st.warning(f"⚡ **{vastu_score} / 100**")
            else:
                st.error(f"⚠️ **{vastu_score} / 100**")
        with score_col2:
            if vastu_score >= 80:
                st.markdown("✅ 房屋朝向與命盤高度吻合，Vastu 能量極佳！")
            elif vastu_score >= 60:
                st.markdown("⚡ 尚可，但建議參考補救措施以提升和諧度。")
            else:
                st.markdown("⚠️ 房屋朝向與命盤存在衝突，建議重點關注補救方案。")

        st.progress(vastu_score / 100)

        # ---- 房屋風水診斷報告 ----
        st.divider()
        st.subheader("🏠 房屋風水診斷報告")

        facing_element = _DIRECTION_ELEMENT.get(house_facing_code, "未知")
        conflict = _ELEMENT_CONFLICTS.get((lagna_element, facing_element))

        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            st.markdown(f"**上升元素：** {lagna_element}象")
            st.markdown(f"**朝向元素：** {facing_element}象")
        with diag_col2:
            if conflict:
                st.error(f"🚨 **Dosha 衝突：** {conflict}")
            else:
                st.success("✅ 元素和諧 — 無明顯 Dosha 衝突")

        # 顏色建議
        rec_colors = _ELEMENT_COLORS.get(lagna_element, ["🎨 請參考一般建議"])
        st.markdown(f"**🎨 推薦室內顏色：** {' · '.join(rec_colors)}")

        if conflict:
            st.markdown("**💊 Dosha 補救建議：**")
            if "水火" in conflict or "Jala-Agni" in conflict:
                st.markdown("- 在東南方放置銅製器具以調和火元素")
                st.markdown("- 避免在廚房使用過多水元素裝飾")
            elif "火水" in conflict or "Agni-Jala" in conflict:
                st.markdown("- 在北方加強綠色植物以橋接能量")
                st.markdown("- 東北方放置水晶調和")
            elif "土風" in conflict or "Pṛthvī-Vāyu" in conflict:
                st.markdown("- 西北方保持通風以釋放滯留能量")
                st.markdown("- 使用風鈴或輕質裝飾促進流動")
            elif "風土" in conflict or "Vāyu-Pṛthvī" in conflict:
                st.markdown("- 西南方放置重型傢具穩固根基")
                st.markdown("- 使用土色系地毯增添穩定感")

        # ---- 行星位置表 ----
        if result.planet_info:
            st.divider()
            st.subheader("📊 九曜行星位置與 Vastu 對應")
            planet_df = pd.DataFrame(result.planet_info)
            st.dataframe(planet_df, use_container_width=True, hide_index=True)

        # ---- 個人化 Vastu 建議 ----
        st.divider()
        st.subheader("🏠 個人化 Vastu Shastra 建議")

        facing = LAGNA_FACING.get(result.lagna_sign, "東方 — 通用推薦方位")
        st.markdown(f"**🧭 命盤推薦朝向：** {facing}")

        # ---- Vastu Purusha Mandala 圖表 ----
        ruler = LAGNA_RULER.get(result.lagna_sign, "Jupiter")
        mandala_html = render_vastu_mandala_html(
            lagna_sign=result.lagna_sign,
            lagna_ruler=ruler,
        )
        components.html(mandala_html, height=920)

        details = LAGNA_VASTU_DETAILS.get(
            result.lagna_sign, LAGNA_VASTU_DETAILS["Aries"]
        )
        rec_data = [
            {"建議項目": key, "詳細說明": value[0], "傳統理由": value[1]}
            for key, value in details.items()
        ]
        rec_df = pd.DataFrame(rec_data)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

        # ---- 最佳房間配置建議 ----
        st.divider()
        st.subheader("🛋️ 最佳房間配置建議")
        room_recs = room_placement_recommendations(result.lagna_sign)
        if room_recs:
            room_df = pd.DataFrame(room_recs)
            st.dataframe(room_df, use_container_width=True, hide_index=True)
        else:
            st.info("暫無特定房間配置建議，請參考上方個人化 Vastu 建議。")

        # ---- Brahmasthan 獨立診斷 ----
        st.divider()
        st.subheader("🙏 Brahmasthan（梵天位）診斷")

        brahma_col1, brahma_col2 = st.columns(2)
        with brahma_col1:
            st.markdown("""
**中央區域重要提醒：**
- ✅ 保持空曠、潔淨、開放
- ✅ 可放置 Vastu Yantra 或水晶
- ❌ 不可設置柱子、樓梯
- ❌ 不可放置重型傢具或廁所
""")
        with brahma_col2:
            st.markdown("""
**Brahmasthan 健康度：**
- 佔全屋面積約 1/9
- 等同人體心輪（Anāhata Chakra）
- 梵天創造之能量中心
- 保持開闊 → 能量均勻分佈八方
""")

        with st.expander("📖 完整 Brahmasthan 說明", expanded=False):
            st.code(BRAHMASTHAN_INFO, language=None)

        # ---- 月亮星座建議 ----
        moon_element = SIGN_ELEMENT.get(result.moon_sign, "未知")
        st.divider()
        st.subheader(f"🌙 月亮星座額外建議（{moon_zh}）")
        moon_tip = MOON_ELEMENT_TIPS.get(moon_element, "請參考一般 Vastu 建議。")
        st.info(moon_tip)

        # ---- 綜合能量分析 ----
        st.divider()
        st.subheader("⚡ 綜合能量分析與特別提醒")

        ruler_direction = PLANET_DIRECTION.get(ruler, "東北")
        ruler_zh = PLANET_ZH.get(ruler, "")
        recommended_facing = LAGNA_FACING.get(
            result.lagna_sign, "東方 — 通用推薦方位",
        )

        energy_notes = [
            f"1. 您的上升星座為 {lagna_zh}，主宰行星為{ruler_zh}，Vastu 上最重要的方位是「{ruler_direction}」。推薦房屋朝向為「{recommended_facing.split('—')[0].strip()}」。",
            "2. 東北方（Īśānya）無論任何命盤都必須保持潔淨開闊，這是宇宙正能量的入口。",
            "3. 中央 Brahmasthan 區域切勿放置重物或設置柱子，以免阻斷能量流通。",
            "4. 床頭朝向以南方為最佳（頭南腳北），可順應地球磁場，有助安眠。",
            "5. 財位（北方）建議放置保險箱或財務相關物品，面向北方工作有助財運。",
        ]

        for note in energy_notes:
            st.markdown(f"- {note}")

        # ---- 精確計算提示 ----
        if not result.used_vedastro:
            st.divider()
            st.warning(
                "💡 以上結果基於簡化推估。建議安裝 pyswisseph（`pip install pyswisseph`）以獲得"
                "精確的吠陀占星計算與更準確的個人化建議。"
            )

        st.divider()
        st.success("🙏 Om Vastu Devaya Namah | 願 Vastu 之神保佑您的居所平安吉祥 🙏")

# ═══════════════════════════════════════════════════════════
#  Tab 3：其他 Kin 系列工具
# ═══════════════════════════════════════════════════════════
with tab3:
    st.header("🔗 其他 Kin 系列術數工具")
    st.markdown("""
歡迎探索 **Kin 系列** — 涵蓋東西方多種傳統占卜與術數系統的開源工具集。
每個專案都可獨立使用，也可透過 Streamlit 互動介面操作。
""")

    _KIN_PROJECTS = [
        {
            "emoji": "🪐",
            "name": "kinastro（堅占星）",
            "url": "https://github.com/kentang2017/kinastro",
            "desc": "印度吠陀占星 Vedic Jyotish 命盤計算與分析工具，支援 Lahiri Ayanamsa、行星力量評估與 Dasha 大運週期。",
        },
        {
            "emoji": "🚪",
            "name": "kinqimen（奇門遁甲）",
            "url": "https://github.com/kentang2017/kinqimen",
            "desc": "中國傳統奇門遁甲排盤系統，支援時家奇門、日家奇門，含完整天地人神四盤。",
        },
        {
            "emoji": "🌌",
            "name": "kintaiyi（太乙神數）",
            "url": "https://github.com/kentang2017/kintaiyi",
            "desc": "中國古代三式之一 — 太乙神數排盤與推演工具。",
        },
        {
            "emoji": "🔮",
            "name": "kinliuren（大六壬）",
            "url": "https://github.com/kentang2017/kinliuren",
            "desc": "中國古代三式之一 — 大六壬排盤系統，含天地盤、四課三傳完整推演。",
        },
        {
            "emoji": "☯️",
            "name": "ichingshifa（周易筮法）",
            "url": "https://github.com/kentang2017/ichingshifa",
            "desc": "周易筮法（大衍之數）數位化工具，模擬傳統蓍草占卦流程。",
        },
        {
            "emoji": "🐚",
            "name": "kinifa（伊法占卜）",
            "url": "https://github.com/kentang2017/kinifa",
            "desc": "非洲約魯巴族 Ifá 占卜系統的數位化實現，含完整 256 Odù 詮釋。",
        },
        {
            "emoji": "🎋",
            "name": "kinwuzhao（五兆）",
            "url": "https://github.com/kentang2017/kinwuzhao",
            "desc": "日本陰陽道五兆占卜法 — 結合中國易學與日本神道傳統。",
        },
        {
            "emoji": "⭐",
            "name": "kinketika（馬來七星擇吉）",
            "url": "https://github.com/kentang2017/kinketika",
            "desc": "馬來傳統七星擇吉系統（Ketika Tujuh），東南亞獨特的擇日工具。",
        },
        {
            "emoji": "📅",
            "name": "kinbazi（八字命理）",
            "url": "https://github.com/kentang2017/kinbazi",
            "desc": "中國八字命理排盤與分析工具，支援大運流年、十神、神煞等。",
        },
        {
            "emoji": "🏔️",
            "name": "kinziwei（紫微斗數）",
            "url": "https://github.com/kentang2017/kinziwei",
            "desc": "紫微斗數命盤排盤工具，含十四主星與輔星完整佈局。",
        },
        {
            "emoji": "🧮",
            "name": "kinmeihua（梅花易數）",
            "url": "https://github.com/kentang2017/kinmeihua",
            "desc": "梅花易數起卦與斷卦工具，支援多種起卦方式。",
        },
    ]

    for proj in _KIN_PROJECTS:
        st.markdown(
            f"### {proj['emoji']} [{proj['name']}]({proj['url']})\n"
            f"{proj['desc']}\n"
        )

    st.divider()
    st.markdown(
        "💡 所有專案均為開源，歡迎 ⭐ Star、Fork 與 Pull Request！\n\n"
        "🔗 [kentang2017 GitHub](https://github.com/kentang2017)"
    )
