# 🕉️ 堅瓦斯圖 Kinvastu — 印度吠陀風水

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![GitHub stars](https://img.shields.io/github/stars/kentang2017/kinvastu?style=social)](https://github.com/kentang2017/kinvastu)

> 結合 **Vastu Shastra**（印度建築風水）與 **Vedic Jyotish**（吠陀占星），提供八大方位 / 十六方位的 Vastu 詳解表格，以及根據個人命盤的個人化居家風水建議。

---

## 📑 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Live Demo](#-live-demo)
- [安裝](#-安裝)
- [Streamlit 互動介面](#️-streamlit-互動介面)
- [快速開始](#-快速開始)
- [專案結構](#-專案結構)
- [從 v1 遷移](#-從-v1-遷移)
- [作者其他 Kin 系列專案](#-作者其他-kin-系列專案)
- [參考經典](#-參考經典)
- [授權](#-授權)

---

## ✨ Features

| 功能 | 說明 |
|------|------|
| 🏛️ **Vastu 方位表格** | 八大 / 十六方位 Vastu Shastra 詳解表，含 Emoji 視覺化與 CSV 匯出 |
| 🪐 **個人化 Astro-Vastu** | 輸入出生資料，取得個人化風水命盤分析報告 |
| 🏠 **房屋風水診斷** | 輸入房屋朝向，產生 Dosha 衝突檢測與顏色警示 |
| 🛋️ **房間配置建議** | 基於命盤的最佳房間擺設與補救方法 |
| 📊 **Vastu Compliance Score** | 0-100 分的 Vastu 合規評分 |
| 🙏 **Brahmasthan 診斷** | 獨立的中央梵天位分析區塊 |
| 🕉️ **Vastu Purusha Mandala** | 9 宮格 + 32 外環天神位互動圖表 |
| 🔗 **Kin 系列入口** | 整合作者所有術數工具的快速連結 |
| 🌙 **Dark Theme** | 適合印度風水的橘金色深色主題 |

---

## 📸 Screenshots

> *截圖即將更新 — 以下為 placeholder*

| Vastu 方位表格 | 個人化 Astro-Vastu |
|:-:|:-:|
| ![Vastu Table](https://via.placeholder.com/400x250/0E1117/FF9933?text=Vastu+Table) | ![Astro-Vastu](https://via.placeholder.com/400x250/0E1117/FF9933?text=Astro-Vastu) |

| Vastu Purusha Mandala | Kin 系列工具 |
|:-:|:-:|
| ![Mandala](https://via.placeholder.com/400x250/0E1117/FF9933?text=Mandala) | ![Kin Series](https://via.placeholder.com/400x250/0E1117/FF9933?text=Kin+Series) |

---

## 🌐 Live Demo

> 若已部署 Streamlit Cloud，請將下方連結替換為實際 URL：

🔗 **[點此開啟 Kinvastu 線上版](https://kinvastu.streamlit.app)**

---

## 📦 安裝

```bash
# 基本安裝（僅核心功能）
pip install pandas tabulate

# 精確占星計算
pip install pyswisseph

# 現代化安裝（使用 pyproject.toml）
pip install .               # 基本安裝
pip install ".[astro]"       # 含占星計算
pip install ".[streamlit]"   # 含 Streamlit 介面
```

## 🖥️ Streamlit 互動介面

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

啟動後瀏覽器會自動開啟，提供三大功能：

| Tab | 功能 | 說明 |
|-----|------|------|
| 🏛️ | Vastu 方位表格 | 瀏覽八大 / 十六方位 Vastu Shastra 詳解表，支援 CSV 匯出 |
| 🪐 | 個人化 Astro-Vastu | 輸入出生資料與房屋朝向，取得完整個人化風水命盤分析報告 |
| 🔗 | Kin 系列工具 | 瀏覽作者所有東西方術數系統的開源工具 |

## 🚀 快速開始

```python
from astro_vastu import detailed_vastu_table, personalized_astro_vastu

# 顯示八方位 Vastu 表格
detailed_vastu_table(directions=8)

# 顯示十六方位 Vastu 表格
detailed_vastu_table(directions=16)

# 取得 DataFrame 格式
df = detailed_vastu_table(directions=8, output="dataframe")

# 個人化 Astro-Vastu 推薦
personalized_astro_vastu(
    name="王小明",
    birth_date="1990-05-15",
    birth_time="08:30",
    birth_place="臺北",
    latitude=25.033,
    longitude=121.565,
)

# 使用 IANA 時區（精確處理夏令時）
personalized_astro_vastu(
    name="王小明",
    birth_date="1990-05-15",
    birth_time="08:30",
    birth_place="臺北",
    latitude=25.033,
    longitude=121.565,
    timezone="Asia/Taipei",
)

# 房間配置建議
from astro_vastu import room_placement_recommendations
recommendations = room_placement_recommendations("Aries")
```

## 📁 專案結構

```
.streamlit/config.toml     # Streamlit dark theme 設定
pyproject.toml             # 現代 Python 套件設定
requirements.txt           # Python 依賴清單
streamlit_app.py           # Streamlit 互動介面入口
astro_vastu/
├── __init__.py            # 套件入口、版本資訊、相容性重新匯出
├── config.py              # 全域設定（AppSettings dataclass）
├── exceptions.py          # 自訂例外類別
├── personalized.py        # personalized_astro_vastu() + room_placement_recommendations()
├── main.py                # 示範入口（保留原 main() 功能）
├── core/                  # 核心 Vastu 靜態資料與表格
│   ├── vastu_data.py      # 8+16 方位資料，支援從 JSON 載入
│   ├── vastu_table.py     # detailed_vastu_table()，支援 console / DataFrame
│   ├── vastu_chart.py     # Vastu Purusha Mandala 圖表渲染器
│   └── brahmasthan.py     # 中央梵天位詳細說明
├── astro/                 # 吠陀占星模組（可選）
│   ├── calculator.py      # 封裝 pyswisseph 吠陀占星計算，含優雅 fallback
│   └── mappings.py        # 星座、行星、方位對應表
├── models/                # 資料模型
│   └── config.py          # BirthData / VastuReportConfig dataclass
├── utils/                 # 工具函數
│   ├── time_utils.py      # zoneinfo 時區處理、輸入驗證
│   └── formatters.py      # 表格格式化工具
└── data/                  # 靜態資料檔案
    └── vastu_directions.json  # 方位資料（含 remedies、colors、room_suggestions）
```

## 🔄 從 v1 遷移

v2.0.0 保持向後相容。原有的呼叫方式繼續有效：

```python
# v1 舊方式（仍然有效）
from astro_vastu import detailed_vastu_table, personalized_astro_vastu

# v2 新方式（更精確的匯入路徑）
from astro_vastu.core.vastu_table import detailed_vastu_table
from astro_vastu.personalized import personalized_astro_vastu
from astro_vastu.personalized import room_placement_recommendations
```

### v2 新增功能

| 功能 | 說明 |
|------|------|
| `use_astro` 參數 | 可完全停用占星計算，避免依賴問題 |
| `timezone` 參數 | 使用 IANA 時區精確處理夏令時 |
| `output="dataframe"` | `detailed_vastu_table()` 可回傳 DataFrame |
| JSON 資料載入 | Vastu 資料可從外部 JSON 更新（含 remedies、colors） |
| 房屋朝向診斷 | 新增 Dosha 衝突檢測與顏色建議 |
| 房間配置建議 | `room_placement_recommendations()` 回傳最佳擺設 |
| Vastu Score | 0-100 分的 Vastu 合規評分 |
| Brahmasthan 診斷 | 獨立的中央梵天位分析 |
| 輸入驗證 | 日期、時間、經緯度的完整驗證 |
| 自訂例外 | `InvalidDateError` / `InvalidTimeError` 等 |
| 型別提示 | 完整的 Python 型別標註 |
| Dark Theme | Streamlit 橘金色深色主題 |

---

## 🔗 作者其他 Kin 系列專案

> Kin 系列 — 涵蓋東西方多種傳統占卜與術數系統的開源工具集

| 專案 | 名稱 | 說明 | 連結 |
|:----:|------|------|:----:|
| 🪐 | **kinastro（堅占星）** | 印度吠陀占星 Vedic Jyotish 命盤計算 | [GitHub](https://github.com/kentang2017/kinastro) |
| 🚪 | **kinqimen（奇門遁甲）** | 中國傳統奇門遁甲排盤系統 | [GitHub](https://github.com/kentang2017/kinqimen) |
| 🌌 | **kintaiyi（太乙神數）** | 中國古代三式之一 — 太乙神數 | [GitHub](https://github.com/kentang2017/kintaiyi) |
| 🔮 | **kinliuren（大六壬）** | 中國古代三式之一 — 大六壬排盤 | [GitHub](https://github.com/kentang2017/kinliuren) |
| ☯️ | **ichingshifa（周易筮法）** | 周易筮法（大衍之數）數位化工具 | [GitHub](https://github.com/kentang2017/ichingshifa) |
| 🐚 | **kinifa（伊法占卜）** | 非洲 Ifá 占卜系統 256 Odù | [GitHub](https://github.com/kentang2017/kinifa) |
| 🎋 | **kinwuzhao（五兆）** | 日本陰陽道五兆占卜法 | [GitHub](https://github.com/kentang2017/kinwuzhao) |
| ⭐ | **kinketika（馬來七星擇吉）** | 馬來傳統 Ketika Tujuh 擇日 | [GitHub](https://github.com/kentang2017/kinketika) |
| 📅 | **kinbazi（八字命理）** | 中國八字命理排盤與分析 | [GitHub](https://github.com/kentang2017/kinbazi) |
| 🏔️ | **kinziwei（紫微斗數）** | 紫微斗數命盤排盤 | [GitHub](https://github.com/kentang2017/kinziwei) |
| 🧮 | **kinmeihua（梅花易數）** | 梅花易數起卦與斷卦 | [GitHub](https://github.com/kentang2017/kinmeihua) |

🔗 **[查看所有 Kin 系列專案 →](https://github.com/kentang2017)**

---

## 📚 參考經典

- **Mayamata**（摩耶論）
- **Manasara**（摩那薩羅）
- **Brihat Samhita**（大合集論）
- **Vastu Ratnakara**（Vastu 寶鑑）
- **Brihat Parashara Hora Shastra**（帕拉夏拉大時論）

## 📄 授權

MIT License © KinVastu 團隊
