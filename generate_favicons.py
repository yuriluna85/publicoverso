#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_favicons.py - Gerador de Favicons em alta resolucao para o Publicoverso
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Gera:
  - favicon.svg
  - favicon-16x16.png
  - favicon-32x32.png
  - favicon-48x48.png
  - apple-touch-icon.png (180x180)
  - favicon.ico (contendo 16x16, 32x32 e 48x48)
"""

import sys
import math
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')

PASTA_PORTAL = Path(__file__).parent


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


# --- 1. Gerar SVG ---
SVG_CONTENT = """<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polygon points="20,2 35,10 35,30 20,38 5,30 5,10" stroke="url(#hexGradFavicon)" stroke-width="2" fill="rgba(0,210,200,0.08)"/>
  <circle cx="20" cy="8" r="2.5" fill="#00D2C8"/>
  <circle cx="31" cy="15" r="2.5" fill="#9146FF"/>
  <circle cx="31" cy="27" r="2.5" fill="#00D2C8"/>
  <circle cx="20" cy="33" r="2.5" fill="#9146FF"/>
  <circle cx="9" cy="27" r="2.5" fill="#00D2C8"/>
  <circle cx="9" cy="15" r="2.5" fill="#9146FF"/>
  <circle cx="20" cy="20" r="3.5" fill="#00D2C8"/>
  <line x1="20" y1="20" x2="20" y2="8" stroke="#00D2C8" stroke-width="1.2" opacity="0.75"/>
  <line x1="20" y1="20" x2="31" y2="15" stroke="#9146FF" stroke-width="1.2" opacity="0.75"/>
  <line x1="20" y1="20" x2="31" y2="27" stroke="#00D2C8" stroke-width="1.2" opacity="0.75"/>
  <line x1="20" y1="20" x2="20" y2="33" stroke="#9146FF" stroke-width="1.2" opacity="0.75"/>
  <line x1="20" y1="20" x2="9" y2="27" stroke="#00D2C8" stroke-width="1.2" opacity="0.75"/>
  <line x1="20" y1="20" x2="9" y2="15" stroke="#9146FF" stroke-width="1.2" opacity="0.75"/>
  <defs>
    <linearGradient id="hexGradFavicon" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
      <stop stop-color="#00D2C8"/>
      <stop offset="1" stop-color="#9146FF"/>
    </linearGradient>
  </defs>
</svg>
"""


def criar_imagem_base(size=512):
    """Desenha a logo em alta resolucao usando PIL para super-sampling antialiased."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    scale = size / 40.0

    # Cores
    c_turquesa = hex_to_rgb('#00D2C8')
    c_roxo = hex_to_rgb('#9146FF')

    # Pontos do Hexagono
    points_orig = [(20, 2), (35, 10), (35, 30), (20, 38), (5, 30), (5, 10)]
    points_scaled = [(x * scale, y * scale) for x, y in points_orig]

    # Preenchimento translucido
    fill_color = (c_turquesa[0], c_turquesa[1], c_turquesa[2], 25)
    draw.polygon(points_scaled, fill=fill_color)

    # Linha do Hexagono com gradiente interpolado
    stroke_w = int(2.2 * scale)
    n_pts = len(points_scaled)
    for i in range(n_pts):
        p1 = points_scaled[i]
        p2 = points_scaled[(i + 1) % n_pts]

        # Gradiente dinamico no contorno
        t = i / float(n_pts)
        r = int(c_turquesa[0] * (1 - t) + c_roxo[0] * t)
        g = int(c_turquesa[1] * (1 - t) + c_roxo[1] * t)
        b = int(c_turquesa[2] * (1 - t) + c_roxo[2] * t)
        draw.line([p1, p2], fill=(r, g, b, 255), width=stroke_w)

    # Nos da Constelacao (cx, cy, cor, raio)
    nos = [
        (20, 8, c_turquesa, 2.5),
        (31, 15, c_roxo, 2.5),
        (31, 27, c_turquesa, 2.5),
        (20, 33, c_roxo, 2.5),
        (9, 27, c_turquesa, 2.5),
        (9, 15, c_roxo, 2.5),
        (20, 20, c_turquesa, 3.8),
    ]

    cx0, cy0 = 20 * scale, 20 * scale
    line_w = int(1.4 * scale)

    # Linhas radiais da constelacao
    for cx, cy, cor, r in nos[:6]:
        px, py = cx * scale, cy * scale
        draw.line([(cx0, cy0), (px, py)], fill=(cor[0], cor[1], cor[2], 200), width=line_w)

    # Circulos dos nos
    for cx, cy, cor, r in nos:
        px, py = cx * scale, cy * scale
        pr = r * scale
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(cor[0], cor[1], cor[2], 255))

    return img


def main():
    print('[INICIANDO] Geracao dos favicons do Publicoverso...')

    # 1. Salvar SVG
    caminho_svg = PASTA_PORTAL / 'favicon.svg'
    caminho_svg.write_text(SVG_CONTENT, encoding='utf-8')
    print(f'[OK] Criado: {caminho_svg.name}')

    # 2. Criar imagem base 512x512 em memoria
    base_img = criar_imagem_base(size=512)

    # 3. Gerar tamanhos PNG
    tamanhos = {
        'favicon-16x16.png': (16, 16),
        'favicon-32x32.png': (32, 32),
        'favicon-48x48.png': (48, 48),
        'apple-touch-icon.png': (180, 180),
    }

    images_png = {}
    for nome, size in tamanhos.items():
        resized = base_img.resize(size, Image.Resampling.LANCZOS)
        caminho = PASTA_PORTAL / nome
        resized.save(caminho, format='PNG')
        images_png[size[0]] = resized
        print(f'[OK] Criado: {nome} ({size[0]}x{size[1]})')

    # 4. Gerar favicon.ico multi-resolucao (16, 32, 48)
    caminho_ico = PASTA_PORTAL / 'favicon.ico'
    img_ico_base = base_img.resize((48, 48), Image.Resampling.LANCZOS)
    img_ico_base.save(
        caminho_ico,
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print(f'[OK] Criado: favicon.ico (multi-resolucao 16, 32, 48)')

    print('\n[SUCESSO] Todos os favicons foram gerados.')


if __name__ == '__main__':
    main()
