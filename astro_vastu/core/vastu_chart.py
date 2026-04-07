"""Vastu Purusha Mandala 圖表渲染器。

提供 9 宮格（內部 3×3 方位區域）加上 32 外環格（外圍護法天神位）
的 Vastu Purusha Mandala 圖表渲染功能，支援個人化高亮顯示。

基於《Mayamata》與《Bṛhat Saṃhitā》的 Paramasayika（9×9）曼荼羅，
外圍 32 天神（Devatā）守護 32 方位能量場。

典型用法::

    from astro_vastu.core.vastu_chart import render_vastu_mandala_html

    html = render_vastu_mandala_html(
        lagna_sign="Aries",
        lagna_ruler="Mars",
    )
"""

from __future__ import annotations

from typing import Optional

# ---------- 行星 → Vastu 方位區域 ----------
PLANET_ZONE: dict[str, str] = {
    "Sun": "E",
    "Moon": "NW",
    "Mars": "S",
    "Mercury": "N",
    "Jupiter": "NE",
    "Venus": "SE",
    "Saturn": "W",
    "Rahu": "SW",
    "Ketu": "SW",
}

# ---------- 行星 Unicode 符號 ----------
PLANET_SYMBOL: dict[str, str] = {
    "Sun": "☉",
    "Moon": "☽",
    "Mars": "♂",
    "Mercury": "☿",
    "Jupiter": "♃",
    "Venus": "♀",
    "Saturn": "♄",
    "Rahu": "☊",
    "Ketu": "☋",
}

# ---------- 行星 → 中文名稱（圖表用簡稱） ----------
_PLANET_ZH_SHORT: dict[str, str] = {
    "Sun": "日",
    "Moon": "月",
    "Mars": "火",
    "Mercury": "水",
    "Jupiter": "木",
    "Venus": "金",
    "Saturn": "土",
    "Rahu": "羅",
    "Ketu": "計",
}

# ---------- 方位區域 → 元素背景色（外環用，較淡） ----------
_ZONE_COLORS: dict[str, str] = {
    "NW": "#E8F5E9",
    "N": "#E3F2FD",
    "NE": "#F3E5F5",
    "E": "#FFF3E0",
    "SE": "#FBE9E7",
    "S": "#EFEBE9",
    "SW": "#E8E0D8",
    "W": "#E1F5FE",
}

# ---------- 方位區域 → 元素背景色（內部宮格用，較飽和） ----------
_ZONE_COLORS_INNER: dict[str, str] = {
    "NW": "#C8E6C9",
    "N": "#BBDEFB",
    "NE": "#E1BEE7",
    "E": "#FFE0B2",
    "SE": "#FFCCBC",
    "S": "#D7CCC8",
    "SW": "#BCAAA4",
    "W": "#B3E5FC",
    "Center": "#FFF9C4",
}

# ---------- 32 外環格天神資料 ----------
# (row_0based, col_0based, sanskrit_name, chinese_name, zone_key)
_OUTER_PADAS: list[tuple[int, int, str, str, str]] = [
    # 北側（頂行，左=西北 → 右=東北）
    (0, 0, "Roga", "羅伽", "NW"),
    (0, 1, "Nāga", "那伽", "N"),
    (0, 2, "Mukhya", "穆克耶", "N"),
    (0, 3, "Bhallāṭa", "跋羅陀", "N"),
    (0, 4, "Soma", "蘇摩", "N"),
    (0, 5, "Bhujaga", "蛇神", "N"),
    (0, 6, "Aditi", "阿底提", "N"),
    (0, 7, "Diti", "底提", "N"),
    (0, 8, "Āpa", "水天", "NE"),
    # 東側（右列，行 1→7）
    (1, 8, "Āpavatsa", "水子", "E"),
    (2, 8, "Parjanya", "雨神", "E"),
    (3, 8, "Jayanta", "勝天", "E"),
    (4, 8, "Indra", "因陀羅", "E"),
    (5, 8, "Sūrya", "太陽", "E"),
    (6, 8, "Satya", "薩提耶", "E"),
    (7, 8, "Bhṛśa", "布利沙", "E"),
    # 南側（底行，右=東南 → 左=西南）
    (8, 8, "Antarikṣa", "虛空天", "SE"),
    (8, 7, "Agni", "火神", "S"),
    (8, 6, "Pūṣan", "布善", "S"),
    (8, 5, "Vitatha", "維塔塔", "S"),
    (8, 4, "Gṛhakṣata", "護宅", "S"),
    (8, 3, "Yama", "閻摩", "S"),
    (8, 2, "Gandharva", "乾闥婆", "S"),
    (8, 1, "Bhṛṅgarāja", "蜂王", "S"),
    (8, 0, "Mṛga", "鹿神", "SW"),
    # 西側（左列，行 7→1）
    (7, 0, "Pitṛgaṇa", "祖靈", "W"),
    (6, 0, "Dauv\u2019ārika", "門神", "W"),
    (5, 0, "Sugrīva", "善頸", "W"),
    (4, 0, "Puṣpadanta", "花齒", "W"),
    (3, 0, "Varuṇa", "水神", "W"),
    (2, 0, "Asura", "阿修羅", "W"),
    (1, 0, "Śoṣa", "乾燥神", "W"),
]

