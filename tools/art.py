"""Gera a arte ASCII (matriz de (char, cor)) usada no painel esquerdo do card."""
import math

COLS, ROWS = 38, 24          # grade util a esquerda do painel de texto
CW, CH = 9.6, 20.0           # largura/altura aproximada de um caractere Consolas 16px
SHADES = [(0.12, ' '), (0.38, '.'), (0.62, ':'), (0.86, '+'), (1.01, '#')]


def shade(coverage):
    for limit, char in SHADES:
        if coverage < limit:
            return char
    return '█'


def blank():
    return [[(' ', None) for _ in range(COLS)] for _ in range(ROWS)]


def draw_pacman(grid, cx, cy, r, mouth_deg=38, color='pac'):
    """Circulo com uma cunha removida (a boca), amostrado em 4x6 por celula."""
    half = math.radians(mouth_deg) / 2
    for row in range(ROWS):
        for col in range(COLS):
            hits = 0
            total = 0
            for sy in range(6):
                for sx in range(4):
                    px = (col + (sx + 0.5) / 4) * CW
                    py = (row + (sy + 0.5) / 6) * CH
                    dx, dy = px - cx, py - cy
                    total += 1
                    if dx * dx + dy * dy > r * r:
                        continue
                    if abs(math.atan2(dy, dx)) < half:   # dentro da boca
                        continue
                    hits += 1
            char = shade(hits / total)
            if char != ' ':
                grid[row][col] = (char, color)


def draw_pellets(grid, row, cols, color='pellet'):
    for col in cols:
        if 0 <= row < ROWS and 0 <= col < COLS:
            grid[row][col] = ('o', color)


MOUTH_FRAMES = [4, 18, 32, 46, 32, 18]   # ciclo de abrir e fechar a boca


def build(mouth_deg=32):
    grid = blank()
    draw_pacman(grid, cx=13.9 * CW, cy=11.5 * CH, r=6.5 * CH, mouth_deg=mouth_deg)
    draw_pellets(grid, 11, [29, 32, 35])
    return grid


if __name__ == '__main__':
    for line in build(46):
        print(''.join(ch for ch, _ in line).rstrip())
