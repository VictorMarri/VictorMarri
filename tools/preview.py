"""Preview em texto do SVG gerado, para conferir alinhamento das colunas."""
import sys
from xml.dom import minidom


def flat(node):
    return "".join(n.data if n.nodeType == n.TEXT_NODE else flat(n) for n in node.childNodes)


doc = minidom.parse(sys.argv[1] if len(sys.argv) > 1 else "light_mode.svg")
blocks = []
for text in doc.getElementsByTagName("text"):
    lines, cur = [], None
    for span in [n for n in text.childNodes if n.nodeName == "tspan"]:
        if span.getAttribute("y"):          # tspan com y inicia uma nova linha
            if cur is not None:
                lines.append(cur)
            cur = ""
        cur = (cur or "") + flat(span)
    if cur is not None:
        lines.append(cur)
    blocks.append(lines)

left, right = blocks[0], blocks[-1]   # 1o quadro da arte + painel
for i in range(max(len(left), len(right))):
    l = left[i] if i < len(left) else ""
    r = right[i] if i < len(right) else ""
    print(f"{l:<39}|{r}|")
