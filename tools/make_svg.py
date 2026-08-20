"""Monta light_mode.svg e dark_mode.svg a partir de tools/art.py + tools/card_profile.py."""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import art                                    # noqa: E402
from card_profile import PROFILE              # noqa: E402

LEFT_X, PANEL_X, TOP_Y, STEP = 15, 390, 30, 20
PANEL_COLS = 60
WIDTH = 985
HEIGHT = TOP_Y + art.ROWS * STEP - 10
DUR = 0.9        # duracao do ciclo completo da boca, em segundos

THEMES = {
    "light_mode.svg": dict(
        bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069", add="#1a7f37",
        delc="#cf222e", cc="#c2cfde", pac="#e3a008", pellet="#57606a"),
    "dark_mode.svg": dict(
        bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff", add="#3fb950",
        delc="#f85149", cc="#616e7f", pac="#ffd33d", pellet="#8b949e"),
}


def esc(text):
    return html.escape(text, quote=False)


def emit(parts, x, y):
    """parts: lista de (texto, classe|None, id|None). O primeiro tspan carrega x/y."""
    out = []
    for i, (text, cls, eid) in enumerate(parts):
        attrs = ' x="%d" y="%d"' % (x, y) if i == 0 else ""
        attrs += ' class="%s"' % cls if cls else ""
        attrs += ' id="%s"' % eid if eid else ""
        out.append("<tspan%s>%s</tspan>" % (attrs, esc(text)))
    return "".join(out)


def dots_for(reserve, value):
    """Mesma regra do today.py, para o layout nao pular quando o script reescrever."""
    just = max(0, reserve - len(value))
    if just <= 2:
        return {0: "", 1: " ", 2: ". "}[just]
    return " " + "." * just + " "


def key_parts(key):
    """'Languages.Programming' -> Languages / . / Programming, com o ponto neutro."""
    parts = []
    for i, chunk in enumerate(key.split(".")):
        if i:
            parts.append((".", None, None))
        parts.append((chunk, "key", None))
    return parts


def field_line(key, value, dyn=None):
    reserve = PANEL_COLS - 5 - len(key)
    parts = [(". ", "cc", None)] + key_parts(key) + [(":", None, None)]
    parts.append((dots_for(reserve, value), "cc", (dyn + "_dots") if dyn else None))
    parts.append((value, "value", dyn))
    return parts


def rule(label):
    head = "- " + label + " "
    return [(head + "-" + "\u2014" * (PANEL_COLS - len(head) - 4) + "-\u2014-", None, None)]


def panel_rows():
    """Uma entrada por linha do painel; None significa linha em branco."""
    title = PROFILE["title"]
    rows = [[(title, None, None),
             (" -" + "\u2014" * (PANEL_COLS - len(title) - 5) + "-\u2014-", None, None)]]

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
    """Converte a grade em parts, agrupando caracteres vizinhos de mesma cor."""
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


def art_frames(theme):
    """Um <g> por quadro da boca; o CSS deixa so um visivel de cada vez."""
    frames = art.MOUTH_FRAMES
    total = len(frames)
    blocks = []
    css = [".pm {opacity: 0;}", ".p0 {opacity: 1;}"]

    for i, degrees in enumerate(frames):
        rows = art_rows(art.build(degrees))
        body = [emit(parts, LEFT_X, TOP_Y + row * STEP)
                for row, parts in enumerate(rows) if parts]
        blocks.append('<g class="pm p%d">\n<text x="%d" y="%d" fill="%s">\n%s\n</text>\n</g>'
                      % (i, LEFT_X, TOP_Y, theme["fg"], "\n".join(body)))

        ini, fim = i * 100.0 / total, (i + 1) * 100.0 / total
        if i == 0:
            steps = "0%%,%.2f%%{opacity:1}%.2f%%,100%%{opacity:0}" % (fim - 0.01, fim)
        elif i == total - 1:
            steps = "0%%,%.2f%%{opacity:0}%.2f%%,100%%{opacity:1}" % (ini - 0.01, ini)
        else:
            steps = ("0%%,%.2f%%{opacity:0}%.2f%%,%.2f%%{opacity:1}%.2f%%,100%%{opacity:0}"
                     % (ini - 0.01, ini, fim - 0.01, fim))
        css.append("@keyframes pm%d {%s}" % (i, steps))
        css.append(".p%d {animation: pm%d %ss infinite;}" % (i, i, DUR))

    return "\n".join(blocks), "\n".join(css)


def build(filename, theme):
    art_block, art_css = art_frames(theme)
    panel_block = "\n".join(emit(parts, PANEL_X, TOP_Y + i * STEP)
                            for i, parts in enumerate(panel_rows()) if parts)

    svg = """<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{w}px" height="{h}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
size-adjust: 109%;
}}
.key {{fill: {key};}}
.value {{fill: {value};}}
.addColor {{fill: {add};}}
.delColor {{fill: {delc};}}
.cc {{fill: {cc};}}
.pac {{fill: {pac};}}
.pellet {{fill: {pellet};}}
text, tspan {{white-space: pre;}}
{art_css}
</style>
<rect width="{w}px" height="{h}px" fill="{bg}" rx="15"/>
{art_block}
<text x="{px}" y="{ty}" fill="{fg}">
{panel_block}
</text>
</svg>
""".format(w=WIDTH, h=HEIGHT, px=PANEL_X, ty=TOP_Y, art_css=art_css,
           art_block=art_block, panel_block=panel_block, **theme)

    pathlib.Path(filename).write_text(svg, encoding="utf-8")
    print("%s: %d bytes" % (filename, len(svg)))


if __name__ == "__main__":
    for name, theme in THEMES.items():
        build(name, theme)
