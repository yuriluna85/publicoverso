#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/classificador_noticias.py
Classificador Inteligente de Notícias para o Portal Publicoverso.
Aplica regras semânticas de desambiguação para categorizar corretamente matérias mineradas.
"""

import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NOTICIAS_FILE = os.path.join(DATA_DIR, "acervo_links_minerados.json")

# Palavras-chave por categoria
KEYWORDS_POLICIAL = [
    "polícia", "policial", "delegado", "delegada", "prisão", "prendeu", "preso", "operação",
    "investigação", "crime", "homicídio", "furto", "roubo", "apreensão", "drogas", "facção",
    "mandado", "segurança pública", "polícia militar", "polícia civil", "polícia federal",
    "bombeiro militar", "guarda municipal", "assalto", "crime organizado", "perícia"
]

KEYWORDS_ESPORTES = [
    "maratona", "corrida", "campeonato", "torneio", "medalha", "ouro", "prata", "bronze",
    "pódio", "atleta", "futebol", "jiu-jitsu", "judô", "natação", "ciclismo", "triathlon",
    "venceu competição", "campeão", "campeã", "corrida de rua", "jogos"
]

KEYWORDS_ARTES = [
    "livro", "obra", "poesia", "romance", "pintura", "exposição", "teatro", "filme",
    "documentário", "música", "álbum", "escritor", "escritora", "artista", "literatura",
    "escultura", "sarau"
]

KEYWORDS_SOLIDARIEDADE = [
    "doação", "doador", "sangue", "ação solidária", "voluntariado", "campanha agasalho",
    "arrecadação", "caridade", "projeto social", "ajuda humanitária", "resgate"
]

def categorizar_item(titulo, resumo, categoria_original=""):
    texto = f"{titulo} {resumo}".lower()
    
    # 1. Regra de Desambiguação Esportes / Artes para Servidores de Segurança
    is_esporte = any(kw in texto for kw in KEYWORDS_ESPORTES)
    is_arte = any(kw in texto for kw in KEYWORDS_ARTES)
    is_solidariedade = any(kw in texto for kw in KEYWORDS_SOLIDARIEDADE)
    is_policial = any(kw in texto for kw in KEYWORDS_POLICIAL)

    # Se a notícia for sobre esporte (ex: policial venceu maratona) -> Esportes
    if is_esporte and ("venceu" in texto or "maratona" in texto or "pódio" in texto or "atleta" in texto or "campeão" in texto or "campeã" in texto):
        return "Esportes e Aventura"

    # Se for sobre arte (ex: delegado lançou livro/quadro) -> Artes e Literatura
    if is_arte and ("livro" in texto or "romance" in texto or "exposição" in texto or "escritor" in texto or "escritora" in texto):
        return "Artes e Literatura"

    # Se for ação voluntária/doação -> Solidariedade
    if is_solidariedade and not ("operação" in texto or "investigação" in texto or "prisão" in texto):
        return "Solidariedade e Comunidade"

    # Se contiver termos policiais estritos (crime, prisão, operação) -> Policial e Segurança Pública
    if is_policial:
        return "Policial e Segurança Pública"

    return categoria_original or "Histórias e Superação"

def reclassificar_acervo():
    if not os.path.exists(NOTICIAS_FILE):
        print(f"[Aviso] Arquivo {NOTICIAS_FILE} não encontrado.")
        return

    with open(NOTICIAS_FILE, "r", encoding="utf-8") as f:
        noticias = json.load(f)

    modificados = 0
    novas_noticias = []
    for item in noticias:
        cat_antiga = item.get("categoria", "")
        cat_nova = categorizar_item(item.get("titulo", ""), item.get("resumo", ""), cat_antiga)
        if cat_antiga != cat_nova:
            item["categoria"] = cat_nova
            modificados += 1
        novas_noticias.append(item)

    with open(NOTICIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(novas_noticias, f, ensure_ascii=False, indent=2)

    print(f"[Sucesso] Classificação concluída. {modificados} notícias foram reclassificadas.")

if __name__ == "__main__":
    reclassificar_acervo()
