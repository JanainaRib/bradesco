import os
import json
import importlib
from datetime import datetime
import tempfile
import pandas as pd

import cnab240.core.header_lote as hl
import cnab240.core.header_arquivo as ha
import cnab240.remessa_pagamento as rp

def check_conf(conf):
    conf_file = f"./cnab240/confs/{conf}.prod.conf"
    if not os.path.isfile(conf_file):
        return False
    return json.load(open(conf_file, "r", encoding="utf-8"))

def generate(conf=None, arquivo_processamento=None, driver=None):
    conf_json = check_conf(conf)
    if not conf_json:
        return "⚠️ Configuração não encontrada."

    odict_ha = ha.default_header_arquivo()
    odict_hl = hl.default_header_lote()

    for indice in conf_json.keys():
        if indice in odict_ha:
            odict_ha[indice] = conf_json[indice]
        if indice in odict_hl:
            odict_hl[indice] = conf_json[indice]

    try:
        modname = f"cnab240.drivers.{driver}"
        module = importlib.import_module(modname)
        contas = module.exec(arquivo_processamento)
    except Exception as e:
        return f"❌ Erro no driver '{driver}': {str(e)}"

    entrada = {
        'header_arquivo': odict_ha,
        'header_lote': odict_hl,
        'segmento_a_contas': contas
    }

    resultado = rp.generate(entrada, conf_json)

    # ✅ Forçar quebra de linha Windows (CRLF)
    if isinstance(resultado, str):
        resultado = resultado.replace('\r\n', '\n').replace('\n', '\r\n')

    return resultado

def processar_pasta(conf, pasta, driver):
    arquivos = [arq for arq in os.listdir(pasta) if arq.endswith(".csv")]
    if not arquivos:
        return "⚠️ Nenhum arquivo CSV encontrado."

    resultados = []
    for arq in arquivos:
        caminho = os.path.join(pasta, arq)
        resultado = generate(conf, caminho, driver)
        resultados.append(f"✅ {arq}:\n{resultado}")
    return "\n\n".join(resultados)

def preparar_df_para_cnab(df: pd.DataFrame) -> pd.DataFrame:
    # Ajuste simples: converter 'Valor a Creditar' para inteiro em centavos
    df_copy = df.copy()
    df_copy['Valor a Creditar'] = (df_copy['Valor a Creditar'].astype(float) * 100).astype(int)
    return df_copy

def processar_dataframe(df: pd.DataFrame, conf: str, driver: str) -> str:
    df_cnab = preparar_df_para_cnab(df)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
        # Salva CSV sem header (header=False) e com separador ';'
        df_cnab.to_csv(tmp.name, sep=';', index=False, header=False)
        tmp_path = tmp.name

    try:
        resultado = generate(conf=conf, arquivo_processamento=tmp_path, driver=driver)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return resultado

