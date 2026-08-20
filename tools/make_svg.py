"""Monta light_mode.svg e dark_mode.svg a partir de tools/art.py + tools/profile.py."""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import art                                    # noqa: E402
from card_profile import PROFILE                   # noqa: E402

LEFT_X, PANEL_X, TOP_Y, STEP = 15, 390, 30, 20
PANEL_COLS = 60
WIDTH = 985
HEIGHT = TOP_Y + art.ROWS * STEP - 10

THEMES = {
    "light_mode.svg": dict(
        bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069", add="#1a7f37",
        delc="#cf222e", cc="#c2cfde", pac="#e3a008", ghost="#cf222e", ghost2="#0969da",
        eye="#eaeef2", pupil="#0a3069", pellet="#57606a"),
    "dark_mode.svg": dict(
        bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff", add="#3fb950",
        delc="#f85149", cc="#616e7f", pac="#ffd33d", ghost="#f85149", ghost2="#58a6ff",
        eye="#ffffff", pupil="#0d1117", pellet="#8b949e"),
}


def esc(text):
    return html.escape(text, quote=False)


def emit(parts, x, y):
    """parts: lista de (texto, classe|None, id|None). O primeiro tspan carrega x/y."""
    out = []
    for i, (text, cls, eid) in enumerate(parts):
        attrs = f' x="{x}" y="{y}"' if i == 0 else ""
        attrs += f' class="{cls}"' if cls else ""
        attrs += f' id="{eid}"' if eid else ""
        out.append(f"<tspan{attrs}>{esc(text)}</tspan>")
    return "".join(out)


def dots_for(reserve, value):
    """Mesma regra do today.py, para o layout nao pular quando o script reescrever."""
    just = max(0, reserve - len(value))
    if just <= 2:
        return {0: "", 1: " ", 2: ". "}[just]
    return " " + "." * just + " "


def key_parts(key):
    """'Languages.Programming' -> Languages / . / Programming, com o ponto neutro."""
    parts, chunks = [], key.split(".")
    for i, chunk in enumerate(chunks):
        if i:
            parts.append((".", None, None))
        parts.append((chunk, "key", None))
    return parts


def field_line(key, value, dyn=None):
    reserve = PANEL_COLS - 5 - len(key)
    parts = [(". ", "cc", None)] + key_parts(key) + [(":", None, None)]
    parts.append((dots_for(reserve, value), "cc", f"{dyn}_dots" if dyn else None))
    parts.append((value, "value", dyn))
    return parts


def rule(label=None):
    if label:
        head = f"- {label} "
        return [(head + "-" + "\u2014" * (PANEL_COLS - len(head) - 4) + "-\u2014-", None, None)]
    return None


def panel_rows():
    """Devolve uma lista de 'linhas', cada uma sendo uma lista de parts (ou None)."""
    rows = [[(PROFILE["title"], None, None)]]
    title_len = len(PROFILE["title"])
    rows[0].append((" -" + "\u2014" * (PANEL_COLS - title_len - 6) + "-\u2014-", None, None))

    for key, value in PROFILE["fields"]:
        if key is None:
            rows.append([(". ", "cc", None)])
        elif key == "Uptime":
            rows.append(field_line(key, "0 years, 0 months, 0 days", dyn="age_data"))
        else:
            rows.append(field_line(key, value))

    rows.append(None)
    rows.append(rule("Contact"))
    for key, value in PROFILE["contacts"]:
        rows.append(field_line(key, value))

    rows.append(None)
    rows.append(rule("GitHub Stats"))
    rows.append([
        (". ", "cc", None), ("Repos", "key", None), (":", None, None),
        (dots_for(6, "0"), "cc", "repo_data_dots"), ("0", "value", "repo_data"),
        (" {", None, None), ("Contributed", "key", None), (": ", None, None),
        ("0", "value", "contrib_data"), ("} | ", None, None),
        ("Stars", "key", None), (":", None, None),
        (dots_for(14, "0"), "cc", "star_data_dots"), ("0", "value", "star_data"),
    ])
    rows.append([
        (". ", "cc", None), ("Commits", "key", None), (":", None, None),
        (dots_for(22, "0"), "cc", "commit_data_dots"), ("0", "value", "commit_data"),
        (" | ", None, None), ("Followers", "key", None), (":", None, None),
        (dots_for(10, "0"), "cc", "follower_data_dots"), ("0", "value", "follower_data"),
    ])
    rows.append([
        (". ", "cc", None), ("Lines of Code on GitHub", "key", None), (":", None, None),
        (dots_for(9, "0"), "cc", "loc_data_dots"), ("0", "value", "loc_data"),
        (" ( ", None, None), ("0", "addColor", "loc_add"), ("++", "addColor", None),
        (", ", None, None), (" ", None, "loc_del_dots"), ("0", "delColor", "loc_del"),
        ("--", "delColor", None), (" )", None, None),
    ])
    return rows


def art_rows(grid):
    lines = []
    for row in grid:
        cells = list(row)
        while cells and cells[-1][0] == " ":
            cells.pop()
        parts, buf, cur = [], "", None
        for char, color in cells:
            color = color if char != " " else None
            if color != cur:
                if buf:
                    parts.append((buf, cur, None))
                buf, cur = char, color
            else:
                buf += char
        if buf:
            parts.append((buf, cur, None))
        lines.append(parts)
    return lines


def build(filename, theme):
    grid = art.build()
    art_lines = art_rows(grid)
    panel = panel_rows()

    body = []
    for i, parts in enumerate(art_lines):
        if parts:
            body.append(emit(parts, LEFT_X, TOP_Y + i * STEP))
    art_block = "\n".join(body)

    body = []
    for i, parts in enumerate(panel):
        if parts:
            body.append(emit(parts, PANEL_X, TOP_Y + i * STEP))
    panel_block = "\n".join(body)

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{WIDTH}px" height="{HEIGHT}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
size-adjust: 109%;
}}
.key {{fill: {theme['key']};}}
.value {{fill: {theme['value']};}}
.addColor {{fill: {theme['add']};}}
.delColor {{fill: {theme['delc']};}}
.cc {{fill: {theme['cc']};}}
.pac {{fill: {theme['pac']};}}
.ghost {{fill: {theme['ghost']};}}
.ghost2 {{fill: {theme['ghost2']};}}
.eye {{fill: {theme['eye']};}}
.pupil {{fill: {theme['pupil']};}}
.pellet {{fill: {theme['pellet']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{WIDTH}px" height="{HEIGHT}px" fill="{theme['bg']}" rx="15"/>
<text x="{LEFT_X}" y="{TOP_Y}" fill="{theme['fg']}">
{art_block}
</text>
<text x="{PANEL_X}" y="{TOP_Y}" fill="{theme['fg']}">
{panel_block}
</text>
</svg>
"""
    pathlib.Path(filename).write_text(svg, encoding="utf-8")
    print(f"{filename}: {len(svg)} bytes")


if __name__ == "__main__":
    for name, theme in THEMES.items():
        build(name, theme)
