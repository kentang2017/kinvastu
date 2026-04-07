#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
  astro_vastu_pro.py — 超級進階 Astro-Vastu 模組
  結合 Vastu Shastra（建築風水）與 Vedic Jyotish（吠陀占星）

  作者：KinVastu 團隊
  授權：MIT License
  Python 版本需求：>= 3.10
===============================================================================

  📦 安裝依賴：
      pip install vedastro pandas tabulate

  📖 功能簡介：
      1. detailed_vastu_table()    — 超詳細 Vastu 八大/十六方位表格（繁體中文）
      2. personalized_astro_vastu() — 根據個人出生資料，結合命盤的個人化 Vastu 建議

  🔧 使用範例：
      from astro_vastu_pro import detailed_vastu_table, personalized_astro_vastu

      # 顯示八方位 Vastu 表格
      detailed_vastu_table(directions=8)

      # 顯示十六方位 Vastu 表格
      detailed_vastu_table(directions=16)

      # 個人化 Astro-Vastu 推薦（需要網路連線以呼叫 VedAstro API）
      personalized_astro_vastu(
          name="王小明",
          birth_date="1990-05-15",
          birth_time="08:30",
          birth_place="臺北",
          latitude=25.033,
          longitude=121.565,
      )

  📚 參考經典：
      - Mayamata（摩耶論）
      - Manasara（摩那薩羅）
      - Brihat Samhita（大合集論）
      - Vastu Ratnakara（Vastu 寶鑑）
      - Brihat Parashara Hora Shastra（帕拉夏拉大時論）
