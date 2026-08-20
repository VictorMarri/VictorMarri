"""Gera a arte ASCII (matriz de (char, cor)) usada no painel esquerdo do card."""
import math

COLS, ROWS = 38, 23          # grade util a esquerda do painel de texto
CW, CH = 9.6, 20.0           # largura/altura aproximada de um caractere Consolas 16px
SHADES = [(0.12, ' '), (0.38, '░'), (0.62, '▒'), (0.86, '▓'), (1.01, '█')]


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


GHOST = [
    "  ▄████▄  ",
    " ████████ ",
    "██████████",
    "██████████",
    "██████████",
    "█▀▀█▀▀█▀▀█",
]
GHOST_EYES = {(2, 2), (2, 3), (2, 6), (2, 7)}      # branco do olho
GHOST_PUPILS = {(3, 2), (3, 3), (3, 6), (3, 7)}    # pupila


def draw_ghost(grid, top, left, color='ghost'):
    for r, line in enumerate(GHOST):
        for c, char in enumerate(line):
            if char == ' ':
                continue
            row, col = top + r, left + c
            if 0 <= row < ROWS and 0 <= col < COLS:
                if (r, c) in GHOST_EYES:
                    tone = 'eye'
                elif (r, c) in GHOST_PUPILS:
                    tone = 'pupil'
                else:
                    tone = color
                grid[row][col] = (char, tone)


def draw_pellets(grid, row, cols, color='pellet'):
    for col in cols:
        if 0 <= row < ROWS and 0 <= col < COLS:
            grid[row][col] = ('●', color)


def build():
    grid = blank()
    draw_pacman(grid, cx=13.9 * CW, cy=7.5 * CH, r=6.5 * CH, mouth_deg=42)
    draw_pellets(grid, 7, [29, 32, 35])
    draw_pellets(grid, 14, list(range(2, 37, 3)))
    draw_ghost(grid, top=17, left=3, color='ghost')
    draw_ghost(grid, top=17, left=16, color='ghost2')
    draw_pellets(grid, 19, [29, 32, 35])
    return grid


if __name__ == '__main__':
    for line in build():
        print(''.join(ch for ch, _ in line).rstrip())
