"""
🕉️ Astro-Vastu Streamlit 互動介面
===================================

提供 Vastu Shastra 方位表格瀏覽與個人化 Astro-Vastu 命盤分析。

啟動方式::

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import datetime
import streamlit as st
import pandas as pd

from astro_vastu.core.vastu_table import detailed_vastu_table
from astro_vastu.core.brahmasthan import BRAHMASTHAN_INFO
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
from astro_vastu.utils.time_utils import (
    resolve_utc_offset,
    validate_coordinates,
    validate_date,
    validate_time,
)

# ─── 頁面設定 ─────────────────────────────────────────────
st.set_page_config(
    page_title="堅瓦斯圖 Kinvastu — 印度吠陀風水",
    page_icon="🕉️",
    layout="wide",
)

st.title("堅瓦斯圖 Kinvastu — 印度吠陀風水")
st.caption("結合 Vastu Shastra（印度建築風水）與 Vedic Jyotish（吠陀占星）")

# ─── 側邊欄導覽 ───────────────────────────────────────────
page = st.sidebar.radio(
    "📌 功能選擇",
    ["🏛️ Vastu 方位表格", "🪐 個人化 Astro-Vastu"],
)

# ═══════════════════════════════════════════════════════════
#  頁面一：Vastu 方位表格
# ═══════════════════════════════════════════════════════════
if page == "🏛️ Vastu 方位表格":
    st.header("🏛️ Vastu Shastra 方位詳解表")

    directions = st.radio(
        "選擇方位數量",
        [8, 16],
        horizontal=True,
        format_func=lambda x: f"{'八大' if x == 8 else '十六'}方位（{x} 方位）",
    )

    df = detailed_vastu_table(directions=directions, output="dataframe")

    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Brahmasthan 說明
    with st.expander("🙏 中央 — Brahmasthan（梵天位）說明", expanded=False):
        st.code(BRAHMASTHAN_INFO, language=None)

# ═══════════════════════════════════════════════════════════
#  頁面二：個人化 Astro-Vastu
# ═══════════════════════════════════════════════════════════
elif page == "🪐 個人化 Astro-Vastu":
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
                placeholder="例如：Asia/Hong Kong",
                help="提供精確的 IANA 時區名稱可更準確處理夏令時。留空則根據經度估算。",
            )
        with col4:
            use_astro = st.checkbox("啟用精確吠陀占星計算", value=True)

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
        st.markdown(f"**🧭 房屋推薦朝向：** {facing}")

        details = LAGNA_VASTU_DETAILS.get(
            result.lagna_sign, LAGNA_VASTU_DETAILS["Aries"]
        )
        rec_data = [
            {"建議項目": key, "詳細說明": value[0], "傳統理由": value[1]}
            for key, value in details.items()
        ]
        rec_df = pd.DataFrame(rec_data)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

        # ---- 月亮星座建議 ----
        moon_element = SIGN_ELEMENT.get(result.moon_sign, "未知")
        st.divider()
        st.subheader(f"🌙 月亮星座額外建議（{moon_zh}）")
        moon_tip = MOON_ELEMENT_TIPS.get(moon_element, "請參考一般 Vastu 建議。")
        st.info(moon_tip)

        # ---- 綜合能量分析 ----
        st.divider()
        st.subheader("⚡ 綜合能量分析與特別提醒")

        ruler = LAGNA_RULER.get(result.lagna_sign, "Jupiter")
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