===============================================================================
"""

from __future__ import annotations

import textwrap
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from tabulate import tabulate

# ---------------------------------------------------------------------------
# VedAstro 動態匯入（優雅 fallback）
# ---------------------------------------------------------------------------
_VEDASTRO_AVAILABLE: bool = False
try:
    from vedastro import (  # type: ignore[import-untyped]
        Calculate,
        GeoLocation,
        PlanetName,
        Time,
        ZodiacName,
    )

    _VEDASTRO_AVAILABLE = True
except ImportError:
    pass

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                   第一部分：靜態 Vastu Shastra 資料                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ---------- 八大方位完整資料 ----------

_VASTU_DATA_8: list[dict[str, str]] = [
    {
        "方向 (Direction)": "East / 東方 (Pūrva)",
        "主宰神祇 (Deity)": "Indra（因陀羅／雷帝）",
        "五大元素 (Element)": "火 (Agni Tattva)",
        "關聯行星 (Planet)": "太陽 (Sun / Sūrya)",
        "推薦顏色 (Colors)": "白色、淺黃色、橙色",
        "推薦材質 (Materials)": "木材、玻璃",
        "適合房間與用途 (Suitable Rooms)": (
            "客廳、起居室、冥想室、讀書室；"
            "適合設置大窗戶或陽台以迎接晨光"
        ),
        "嚴格避免事項 (Avoid)": (
            "避免設置廁所、垃圾間或儲藏室；"
            "不宜堆放重物或雜物"
        ),
        "傳統意義與能量 (Significance)": (
            "東方代表新生、啟明與知識的力量。"
            "晨曦之光帶來生命能量（Prāṇa），"
            "有利於健康、名望與靈性成長。"
        ),
    },
    {
        "方向 (Direction)": "South-East / 東南 (Āgneya)",
        "主宰神祇 (Deity)": "Agni（阿耆尼／火神）",
        "五大元素 (Element)": "火 (Agni Tattva)",
        "關聯行星 (Planet)": "金星 (Venus / Śukra)",
        "推薦顏色 (Colors)": "紅色、橘色、粉紅色",
        "推薦材質 (Materials)": "花崗岩、陶瓷、紅磚",
        "適合房間與用途 (Suitable Rooms)": (
            "廚房（最佳位置）、電氣設備間、"
            "壁爐區域；適合放置與火相關的設施"
        ),
        "嚴格避免事項 (Avoid)": (
            "嚴禁設置水井、水塔或蓄水池；"
            "避免放置鏡子、水族箱"
        ),
        "傳統意義與能量 (Significance)": (
            "東南方為火元素的主宰方位，"
            "掌管消化力（Jaṭhara Agni）與轉化能量。"
            "正確使用能提升家庭健康與活力。"
        ),
    },
    {
        "方向 (Direction)": "South / 南方 (Dakṣiṇa)",
        "主宰神祇 (Deity)": "Yama（閻摩／死神）",
        "五大元素 (Element)": "土 (Pṛthvī Tattva)",
        "關聯行星 (Planet)": "火星 (Mars / Maṅgala)",
        "推薦顏色 (Colors)": "紅色、珊瑚色、深橘色",
        "推薦材質 (Materials)": "石材、厚重木材、紅土磚",
        "適合房間與用途 (Suitable Rooms)": (
            "主臥室、倉庫、重型家具擺放區；"
            "南牆宜加厚加高以擋煞氣"
        ),
        "嚴格避免事項 (Avoid)": (
            "避免設置大門正對正南；"
            "不宜開大窗或設陽台；"
            "避免放置水元素物品"
        ),
        "傳統意義與能量 (Significance)": (
            "南方由閻摩主宰，象徵秩序與法則。"
            "能量沉穩厚重，適合休息與儲存。"
            "需保持此方位的牆面厚實堅固。"
        ),
    },
    {
        "方向 (Direction)": "South-West / 西南 (Nairṛtya)",
        "主宰神祇 (Deity)": "Nirṛti（尼律提／羅剎主）",
        "五大元素 (Element)": "土 (Pṛthvī Tattva)",
        "關聯行星 (Planet)": "羅睺 (Rahu)",
        "推薦顏色 (Colors)": "棕色、米色、土黃色",
        "推薦材質 (Materials)": "厚重石材、混凝土、實木",
        "適合房間與用途 (Suitable Rooms)": (
            "家主（男主人）臥室、保險箱放置處、"
            "重型儲藏室；此方位宜重不宜輕"
        ),
        "嚴格避免事項 (Avoid)": (
            "嚴禁設置化糞池或地下水池；"
            "不宜挖掘或下沉；"
            "避免設為兒童房或客房"
        ),
        "傳統意義與能量 (Significance)": (
            "西南方代表穩定與根基，是整棟建築"
            "能量的「錨點」。此方位越重越高，"
            "家運越穩定，男主人運勢越強。"
        ),
    },
    {
        "方向 (Direction)": "West / 西方 (Paścima)",
        "主宰神祇 (Deity)": "Varuṇa（伐樓那／水神）",
        "五大元素 (Element)": "水 (Jala Tattva)",
        "關聯行星 (Planet)": "土星 (Saturn / Śani)",
        "推薦顏色 (Colors)": "藍色、白色、銀色",
        "推薦材質 (Materials)": "金屬、鋼鐵、深色木材",
        "適合房間與用途 (Suitable Rooms)": (
            "餐廳、兒童房、學習室；"
            "適合設置金屬裝飾品與水景"
        ),
        "嚴格避免事項 (Avoid)": (
            "不宜設置主臥室在純西方；"
            "避免大門直接朝向正西"
        ),
        "傳統意義與能量 (Significance)": (
            "西方由水神伐樓那主宰，"
            "象徵收穫、成熟與社交能力。"
            "夕陽能量有助於放鬆與恢復。"
        ),
    },
    {
        "方向 (Direction)": "North-West / 西北 (Vāyavya)",
        "主宰神祇 (Deity)": "Vāyu（伐由／風神）",
        "五大元素 (Element)": "風 (Vāyu Tattva)",
        "關聯行星 (Planet)": "月亮 (Moon / Chandra)",
        "推薦顏色 (Colors)": "灰色、白色、淺藍色",
        "推薦材質 (Materials)": "輕質材料、竹子、薄木板",
        "適合房間與用途 (Suitable Rooms)": (
            "客房、女兒房、車庫、穀倉；"
            "適合設為「過渡性」空間"
        ),
        "嚴格避免事項 (Avoid)": (
            "不宜作為家主臥室；"
            "避免放置保險箱或貴重物品；"
            "不宜設為祈禱室"
        ),
        "傳統意義與能量 (Significance)": (
            "西北方為風元素主宰方位，"
            "象徵流動、變化與人際關係。"
            "能量輕盈流動，適合暫住與社交空間。"
        ),
    },
    {
        "方向 (Direction)": "North / 北方 (Uttara)",
        "主宰神祇 (Deity)": "Kubera（俱吠羅／財神）",
        "五大元素 (Element)": "水 (Jala Tattva)",
        "關聯行星 (Planet)": "水星 (Mercury / Budha)",
        "推薦顏色 (Colors)": "綠色、藍色、淺色系",
        "推薦材質 (Materials)": "輕質材料、玻璃、水晶",
        "適合房間與用途 (Suitable Rooms)": (
            "客廳、財務辦公室、保險箱（財位）；"
            "適合開大窗與設入口；"
            "北方宜保持開闊、明亮"
        ),
        "嚴格避免事項 (Avoid)": (
            "嚴禁設置廁所或廚房；"
            "不宜堆放垃圾或雜物；"
            "避免建築此方位過高"
        ),
        "傳統意義與能量 (Significance)": (
            "北方為財神俱吠羅的方位，"
            "是財富與繁榮的源頭。"
            "保持北方開闊低矮，能招財納福。"
            "地球磁場從北方流入，有利於生命力。"
        ),
    },
    {
        "方向 (Direction)": "North-East / 東北 (Īśānya)",
        "主宰神祇 (Deity)": "Īśāna（伊舍那天／濕婆化身）",
        "五大元素 (Element)": "空 / 以太 (Ākāśa Tattva)",
        "關聯行星 (Planet)": "木星 (Jupiter / Bṛhaspati)",
        "推薦顏色 (Colors)": "黃色、金色、淺色調",
        "推薦材質 (Materials)": "大理石、水晶、黃銅",
        "適合房間與用途 (Suitable Rooms)": (
            "祈禱室（Pūjā Room，最佳位置）、"
            "冥想角落、水井或水池；"
            "此方位必須保持最潔淨、最低矮、最開闊"
        ),
        "嚴格避免事項 (Avoid)": (
            "嚴禁設置廁所、廚房或垃圾間；"
            "不可放置重物或建高牆；"
            "絕對不可挖化糞池"
        ),
        "傳統意義與能量 (Significance)": (
            "東北方是全屋最神聖的方位，"
            "為宇宙正能量（Cosmic Prāṇa）的入口。"
            "由濕婆之化身伊舍那天守護，"
            "連結木星的智慧與吉祥能量，"
            "是靈性成長與開悟的源頭。"
        ),
    },
]

# ---------- 額外 8 個子方位（16 方位版本追加） ----------

_VASTU_DATA_SUB8: list[dict[str, str]] = [
    {
        "方向 (Direction)": "East-NorthEast / 東偏東北 (Pūrva-Īśānya)",
        "主宰神祇 (Deity)": "Āditya（阿底提耶／太陽神群）",
        "五大元素 (Element)": "空 / 火 過渡區",
        "關聯行星 (Planet)": "太陽 (Sun)",
        "推薦顏色 (Colors)": "淺黃色、金色",
        "推薦材質 (Materials)": "玻璃、輕質木材",
        "適合房間與用途 (Suitable Rooms)": "晨間瑜伽區、閱讀角落",
        "嚴格避免事項 (Avoid)": "避免設置重物或暗室",
        "傳統意義與能量 (Significance)": "社交與人際關係能量的匯聚處，適合交流活動。",
    },
    {
        "方向 (Direction)": "East-SouthEast / 東偏東南 (Pūrva-Āgneya)",
        "主宰神祇 (Deity)": "Agni-Pūrva（東方火神面向）",
        "五大元素 (Element)": "火（強烈）",
        "關聯行星 (Planet)": "金星 (Venus)",
        "推薦顏色 (Colors)": "橘紅色、珊瑚色",
        "推薦材質 (Materials)": "陶瓷、紅磚",
        "適合房間與用途 (Suitable Rooms)": "電器設備間、暖氣設備",
        "嚴格避免事項 (Avoid)": "避免水池或水景",
        "傳統意義與能量 (Significance)": "與健康活力密切相關的火性能量區域。",
    },
    {
        "方向 (Direction)": "South-SouthEast / 南偏東南 (Dakṣiṇa-Āgneya)",
        "主宰神祇 (Deity)": "Agni-Dakṣiṇa（南方火神面向）",
        "五大元素 (Element)": "火 / 土 過渡區",
        "關聯行星 (Planet)": "火星 (Mars)",
        "推薦顏色 (Colors)": "深紅色、棕色",
        "推薦材質 (Materials)": "紅土、花崗岩",
        "適合房間與用途 (Suitable Rooms)": "儲藏室、工具間",
        "嚴格避免事項 (Avoid)": "不宜設為臥室或起居室",
        "傳統意義與能量 (Significance)": "自信與勇氣的能量來源區域。",
    },
    {
        "方向 (Direction)": "South-SouthWest / 南偏西南 (Dakṣiṇa-Nairṛtya)",
        "主宰神祇 (Deity)": "Nirṛti-Dakṣiṇa（南方尼律提面向）",
        "五大元素 (Element)": "土（強烈）",
        "關聯行星 (Planet)": "羅睺 (Rahu)",
        "推薦顏色 (Colors)": "深棕色、暗紅色",
        "推薦材質 (Materials)": "厚重石材、混凝土",
        "適合房間與用途 (Suitable Rooms)": "廢棄物處理區、重型倉庫",
        "嚴格避免事項 (Avoid)": "嚴禁地面下沉或空置",
        "傳統意義與能量 (Significance)": "需要穩固的錨定能量，保持厚重。",
    },
    {
        "方向 (Direction)": "West-SouthWest / 西偏西南 (Paścima-Nairṛtya)",
        "主宰神祇 (Deity)": "Nirṛti-Paścima（西方尼律提面向）",
        "五大元素 (Element)": "土 / 水 過渡區",
        "關聯行星 (Planet)": "土星 (Saturn)",
        "推薦顏色 (Colors)": "深藍色、灰色",
        "推薦材質 (Materials)": "金屬、深色石材",
        "適合房間與用途 (Suitable Rooms)": "學習室、研究室",
        "嚴格避免事項 (Avoid)": "不宜過於明亮或空曠",
        "傳統意義與能量 (Significance)": "與教育、知識儲備有關的沉穩能量。",
    },
    {
        "方向 (Direction)": "West-NorthWest / 西偏西北 (Paścima-Vāyavya)",
        "主宰神祇 (Deity)": "Vāyu-Paścima（西方風神面向）",
        "五大元素 (Element)": "水 / 風 過渡區",
        "關聯行星 (Planet)": "月亮 (Moon)",
        "推薦顏色 (Colors)": "銀色、淺灰色",
        "推薦材質 (Materials)": "輕金屬、竹子",
        "適合房間與用途 (Suitable Rooms)": "儲物間、衣帽間、洗衣房",
        "嚴格避免事項 (Avoid)": "避免作為長期居住空間",
        "傳統意義與能量 (Significance)": "存儲與整理的能量流動區域。",
    },
    {
        "方向 (Direction)": "North-NorthWest / 北偏西北 (Uttara-Vāyavya)",
        "主宰神祇 (Deity)": "Vāyu-Uttara（北方風神面向）",
        "五大元素 (Element)": "風 / 水 過渡區",
        "關聯行星 (Planet)": "水星 (Mercury)",
        "推薦顏色 (Colors)": "淺綠色、薄荷色",
        "推薦材質 (Materials)": "玻璃、淺色木材",
        "適合房間與用途 (Suitable Rooms)": "社交空間、接待室、客廳",
        "嚴格避免事項 (Avoid)": "不宜放重型設備",
        "傳統意義與能量 (Significance)": "人際關係與銀行事務相關的流動能量。",
    },
    {
        "方向 (Direction)": "North-NorthEast / 北偏東北 (Uttara-Īśānya)",
        "主宰神祇 (Deity)": "Soma（蘇摩／月神）",
        "五大元素 (Element)": "水 / 空 過渡區",
        "關聯行星 (Planet)": "木星 (Jupiter)",
        "推薦顏色 (Colors)": "白色、淺金色、象牙色",
        "推薦材質 (Materials)": "大理石、水晶",
        "適合房間與用途 (Suitable Rooms)": "冥想室、水井、水塔（小型）",
        "嚴格避免事項 (Avoid)": "嚴禁任何汙染源",
        "傳統意義與能量 (Significance)": "最神聖的子方位，醫療治癒與淨化能量集中處。",
    },
]

# ---------- 中央 Brahmasthan 資料 ----------

_BRAHMASTHAN_INFO: str = textwrap.dedent("""\
    ╔═══════════════════════════════════════════════════════════════════╗
    ║               🙏 中央 — Brahmasthan（梵天位）                   ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  梵文名稱：Brahmasthan / Brahma Sthāna                         ║
    ║  主宰神祇：Brahmā（梵天 — 宇宙創造之神）                       ║
    ║  五大元素：空 / 以太 (Ākāśa) — 五大元素的交匯點                ║
    ║  關聯行星：所有九曜之核心（尤其太陽 Sūrya）                     ║
    ║                                                                   ║
    ║  📐 說明：                                                       ║
    ║  Brahmasthan 是建築物正中央的區域，約佔全屋面積的 1/9。         ║
    ║  此處是宇宙能量（Cosmic Prāṇa）的中心匯聚點，                  ║
    ║  等同於人體的心輪（Anāhata Chakra）位置。                       ║
    ║                                                                   ║
    ║  ✅ 應保持：                                                     ║
    ║     • 完全開闊、空曠、潔淨                                       ║
    ║     • 最好是天井、中庭或開放空間                                  ║
    ║     • 可放置小型銅製或黃金 Vastu Yantra                          ║
    ║     • 適合設置水晶或天然植物                                      ║
    ║                                                                   ║
    ║  ❌ 嚴格禁止：                                                   ║
    ║     • 不可設置柱子、樑柱穿過                                      ║
    ║     • 不可建造樓梯                                                ║
    ║     • 不可設置廁所或廚房                                          ║
    ║     • 不可放置重型家具或地下室                                    ║
    ║     • 不可設牆壁隔斷此區域                                        ║
    ║                                                                   ║
    ║  🕉️ 傳統意義：                                                   ║
    ║  Brahmasthan 代表整棟建築的「生命核心」。                        ║
    ║  古典經典 Mayamata 明確指出，此區域若受到干擾，                  ║
    ║  將導致居住者健康衰退、家庭不和與財運受損。                      ║
    ║  保持其開闊純淨，則宇宙能量能均勻分佈至八大方位。               ║
    ╚═══════════════════════════════════════════════════════════════════╝