# ---------- 9 宮格（內部方位區域）資料 ----------
# (zone_key, zh_label, deity_zh, element, vastu_tip, css_grid_row, css_grid_col)
_INNER_ZONES: list[tuple[str, str, str, str, str, str, str]] = [
    ("NW", "西北\nVāyavya", "風神 Vāyu", "風", "客房·車庫", "2/4", "2/4"),
    ("N", "北方\nUttara", "財神 Kubera", "水", "財位·客廳", "2/4", "4/7"),
    ("NE", "東北\nĪśānya", "伊舍那天", "空", "祈禱·冥想", "2/4", "7/9"),
    ("W", "西方\nPaścima", "水神 Varuṇa", "水", "餐廳·學習", "4/7", "2/4"),
    ("Center", "中央\nBrahmasthan", "梵天 Brahmā", "以太", "保持空曠", "4/7", "4/7"),
    ("E", "東方\nPūrva", "天帝 Indra", "火", "起居·窗戶", "4/7", "7/9"),
    ("SW", "西南\nNairṛtya", "尼律提 Nirṛti", "土", "主臥·重物", "7/9", "2/4"),
    ("S", "南方\nDakṣiṇa", "閻摩 Yama", "土", "臥室·儲藏", "7/9", "4/7"),
    ("SE", "東南\nĀgneya", "火神 Agni", "火", "廚房·電器", "7/9", "7/9"),
]


