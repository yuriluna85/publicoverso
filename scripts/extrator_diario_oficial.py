#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrator_diario_oficial.py - Extrator de Portarias e Atos do Diário Oficial (DOU / DOE)
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Módulo autônomo responsável por:
1. Buscar portarias e atos de pessoal na Seção 2 do Diário Oficial da União (in.gov.br) e Diários Estaduais.
2. Segmentar as publicações em 6 categorias funcionais:
   - Admissões & Nomeações
   - Convocações
   - Exonerações & Dispensas
   - Aposentadorias
   - Demissões & Penalidades (PAD)
   - Comissões & Funções Gratificadas
3. Salvar os registros particionados em CSV por pastas de Ano/Mês (data/diario_oficial/AAAA/MM/movimentacoes_AAAA_MM.csv).
4. Gerar o arquivo de acesso rápido data/diario_oficial/movimentacoes_recentes.json para a interface.

Uso:
  python scripts/extrator_diario_oficial.py
  python scripts/extrator_diario_oficial.py --dias 15
"""

import sys
import os
import json
import csv
import time
import re
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import config

DATA_DO_DIR = RAIZ / 'data' / 'diario_oficial'
ARQUIVO_RECENTES_JSON = DATA_DO_DIR / 'movimentacoes_recentes.json'
ARQUIVO_INDICE_MESES = DATA_DO_DIR / 'indice_meses_disponiveis.json'

# --- Consultas de Atos Oficiais da Seção 2 do DOU / DOE ---
DORKS_DIARIO_OFICIAL = [
    {
        'tipo': 'Admissões & Nomeações',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("NOMEAR" OR "nomeia" OR "para exercer o cargo de provimento efetivo" OR "posse")',
    },
    {
        'tipo': 'Convocações',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("CONVOCAR" OR "Edital de Convocação" OR "convoca os candidatos aprovados")',
    },
    {
        'tipo': 'Exonerações & Dispensas',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("EXONERAR" OR "exonera, a pedido" OR "DISPENSAR" OR "declara vago o cargo")',
    },
    {
        'tipo': 'Aposentadorias',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("CONCEDER APOSENTADORIA" OR "aposentadoria voluntária com proventos" OR "aposentar")',
    },
    {
        'tipo': 'Demissões & Penalidades',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("APLICAR A PENALIDADE DE DEMISSÃO" OR "demitir o servidor" OR "cassação de aposentadoria")',
    },
    {
        'tipo': 'Comissões & Funções Gratificadas',
        'query': 'site:in.gov.br/web/dou/-/ "Seção 2" ("designar para exercer a Função Gratificada" OR "Código CD-" OR "Código FG-" OR "Código FCE-")',
    }
]


def extrair_orgao_e_numero_portaria(titulo, resumo):
    """Extrai o número da portaria e tenta identificar o órgão emissor no texto."""
    texto = f"{titulo} {resumo}"

    # Busca número de portaria
    match_portaria = re.search(r'(portaria\s+(?:nº|n°|n\.?)\s*[\d\.\/-]+|edital\s+(?:nº|n°|n\.?)\s*[\d\.\/-]+)', texto, re.IGNORECASE)
    numero_portaria = match_portaria.group(1).title() if match_portaria else 'Portaria Oficial'

    # Busca órgão conhecido
    orgaos_conhecidos = [
        'Ministério da Gestão e da Inovação', 'Ministério da Educação', 'Ministério da Saúde',
        'Ministério da Justiça', 'Polícia Federal', 'Polícia Rodoviária Federal',
        'Instituto Federal Baiano', 'Instituto Federal', 'Universidade Federal da Bahia',
        'Universidade Federal', 'Receita Federal', 'Instituto Nacional do Seguro Social',
        'Tribunal Regional Federal', 'Tribunal de Justiça', 'Fiocruz', 'Embrapa', 'INPE', 'IBGE'
    ]

    orgao_encontrado = 'Governo Federal / Administração Pública'
    for org in orgaos_conhecidos:
        if org.lower() in texto.lower():
            orgao_encontrado = org
            break

    return numero_portaria, orgao_encontrado


def extrair_nome_servidor(titulo, resumo):
    """Extrai nome próprio do servidor destacado na publicação."""
    texto = f"{titulo} {resumo}"
    # Busca nomes próprios com caixa alta (ex: NOMEAR CARLOS ALBERTO SILVA)
    match_nome = re.search(r'(?:NOMEAR|EXONERAR|DISPENSAR|CONCEDER APOSENTADORIA A|CONVOCAR)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{8,50})(?:,|\spara|\sservidor|\sportador|\smatrícula)', texto)
    if match_nome:
        return match_nome.group(1).strip().title()

    # Fallback: primeira sequência com cara de nome
    match_fallback = re.search(r'servidor[a]?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})', texto)
    if match_fallback:
        return match_fallback.group(1).strip().title()

    return 'Servidor Público Nominado'


def garantir_estrutura_pastas(ano, mes):
    """Cria a pasta particionada data/diario_oficial/AAAA/MM/ se não existir."""
    pasta_ano_mes = DATA_DO_DIR / str(ano) / f"{mes:02d}"
    pasta_ano_mes.mkdir(parents=True, exist_ok=True)
    return pasta_ano_mes


def executar_extracao(dias=15):
    """Executa a busca oficial no DOU e gera o particionamento em CSV/JSON."""
    print("=" * 65)
    print("EXTRATOR DO DIÁRIO OFICIAL DA UNIÃO & ESTADOS (PUBLICOVERSO)")
    print(f"Janela de Busca: {dias} dias | Destino: data/diario_oficial/AAAA/MM/")
    print("=" * 65)

    if not config.SERPER_API_KEY:
        print("[AVISO] SERPER_API_KEY não encontrada. Operando em modo de preservação.")

    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    pasta_mes = garantir_estrutura_pastas(ano_atual, mes_atual)

    arquivo_csv_mes = pasta_mes / f"movimentacoes_{ano_atual}_{mes_atual:02d}.csv"

    # Carrega registros existentes no mês
    registros_mes = []
    urls_registradas = set()

    if arquivo_csv_mes.exists():
        try:
            with open(arquivo_csv_mes, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    registros_mes.append(row)
                    urls_registradas.add(row.get('url_portaria', ''))
        except Exception:
            pass

    novos_atos = 0
    blacklist_descartes = config.carregar_blacklist_descartes()

    if config.SERPER_API_KEY:
        headers = {'X-API-KEY': config.SERPER_API_KEY, 'Content-Type': 'application/json'}

        for item in DORKS_DIARIO_OFICIAL:
            tipo_ato = item['tipo']
            print(f"Buscando no DOU: [{tipo_ato}] ...")

            payload = {
                'q': item['query'],
                'gl': 'br',
                'hl': 'pt-br',
                'num': 10,
                'tbs': f'qdr:d{dias}'
            }

            try:
                resp = requests.post(config.SERPER_NEWS_URL, headers=headers, json=payload, timeout=15)
                if resp.status_code == 200:
                    resultados = resp.json().get('news', [])
                    for r in resultados:
                        url_bruta = r.get('link', '')
                        titulo = r.get('title', '')
                        resumo = r.get('snippet', '')
                        data_pub = r.get('date', hoje.strftime('%d/%m/%Y'))

                        if not url_bruta or url_bruta in urls_registradas:
                            continue

                        url_canon = config.normalizar_url_para_deduplicacao(url_bruta)
                        slug_titulo = config.normalizar_titulo_para_slug(titulo)

                        if url_canon in blacklist_descartes or slug_titulo in blacklist_descartes:
                            continue

                        # Validação Factual: Exige contexto de ato oficial do serviço público
                        if not any(k in f"{titulo} {resumo}".lower() for k in ['portaria', 'edital', 'seção 2', 'secao 2', 'diário oficial', 'diario oficial', 'nomear', 'exonerar', 'aposentadoria', 'convocar', 'demissão']):
                            continue

                        numero_portaria, orgao = extrair_orgao_e_numero_portaria(titulo, resumo)
                        servidor_nome = extrair_nome_servidor(titulo, resumo)
                        ato_id = 'dou-' + hashlib.md5(url_bruta.encode()).hexdigest()[:10]

                        novo_registro = {
                            'id': ato_id,
                            'data_publicacao': hoje.strftime('%d/%m/%Y'),
                            'secao_diario': 'Seção 2 - Atos de Pessoal',
                            'orgao': orgao,
                            'tipo_ato': tipo_ato,
                            'servidor_nome': servidor_nome,
                            'cargo_funcao': numero_portaria,
                            'resumo_portaria': (resumo[:220] if resumo else titulo).replace('\n', ' '),
                            'numero_portaria': numero_portaria,
                            'url_portaria': url_bruta
                        }

                        registros_mes.insert(0, novo_registro)
                        urls_registradas.add(url_bruta)
                        novos_atos += 1
                        print(f"  [ATO REGISTRADO] {tipo_ato} | {servidor_nome} | {orgao}")

                time.sleep(config.PAUSA_ENTRE_REQUISICOES)
            except Exception as e:
                print(f"  [ERRO BUSCA DOU] {e}")

    # Salva o CSV atualizado do mês
    campos_csv = ['id', 'data_publicacao', 'secao_diario', 'orgao', 'tipo_ato', 'servidor_nome', 'cargo_funcao', 'resumo_portaria', 'numero_portaria', 'url_portaria']
    with open(arquivo_csv_mes, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos_csv)
        writer.writeheader()
        writer.writerows(registros_mes)

    # Atualiza o arquivo de acesso rápido JSON para o frontend (últimos 50 atos)
    movimentacoes_recentes = registros_mes[:50]
    with open(ARQUIVO_RECENTES_JSON, 'w', encoding='utf-8') as f:
        json.dump(movimentacoes_recentes, f, ensure_ascii=False, indent=2)

    # Atualiza o índice de meses disponíveis
    indice_meses = [
        {"ano": ano_atual, "mes": mes_atual, "label": f"{mes_atual:02d}/{ano_atual}", "caminho_csv": f"data/diario_oficial/{ano_atual}/{mes_atual:02d}/movimentacoes_{ano_atual}_{mes_atual:02d}.csv"}
    ]
    with open(ARQUIVO_INDICE_MESES, 'w', encoding='utf-8') as f:
        json.dump(indice_meses, f, ensure_ascii=False, indent=2)

    print("-" * 65)
    print(f"EXTRAÇÃO DO DIÁRIO OFICIAL CONCLUÍDA:")
    print(f"  - Novos atos registrados hoje: {novos_atos}")
    print(f"  - Total de registros no mês ({mes_atual:02d}/{ano_atual}): {len(registros_mes)}")
    print(f"  - CSV mantido em: {arquivo_csv_mes}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Publicoverso - Extrator de Portarias do Diário Oficial")
    parser.add_argument('--dias', type=int, default=15, help="Janela de busca em dias (padrão: 15)")
    args = parser.parse_args()

    executar_extracao(dias=args.dias)


if __name__ == '__main__':
    main()