""")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║              第二部分：Vastu 表格輸出函數                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def detailed_vastu_table(directions: int = 8) -> None:
    """產生超詳細的 Vastu Shastra 方位表格並列印至終端。

    Args:
        directions: 顯示 ``8`` 大方位或 ``16`` 方位版本（含子方位）。
            預設為 8。

    Raises:
        ValueError: 若 ``directions`` 不是 8 或 16。

    Example::

        detailed_vastu_table()        # 8 方位
        detailed_vastu_table(16)      # 16 方位
    """
    if directions not in (8, 16):
        raise ValueError("directions 參數僅接受 8 或 16。")

    data = list(_VASTU_DATA_8)
    if directions == 16:
        # 將子方位穿插至主方位之間以呈現順時針排列
        merged: list[dict[str, str]] = []
        # 順時針 16 方位排列：
        # E, ENE, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW, N, NNE, NE
        order_main = [0, 1, 2, 3, 4, 5, 6, 7]  # 八大方位在 _VASTU_DATA_8 的索引
        order_sub = [0, 1, 2, 3, 4, 5, 6, 7]    # 子方位在 _VASTU_DATA_SUB8 的索引
        # 完整順時針：E, ENE, ESE, SE, SSE, SSW, S, SSW, SW, WSW, W, WNW, NW, NNW, N, NNE, NE
        # 對應穿插邏輯：每個主方位後接一個子方位
        for i in range(8):
            merged.append(_VASTU_DATA_8[order_main[i]])
            merged.append(_VASTU_DATA_SUB8[order_sub[i]])
        data = merged

    df = pd.DataFrame(data)

    # 用 textwrap 把長文字自動換行（方便窄終端閱讀）
    wrap_width = 30
    for col in df.columns:
        df[col] = df[col].apply(lambda x: "\n".join(textwrap.wrap(str(x), wrap_width)))

    title = f"🕉️  Vastu Shastra {'十六' if directions == 16 else '八大'}方位詳解表"
    separator = "═" * 60
    print(f"\n{separator}")
    print(f"  {title}")
    print(f"{separator}\n")

    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
            stralign="left",
        )
    )

    # 附加中央 Brahmasthan 說明
    print(f"\n{_BRAHMASTHAN_INFO}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║              第三部分：Jyotish ↔ Vastu 對應映射                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# 星座 → 中文名稱
_ZODIAC_ZH: dict[str, str] = {
    "Aries": "牡羊座 (Meṣa)",
    "Taurus": "金牛座 (Vṛṣabha)",
    "Gemini": "雙子座 (Mithuna)",
    "Cancer": "巨蟹座 (Karkaṭa)",
    "Leo": "獅子座 (Siṃha)",
    "Virgo": "處女座 (Kanyā)",
    "Libra": "天秤座 (Tulā)",
    "Scorpio": "天蠍座 (Vṛścika)",
    "Sagittarius": "射手座 (Dhanus)",
    "Capricorn": "摩羯座 (Makara)",
    "Aquarius": "水瓶座 (Kumbha)",
    "Pisces": "雙魚座 (Mīna)",
}

# 行星 → 中文名稱
_PLANET_ZH: dict[str, str] = {
    "Sun": "太陽 (Sūrya)",
    "Moon": "月亮 (Chandra)",
    "Mars": "火星 (Maṅgala)",
    "Mercury": "水星 (Budha)",
    "Jupiter": "木星 (Bṛhaspati)",
    "Venus": "金星 (Śukra)",
    "Saturn": "土星 (Śani)",
    "Rahu": "羅睺 (Rāhu)",
    "Ketu": "計都 (Ketu)",
}

# 行星 → Vastu 方位（傳統 Jyotish-Vastu 對應）
_PLANET_DIRECTION: dict[str, str] = {
    "Sun": "東方 (East)",
    "Moon": "西北 (North-West)",
    "Mars": "南方 (South)",
    "Mercury": "北方 (North)",
    "Jupiter": "東北 (North-East)",
    "Venus": "東南 (South-East)",
    "Saturn": "西方 (West)",
    "Rahu": "西南 (South-West)",
    "Ketu": "西南偏南 (South-SouthWest)",
}

# 星座元素分類
_SIGN_ELEMENT: dict[str, str] = {
    "Aries": "火", "Leo": "火", "Sagittarius": "火",
    "Taurus": "土", "Virgo": "土", "Capricorn": "土",
    "Gemini": "風", "Libra": "風", "Aquarius": "風",
    "Cancer": "水", "Scorpio": "水", "Pisces": "水",
}

# Lagna（上升星座）→ 推薦房屋朝向
_LAGNA_FACING: dict[str, str] = {
    "Aries": "東方 — 火象上升適合迎接晨曦能量",
    "Taurus": "北方 — 金牛上升需穩定財運能量",
    "Gemini": "北方 — 風象上升適合北方流動能量",
    "Cancer": "東方 — 水象上升受益於東方的 Prāṇa",
    "Leo": "東方 — 太陽主宰，面東迎日最吉",
    "Virgo": "北方 — 水星主宰，北方為水星方位",
    "Libra": "西方 — 金星主宰，西方為社交方位",
    "Scorpio": "南方 — 火星主宰，南方能量穩固",
    "Sagittarius": "東北 — 木星主宰，東北為最靈性方位",
    "Capricorn": "西方或南方 — 土星主宰，沉穩方位為佳",
    "Aquarius": "西方或北方 — 土星共主，風象需流動空間",
    "Pisces": "東北 — 木星主宰，靈性能量最強方位",
}

# Lagna → Vastu 個人化建議細節
_LAGNA_VASTU_DETAILS: dict[str, dict[str, str]] = {
    "Aries": {
        "大門位置": "東方或東北方",
        "主臥室": "南方或西南方",
        "財位 (Kubera Sthana)": "北方 — 放置保險箱或財務文件",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "南方或東方",
        "加強區域": "東方 — 加強太陽能量有利領導力",
        "避開區域": "西南方不宜有水元素",
    },
    "Taurus": {
        "大門位置": "北方或東方",
        "主臥室": "西南方 — 金牛上升需穩固根基",
        "財位 (Kubera Sthana)": "北方 — 金星與財富的連結方位",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "南方或西方",
        "加強區域": "東南方 — 加強金星能量有利感情與財富",
        "避開區域": "西北方不宜放重物",
    },
    "Gemini": {
        "大門位置": "北方",
        "主臥室": "西方或西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "東方或南方",
        "加強區域": "北方 — 水星方位，加強溝通與智慧",
        "避開區域": "東南方不宜有過多風元素",
    },
    "Cancer": {
        "大門位置": "東方或北方",
        "主臥室": "西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方 — 水象上升更需靈性空間",
        "廚房": "東南方",
        "床頭朝向": "東方",
        "加強區域": "西北方 — 月亮方位，加強情感安穩",
        "避開區域": "南方不宜有水池",
    },
    "Leo": {
        "大門位置": "東方 — 太陽方位，最為吉祥",
        "主臥室": "西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "東方 — 面向太陽升起的方向",
        "加強區域": "東方 — 太陽能量帶來權威與名望",
        "避開區域": "西北方不宜設為主要活動區",
    },
    "Virgo": {
        "大門位置": "北方",
        "主臥室": "西南方或南方",
        "財位 (Kubera Sthana)": "北方 — 水星主宰的財富方位",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "南方或東方",
        "加強區域": "北方 — 水星能量促進分析力與事業",
        "避開區域": "西南方不宜放電器",
    },
    "Libra": {
        "大門位置": "西方或北方",
        "主臥室": "西南方 — 金星能量帶來和諧",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "西方或南方",
        "加強區域": "東南方 — 金星方位，增進美感與關係",
        "避開區域": "正南方大門應避免",
    },
    "Scorpio": {
        "大門位置": "南方或東方",
        "主臥室": "西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方 — 轉化天蠍的深層能量",
        "廚房": "東南方",
        "床頭朝向": "南方",
        "加強區域": "南方 — 火星能量帶來勇氣與轉化力",
        "避開區域": "東北方不宜有任何汙染",
    },
    "Sagittarius": {
        "大門位置": "東北方 — 木星方位，最為吉祥",
        "主臥室": "西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方 — 木星雙重加持",
        "廚房": "東南方",
        "床頭朝向": "東方或南方",
        "加強區域": "東北方 — 木星能量帶來智慧與好運",
        "避開區域": "西南方不宜有火元素",
    },
    "Capricorn": {
        "大門位置": "西方或南方",
        "主臥室": "西南方 — 土星穩固能量",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "南方或西方",
        "加強區域": "西方 — 土星方位，增強紀律與長壽",
        "避開區域": "東方不宜有土星屬性物品（如鐵器）",
    },
    "Aquarius": {
        "大門位置": "西方或北方",
        "主臥室": "西南方或西方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方",
        "廚房": "東南方",
        "床頭朝向": "南方",
        "加強區域": "西方與北方 — 土星與風象能量的結合",
        "避開區域": "東南方不宜有過多金屬",
    },
    "Pisces": {
        "大門位置": "東北方 — 木星的靈性入口",
        "主臥室": "西南方",
        "財位 (Kubera Sthana)": "北方",
        "祈禱室 (Pūjā Room)": "東北方 — 雙魚的靈性天賦在此綻放",
        "廚房": "東南方",
        "床頭朝向": "東方",
        "加強區域": "東北方 — 加強靈性直覺與冥想深度",
        "避開區域": "南方不宜有水元素衝突",
    },
}


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║          第四部分：個人化 Astro-Vastu 推薦函數                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def _format_vedastro_time(birth_date: str, birth_time: str, utc_offset: str) -> str:
    """將出生日期、時間格式化為 VedAstro 接受的字串格式。

    VedAstro Time 格式：``"HH:MM DD/MM/YYYY +HH:MM"``

    Args:
        birth_date: 出生日期，格式 ``YYYY-MM-DD``。
        birth_time: 出生時間，格式 ``HH:MM``。
        utc_offset: UTC 偏移量，例如 ``"+08:00"``。

    Returns:
        VedAstro 格式的時間字串。
    """
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    return f"{dt.strftime('%H:%M')} {dt.strftime('%d/%m/%Y')} {utc_offset}"


def _longitude_to_utc_offset(longitude: float) -> str:
    """根據經度估算 UTC 偏移量。

    這是一個簡化估算，每 15° 經度對應 1 小時。
    實際時區可能因國家政策而異。

    Args:
        longitude: 經度（東經為正，西經為負）。

    Returns:
        UTC 偏移量字串，如 ``"+08:00"``。
    """
    offset_hours = round(longitude / 15)
    sign = "+" if offset_hours >= 0 else "-"
    abs_hours = abs(offset_hours)
    return f"{sign}{abs_hours:02d}:00"


def _get_fallback_lagna(birth_time: str) -> str:
    """根據出生時間粗略推估上升星座（Fallback 用途）。

    這是極度簡化的推估方法，僅在 VedAstro 不可用時使用。
    實際上升星座取決於精確的出生時間、日期與地點。

    Args:
        birth_time: 出生時間，格式 ``HH:MM``。

    Returns:
        粗略推估的星座英文名稱。
    """
    hour = int(birth_time.split(":")[0])
    # 粗略分配：每 2 小時一個星座（從日出約 6:00 開始）
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    # 假設 6:00 日出為 Aries，每 2 小時推進
    index = ((hour - 6) % 24) // 2
    return signs[index % 12]


def _build_planet_table(planet_data: list[dict[str, str]]) -> str:
    """將行星資料列表格式化為美觀表格字串。

    Args:
        planet_data: 行星資訊字典列表。

    Returns:
        使用 tabulate 格式化的表格字串。
    """
    df = pd.DataFrame(planet_data)
    return tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False, stralign="left")


def personalized_astro_vastu(
    name: str,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    latitude: float,
    longitude: float,
    utc_offset: Optional[str] = None,
) -> None:
    """根據個人出生資料，結合吠陀占星命盤產生個人化 Vastu 建議。

    優先使用 VedAstro 庫計算精確命盤。若 VedAstro 未安裝或 API 呼叫失敗，
    將使用簡化的 fallback 推估方法並提示使用者。

    Args:
        name: 使用者姓名。
        birth_date: 出生日期，格式 ``YYYY-MM-DD``。
        birth_time: 出生時間，格式 ``HH:MM``（24 小時制）。
        birth_place: 出生地點名稱（用於顯示）。
        latitude: 出生地緯度。
        longitude: 出生地經度（東經為正）。
        utc_offset: UTC 偏移量，例如 ``"+08:00"``。
            若未提供，將根據經度自動估算。

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
    if utc_offset is None:
        utc_offset = _longitude_to_utc_offset(longitude)

    separator = "═" * 64
    print(f"\n{separator}")
    print("  🪐 個人化 Astro-Vastu 命盤分析報告")
    print(separator)
    print(f"  姓名：{name}")
    print(f"  出生日期：{birth_date}")
    print(f"  出生時間：{birth_time}")
    print(f"  出生地點：{birth_place}（{latitude}°N, {longitude}°E）")
    print(f"  UTC 偏移：{utc_offset}")
    print(separator)

    lagna_sign: str = ""
    moon_sign: str = ""
    planet_info: list[dict[str, str]] = []
    used_vedastro: bool = False

    if _VEDASTRO_AVAILABLE:
        try:
            geo = GeoLocation(birth_place, longitude, latitude)
            time_str = _format_vedastro_time(birth_date, birth_time, utc_offset)
            birth_time_obj = Time(time_str, geo)

            # 取得 Lagna（上升星座）
            lagna_result = Calculate.LagnaSignName(birth_time_obj)
            lagna_sign = str(lagna_result).strip()
            # 清理可能的格式問題
            for zn in _ZODIAC_ZH:
                if zn.lower() in lagna_sign.lower():
                    lagna_sign = zn
                    break

            # 取得 Moon Sign（月亮星座）
            moon_result = Calculate.MoonSignName(birth_time_obj)
            moon_sign = str(moon_result).strip()
            for zn in _ZODIAC_ZH:
                if zn.lower() in moon_sign.lower():
                    moon_sign = zn
                    break

            # 取得各行星所在星座與力量
            planets = [
                PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
                PlanetName.Mercury, PlanetName.Jupiter,
                PlanetName.Venus, PlanetName.Saturn,
                PlanetName.Rahu, PlanetName.Ketu,
            ]
            planet_names_en = [
                "Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu",
            ]

            for p_obj, p_name in zip(planets, planet_names_en):
                try:
                    sign_result = Calculate.PlanetRasiD1Sign(p_obj, birth_time_obj)
                    sign_str = str(sign_result).strip()
                    matched_sign = sign_str
                    for zn in _ZODIAC_ZH:
                        if zn.lower() in sign_str.lower():
                            matched_sign = zn
                            break

                    # 嘗試取得行星力量
                    strength_str = "—"
                    try:
                        strength_result = Calculate.PlanetPowerPercentage(
                            p_obj, birth_time_obj
                        )
                        strength_str = str(strength_result).strip()
                    except Exception:
                        pass

                    planet_info.append({
                        "行星": _PLANET_ZH.get(p_name, p_name),
                        "所在星座": _ZODIAC_ZH.get(matched_sign, matched_sign),
                        "Vastu 方位": _PLANET_DIRECTION.get(p_name, "—"),
                        "力量": strength_str,
                    })
                except Exception:
                    planet_info.append({
                        "行星": _PLANET_ZH.get(p_name, p_name),
                        "所在星座": "（計算中出現問題）",
                        "Vastu 方位": _PLANET_DIRECTION.get(p_name, "—"),
                        "力量": "—",
                    })

            used_vedastro = True
            print("\n  ✅ 已使用 VedAstro 庫進行精確吠陀計算（Lahiri Ayanamsa）。\n")

        except Exception as e:
            print(f"\n  ⚠️  VedAstro API 呼叫失敗：{e}")
            print("      將使用簡化推估方法作為替代。\n")
            _VEDASTRO_AVAILABLE_LOCAL = False
    else:
        _VEDASTRO_AVAILABLE_LOCAL = False

    if not used_vedastro:
        if not _VEDASTRO_AVAILABLE:
            print("\n  ⚠️  VedAstro 庫未安裝。請執行以下命令安裝：")
            print("      pip install vedastro")
            print("      安裝後即可獲得精確的吠陀占星計算。\n")
            print("  📌 目前使用簡化推估方法（僅供參考，精度有限）。\n")

        # Fallback：簡化推估
        lagna_sign = _get_fallback_lagna(birth_time)
        # Fallback 月亮星座：根據出生月份粗略推估
        month = int(birth_date.split("-")[1])
        moon_signs_by_month = [
            "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini",
            "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
        ]
        moon_sign = moon_signs_by_month[(month - 1) % 12]

        # Fallback 行星資料：只提供方位對應
        planet_names_en = [
            "Sun", "Moon", "Mars", "Mercury", "Jupiter",
            "Venus", "Saturn", "Rahu", "Ketu",
        ]
        for p_name in planet_names_en:
            planet_info.append({
                "行星": _PLANET_ZH.get(p_name, p_name),
                "所在星座": "（需 VedAstro 精確計算）",
                "Vastu 方位": _PLANET_DIRECTION.get(p_name, "—"),
                "力量": "—",
            })

    # ---------- 顯示命盤摘要 ----------
    lagna_zh = _ZODIAC_ZH.get(lagna_sign, lagna_sign)
    moon_zh = _ZODIAC_ZH.get(moon_sign, moon_sign)
    lagna_element = _SIGN_ELEMENT.get(lagna_sign, "未知")

    print(f"  🔮 上升星座（Lagna / Ascendant）：{lagna_zh}")
    print(f"  🌙 月亮星座（Moon Rāśi）：{moon_zh}")
    print(f"  🜂 上升元素屬性：{lagna_element}象")
    print()

    # ---------- 行星位置表 ----------
    print("  📊 九曜行星位置與 Vastu 對應：\n")
    if planet_info:
        print(_build_planet_table(planet_info))
    print()

    # ---------- 個人化 Vastu 建議 ----------
    print(separator)
    print("  🏠 個人化 Vastu Shastra 建議")
    print(separator)

    facing = _LAGNA_FACING.get(lagna_sign, "東方 — 通用推薦方位")
    print(f"\n  🧭 房屋推薦朝向：{facing}\n")

    details = _LAGNA_VASTU_DETAILS.get(lagna_sign, _LAGNA_VASTU_DETAILS["Aries"])
    recommendation_data = [
        {"建議項目": key, "詳細說明": value}
        for key, value in details.items()
    ]
    df_rec = pd.DataFrame(recommendation_data)
    print(
        tabulate(
            df_rec,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
            stralign="left",
        )
    )

    # ---------- 根據月亮星座的額外建議 ----------
    moon_element = _SIGN_ELEMENT.get(moon_sign, "未知")
    print(f"\n  🌙 月亮星座額外建議（基於月亮在 {moon_zh} 的位置）：\n")

    moon_tips: dict[str, str] = {
        "火": (
            "月亮在火象星座：情緒活躍，適合在南方或東方放置\n"
            "      舒緩系色調（藍色、白色）的裝飾品以平衡火性能量。\n"
            "      臥室宜避免過多紅色或橘色。"
        ),
        "土": (
            "月亮在土象星座：情緒穩定，適合在西南方加強\n"
            "      根基能量。可在北方放置綠色植物增添生機。\n"
            "      家中宜多使用天然石材與木質材料。"
        ),
        "風": (
            "月亮在風象星座：思緒活躍，需在北方設置安靜的\n"
            "      閱讀或冥想空間。避免家中過多的風鈴或流動裝飾。\n"
            "      東北方可放置水晶以穩定心智。"
        ),
        "水": (
            "月亮在水象星座：直覺敏銳但情緒起伏大，\n"
            "      東北方的祈禱室對您格外重要。\n"
            "      西北方可放置銀色或白色物品以安撫月亮能量。\n"
            "      避免家中有漏水或積水現象。"
        ),
    }
    print(f"      {moon_tips.get(moon_element, '請參考一般 Vastu 建議。')}")

    # ---------- 綜合能量分析 ----------
    print(f"\n{separator}")
    print("  ⚡ 綜合能量分析與特別提醒")
    print(separator)

    energy_notes: list[str] = [
        f"1. 您的上升星座為 {lagna_zh}，Vastu 上最重要的方位是"
        f"「{_PLANET_DIRECTION.get(_get_lagna_ruler(lagna_sign), '東北')}」"
        f"（{_PLANET_ZH.get(_get_lagna_ruler(lagna_sign), '')} 主宰方位）。",
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

    if not used_vedastro:
        print("\n  💡 溫馨提示：以上結果基於簡化推估。")
        print("     建議安裝 VedAstro（pip install vedastro）以獲得")
        print("     精確的吠陀占星計算與更準確的個人化建議。")

    print("\n  🙏 Om Vastu Devaya Namah | 願 Vastu 之神保佑您的居所平安吉祥 🙏")
    print(f"{separator}\n")


def _get_lagna_ruler(lagna_sign: str) -> str:
    """取得上升星座的主宰行星。

    Args:
        lagna_sign: 星座英文名稱。

    Returns:
        主宰行星的英文名稱。
    """
    rulers: dict[str, str] = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter",
    }
    return rulers.get(lagna_sign, "Jupiter")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      主程式入口 / 使用範例                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def main() -> None:
    """主程式入口：展示 Vastu 表格與個人化推薦範例。"""

    print("\n" + "★" * 64)
    print("  歡迎使用 astro_vastu_pro — 超級進階 Astro-Vastu 模組")
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