def render_vastu_mandala_html(
    lagna_sign: str = "",
    lagna_ruler: str = "",
    highlight_zones: Optional[dict[str, str]] = None,
) -> str:
    """渲染個人化 Vastu Purusha Mandala 圖表為 HTML。

    產生一個包含 9 宮格內部區域與 32 外環天神格的圖表，
    根據命盤資訊高亮標示重要方位。

    Args:
        lagna_sign: 上升星座英文名（用於圖表標題）。
        lagna_ruler: 上升星座主宰行星英文名。
        highlight_zones: 額外要高亮的方位區域，
            鍵為方位代碼（如 ``"E"``），值為高亮原因文字。

    Returns:
        完整的 HTML 字串，適用於 ``streamlit.components.v1.html()``。
    """
    if highlight_zones is None:
        highlight_zones = {}

    ruler_zone = PLANET_ZONE.get(lagna_ruler, "")

    # 每個方位區域的天然對應行星
    zone_planets: dict[str, list[str]] = {}
    for planet, zone in PLANET_ZONE.items():
        zone_planets.setdefault(zone, []).append(planet)

    parts: list[str] = [_CSS_HTML_HEAD, _build_header()]

    # 曼荼羅主體
    parts.append('<div class="mandala-wrapper">')
    parts.append('<div class="compass-label top">⬆ 北 North</div>')
    parts.append('<div class="middle-row">')
    parts.append(
        '<div class="compass-label left">'
        "⬅<br>西<br>W<br>e<br>s<br>t</div>"
    )
    parts.append('<div class="vastu-grid">')

    # ── 32 外環格 ──
    for row, col, sanskrit, chinese, zone in _OUTER_PADAS:
        is_ruler = zone == ruler_zone
        bg = _ZONE_COLORS.get(zone, "#f5f5f5")
        cls = "pada-cell lagna-highlight" if is_ruler else "pada-cell"
        style = (
            f"grid-row:{row + 1}/{row + 2};"
            f"grid-column:{col + 1}/{col + 2};"
            f"background:{bg};"
        )
        parts.append(
            f'<div class="{cls}" style="{style}" '
            f'title="{sanskrit} ({chinese}) — {zone} 方位">'
            f'<span class="deity-zh">{chinese}</span>'
            f'<span class="deity-sk">{sanskrit}</span>'
            f"</div>"
        )

    # ── 9 宮格 ──
    for zone_key, zh_label, deity, element, tip, gr, gc in _INNER_ZONES:
        is_ruler = zone_key == ruler_zone
        is_center = zone_key == "Center"
        bg = _ZONE_COLORS_INNER.get(zone_key, "#fff")

        cls_list = ["zone-cell"]
        if is_ruler:
            cls_list.append("lagna-highlight")
        if is_center:
            cls_list.append("center-zone")

        style = f"grid-row:{gr};grid-column:{gc};background:{bg};"

        # 方位名稱
        name_html = zh_label.replace("\n", "<br>")

        # 行星徽章
        badges = ""
        if zone_key in zone_planets:
            badge_items = []
            for p in zone_planets[zone_key]:
                sym = PLANET_SYMBOL.get(p, "")
                zh_short = _PLANET_ZH_SHORT.get(p, "")
                bcls = "planet-badge ruler" if p == lagna_ruler else "planet-badge"
                badge_items.append(
                    f'<span class="{bcls}" title="{p} ({zh_short})">'
                    f"{sym}</span>"
                )
            badges = (
                f'<div class="zone-planets">{"".join(badge_items)}</div>'
            )

        # 主宰指示
        ruler_html = ""
        if is_ruler:
            ruler_html = '<div class="ruler-indicator">⭐ 主宰方位</div>'

        # 中央圖示
        center_html = ""
        if is_center:
            center_html = '<div class="center-icon">🕉️</div>'

        parts.append(
            f'<div class="{" ".join(cls_list)}" style="{style}">'
            f"{center_html}"
            f'<div class="zone-name">{name_html}</div>'
            f'<div class="zone-deity">{deity}</div>'
            f'<div class="zone-element">{element}象</div>'
            f'<div class="zone-tip">{tip}</div>'
            f"{badges}"
            f"{ruler_html}"
            f"</div>"
        )

    parts.append("</div>")  # vastu-grid
    parts.append(
        '<div class="compass-label right">'
        "東<br>E<br>a<br>s<br>t<br>➡</div>"
    )
    parts.append("</div>")  # middle-row
    parts.append('<div class="compass-label bottom">⬇ 南 South</div>')
    parts.append("</div>")  # mandala-wrapper

    parts.append(_build_legend(lagna_ruler, ruler_zone))
    parts.append("</body></html>")

    return "\n".join(parts)


# ── 私有輔助函數 ──────────────────────────────────────────


def _build_header() -> str:
    """產生圖表標題 HTML。"""
    return (
        '<div class="chart-title">'
        "🕉️ Vastu Purusha Mandala 曼荼羅</div>"
        '<div class="chart-subtitle">'
        "9 宮格（內部方位）+ 32 外環格（護法天神位）"
        "｜Paramasayika 9×9</div>"
    )


def _build_legend(lagna_ruler: str, ruler_zone: str) -> str:
    """產生圖例說明 HTML。"""
    sym = PLANET_SYMBOL.get(lagna_ruler, "")
    zh = _PLANET_ZH_SHORT.get(lagna_ruler, lagna_ruler)
    return (
        '<div class="legend">'
        '<div class="legend-title">📖 圖例說明</div>'
        '<div class="legend-items">'
        # 金色邊框
        '<div class="legend-item">'
        '<span class="legend-swatch" '
        'style="background:#FFD700;border:2px solid #E6A800;"></span>'
        f" 金色邊框 = 上升主宰行星 {sym} {zh} 方位（{ruler_zone}）"
        "</div>"
        # 主宰行星徽章
        '<div class="legend-item">'
        f'<span class="planet-badge ruler" '
        f'style="width:16px;height:16px;font-size:10px;">{sym}</span>'
        " 主宰行星"
        "</div>"
        # 對應行星徽章
        '<div class="legend-item">'
        '<span class="planet-badge" '
        'style="width:16px;height:16px;font-size:10px;">☉</span>'
        " 方位對應行星"
        "</div>"
        # 元素色塊
        '<div class="legend-item">'
        '<span class="legend-swatch" style="background:#E3F2FD;"></span>水 '
        '<span class="legend-swatch" style="background:#FFF3E0;"></span>火 '
        '<span class="legend-swatch" style="background:#EFEBE9;"></span>土 '
        '<span class="legend-swatch" style="background:#E8F5E9;"></span>風 '
        '<span class="legend-swatch" style="background:#F3E5F5;"></span>空'
        "</div>"
        "</div>"
        "</div>"
    )


