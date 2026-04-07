# 🕉️ astro_vastu — 超級進階 Astro-Vastu 模組

> 結合 **Vastu Shastra**（印度建築風水）與 **Vedic Jyotish**（吠陀占星），提供八大方位 / 十六方位的 Vastu 詳解表格，以及根據個人命盤的個人化居家風水建議。

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📦 安裝

```bash
# 必要依賴
pip install pandas tabulate

# 可選：精確吠陀占星計算（VedAstro）
pip install vedastro
```

## 🖥️ Streamlit 互動介面

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

啟動後瀏覽器會自動開啟，提供兩大功能：

| 功能 | 說明 |
|------|------|
| 🏛️ Vastu 方位表格 | 瀏覽八大 / 十六方位 Vastu Shastra 詳解表 |
| 🪐 個人化 Astro-Vastu | 輸入出生資料，取得個人化風水命盤分析報告 |

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

# 停用占星計算（純 Fallback 模式）
personalized_astro_vastu(
    name="王小明",
    birth_date="1990-05-15",
    birth_time="08:30",
    birth_place="臺北",
    latitude=25.033,
    longitude=121.565,
    use_astro=False,
)
```

## 📁 專案結構

```
requirements.txt           # Python 依賴清單
streamlit_app.py           # Streamlit 互動介面入口
astro_vastu/
├── __init__.py            # 套件入口、版本資訊、相容性重新匯出
├── config.py              # 全域設定（AppSettings dataclass）
├── exceptions.py          # 自訂例外類別
├── personalized.py        # personalized_astro_vastu() 主函數
├── main.py                # 示範入口（保留原 main() 功能）
├── core/                  # 核心 Vastu 靜態資料與表格
│   ├── vastu_data.py      # 8+16 方位資料，支援從 JSON 載入
│   ├── vastu_table.py     # detailed_vastu_table()，支援 console / DataFrame
│   └── brahmasthan.py     # 中央梵天位詳細說明
├── astro/                 # 吠陀占星模組（可選）
│   ├── calculator.py      # 封裝 VedAstro，含優雅 fallback
│   └── mappings.py        # 星座、行星、方位對應表
├── models/                # 資料模型
│   └── config.py          # BirthData / VastuReportConfig dataclass
├── utils/                 # 工具函數
│   ├── time_utils.py      # zoneinfo 時區處理、輸入驗證
│   └── formatters.py      # 表格格式化工具
└── data/                  # 靜態資料檔案
    └── vastu_directions.json  # 方位資料（可外部更新）
```

## 🔄 從 v1 遷移

v2.0.0 保持向後相容。原有的呼叫方式繼續有效：

```python
# v1 舊方式（仍然有效）
from astro_vastu import detailed_vastu_table, personalized_astro_vastu

# v2 新方式（更精確的匯入路徑）
from astro_vastu.core.vastu_table import detailed_vastu_table
from astro_vastu.personalized import personalized_astro_vastu
```

### v2 新增功能

| 功能 | 說明 |
|------|------|
| `use_astro` 參數 | 可完全停用占星計算，避免依賴問題 |
| `timezone` 參數 | 使用 IANA 時區精確處理夏令時 |
| `output="dataframe"` | `detailed_vastu_table()` 可回傳 DataFrame |
| JSON 資料載入 | Vastu 資料可從外部 JSON 更新 |
| 輸入驗證 | 日期、時間、經緯度的完整驗證 |
| 自訂例外 | `InvalidDateError` / `InvalidTimeError` 等 |
| 型別提示 | 完整的 Python 型別標註 |

## 📚 參考經典

- **Mayamata**（摩耶論）
- **Manasara**（摩那薩羅）
- **Brihat Samhita**（大合集論）
- **Vastu Ratnakara**（Vastu 寶鑑）
- **Brihat Parashara Hora Shastra**（帕拉夏拉大時論）

## 📄 授權

MIT License © KinVastu 團隊