# ── CSS + HTML 頭部 ──────────────────────────────────────

_CSS_HTML_HEAD = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:"Microsoft JhengHei","PingFang TC",system-ui,-apple-system,sans-serif;
  background:transparent;padding:12px;
}
.chart-title{
  text-align:center;font-size:18px;font-weight:bold;
  margin-bottom:8px;color:#333;
}
.chart-subtitle{
  text-align:center;font-size:12px;color:#666;margin-bottom:14px;
}
.mandala-wrapper{
  display:flex;flex-direction:column;align-items:center;
}
.middle-row{
  display:flex;align-items:center;width:100%;max-width:720px;
}
.compass-label{
  font-weight:bold;font-size:13px;color:#555;text-align:center;
}
.compass-label.top,.compass-label.bottom{margin:4px 0;}
.compass-label.left,.compass-label.right{
  padding:0 6px;line-height:1.5;min-width:28px;
}
.vastu-grid{
  display:grid;
  grid-template-columns:repeat(9,1fr);
  grid-template-rows:repeat(9,1fr);
  gap:2px;flex:1;aspect-ratio:1;
  background:#bdbdbd;border-radius:8px;padding:2px;
  max-width:680px;
}
.pada-cell{
  border-radius:3px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  padding:2px 1px;cursor:default;transition:transform .15s;
  overflow:hidden;
}
.pada-cell:hover{
  transform:scale(1.1);z-index:2;
  box-shadow:0 2px 8px rgba(0,0,0,.25);
}
.deity-zh{font-size:11px;font-weight:600;line-height:1.2;color:#333;}
.deity-sk{font-size:8px;color:#777;line-height:1.1;}
.zone-cell{
  border-radius:6px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  padding:6px 3px;border:1px solid rgba(0,0,0,.08);
}
.zone-name{
  font-size:13px;font-weight:bold;color:#222;line-height:1.3;
  margin-bottom:1px;
}
.zone-deity{font-size:10px;color:#555;margin-bottom:1px;}
.zone-element{font-size:9px;color:#888;margin-bottom:1px;}
.zone-tip{
  font-size:9px;color:#6d4c41;background:rgba(255,255,255,.5);
  border-radius:3px;padding:1px 4px;margin-bottom:2px;
}
.zone-planets{
  display:flex;gap:2px;flex-wrap:wrap;justify-content:center;
  margin-top:2px;
}
.planet-badge{
  display:inline-flex;align-items:center;justify-content:center;
  width:18px;height:18px;border-radius:50%;
  background:#546E7A;color:#fff;font-size:11px;line-height:1;
}
.planet-badge.ruler{
  background:#E65100;box-shadow:0 0 4px rgba(230,81,0,.5);
}
.ruler-indicator{
  font-size:9px;color:#E65100;font-weight:bold;margin-top:1px;
}
.center-icon{font-size:20px;margin-bottom:1px;}
.center-zone{border:2px solid #FFD700 !important;}
.lagna-highlight{
  box-shadow:inset 0 0 0 3px #FFD700,0 0 10px rgba(255,215,0,.3);
  position:relative;
}
.legend{
  margin-top:14px;padding:10px 14px;background:#fafafa;
  border-radius:8px;border:1px solid #e0e0e0;
  max-width:720px;width:100%;
}
.legend-title{font-size:12px;font-weight:bold;margin-bottom:6px;color:#333;}
.legend-items{
  display:flex;flex-wrap:wrap;gap:10px;font-size:11px;color:#555;
}
.legend-item{display:flex;align-items:center;gap:4px;}
.legend-swatch{
  width:14px;height:14px;border-radius:3px;display:inline-block;
}
@media(max-width:600px){
  .deity-zh{font-size:9px;} .deity-sk{font-size:7px;}
  .zone-name{font-size:10px;} .zone-deity{font-size:8px;}
  .vastu-grid{max-width:98vw;}
}
</style></head><body>
"""
