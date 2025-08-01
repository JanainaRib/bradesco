import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
import zipfile
import os
import io
import base64
import unicodedata

import cnab240_exec  # seu módulo CNAB
import cnab240_exec_ted


def limpar_caracteres(texto):
    # Remove acentos e transforma caracteres em ASCII equivalente
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    # Remove qualquer símbolo que não seja letra, número ou espaço
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# Função para extrair dados dos arquivos TXT enviados
def extracao_arquivos(uploaded_files):
    dados_totais = []

    for arquivo in uploaded_files:
        nome_arquivo = arquivo.name
        filial_nome = nome_arquivo[:5]
        cod_filial = nome_arquivo[6:9]

        conteudo = arquivo.read().decode('utf-8')
        linhas = conteudo.splitlines()
        if len(linhas) < 3:
            continue

        linha1 = linhas[0]

        for i in range(2, len(linhas), 2):
            if i + 2 >= len(linhas):
                break

            linha2 = linhas[i]
            linha3 = linhas[i + 1]

            cliente = linha2[43:73].strip()
            cliente_limpo = limpar_caracteres(cliente)

            registro = {
                'Abreviatura': filial_nome,
                'CNPJ Filial': linha1[18:32].strip(),
                'Ponto': linha2[43:73].strip(),
                'Cliente': cliente_limpo,
                'CNPJ Cliente': linha3[18:32].strip(),
                'Numero Convenio': linha2[73:93].strip(),
                'Agencia Convenio': linha2[19:23].strip(),
                'Agencia': linha2[24:28].strip(),
                'C/C': linha2[29:42].strip(),
                'GTV': "",
                'OCT': "",
                'Local': "",
                'Remetente': "",
                'Finalidade': linha2[19:23].strip(),
                'data': linha2[93:101],
                'Valor a Creditar': float(linha2[118:139]) / 100,
                'Corte': "0",
                'DDP': "SIM",
                'Banco': linha2[20:23].strip(),
                'Ag_dv': "",
                'Conta_dv': "",
                'Codigo_Filial': cod_filial
            }

            dados_totais.append(registro)

    return pd.DataFrame(dados_totais)

# Função para ajustar valor formatado no TXT gerado
def ajustar_numero(numero):
    return str(numero).replace('.', '').replace(',', '') + '00'

# Streamlit UI
st.set_page_config(page_title="Prosegur - Bradesco PIX", layout="wide", page_icon="img/images.ico")
# Oculta o menu e o rodapé
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# Função para converter imagem local em base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Caminho da imagem
image_path = "img/prosegur.png"
img_base64 = get_base64_image(image_path)

st.markdown(
    f"""
    <style>
        .header-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            display: flex;
            align-items: center;
            gap: 15px;
            background-color: white;
            padding: 20px 20px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            z-index: 100;
        }}

        .logo-img {{
            width: 90px;
        }}

        .raleway-title {{
            font-family: 'Raleway', sans-serif;
            font-size: 28px;
            font-weight: 100;
            color: #000000;
            margin: 0;
        }}

        .header-space-adjust {{
            margin-top: 130px; /* Altura reservada para o cabeçalho */
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@100&display=swap" rel="stylesheet">
    
    <div class="header-container">
        <img class="logo-img" src="data:image/png;base64,{img_base64}">
        <h1 class="raleway-title">Geração de Arquivo CNAB240 – Bradesco</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Espaço reservado abaixo do cabeçalho fixo
st.markdown(
    """
    <style>
        .header-space-adjust {
            margin-top: 100px; /* ou tente 90px ou 80px */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        .custom-upload-label {
            font-size: 24px;
            font-weight: 400;
            color: #000000;
            margin-bottom: 10px;
            font-family: 'Raleway', sans-serif;
        }
    </style>
    <div class="custom-upload-label">📂 Selecione um ou mais arquivos .txt:</div>
    """,
    unsafe_allow_html=True
)
uploaded_files = st.file_uploader(
    "",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("🔄 Processando arquivos..."):
        df = extracao_arquivos(uploaded_files)

        if df.empty:
            st.warning("⚠️ Nenhum dado foi extraído.")
        else:
            st.success("✅ Dados extraídos!")

            st.subheader("📝 Edite os dados extraídos")

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Valor a Creditar": st.column_config.NumberColumn("Valor a Creditar", step=0.01)
                },
                key="editor"
            )

            # Botão para gerar arquivos TXT por filial
            #st.subheader("📥 Extrair e Baixar XLSX")
            col = st.columns(1)[0]  # pega a única coluna

            btn_col1, btn_col2, btn_col3 = col.columns([0.2,0.2,0.2])

            with btn_col1:
                if st.button("Baixar XLSX"):
                    if edited_df.empty:
                        st.warning("⚠️ Nenhum dado para exportar.")
                    else:
                        # Ajusta o dataframe, se quiser ajustar colunas antes do export
                        df_export = edited_df.copy()

                        # Exemplo: ajustar valor para formato numérico padrão (se quiser)
                        df_export['Valor a Creditar'] = df_export['Valor a Creditar'].astype(float).round(2)

                        # Gera o arquivo Excel em memória
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_export.to_excel(writer, index=False, sheet_name='Dados Extraidos')

                            # Ajustes opcionais no formato da planilha
                            workbook  = writer.book
                            worksheet = writer.sheets['Dados Extraidos']

                            # Ajustar largura das colunas automaticamente (opcional)
                            for i, col in enumerate(df_export.columns):
                                max_len = max(
                                    df_export[col].astype(str).map(len).max(),
                                    len(col)
                                ) + 2
                                worksheet.set_column(i, i, max_len)

                        output.seek(0)

                        st.download_button(
                            label="📥 Baixar Dados Extraidos (XLSX)",
                            data=output,
                            file_name=f"dados_extraidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                # Botão para gerar o arquivo CNAB 240 pelo seu módulo
                #st.subheader("📥 Gerar arquivo CNAB 240")
        with btn_col2:
            if st.button("Gerar TXT PIX"):
                with st.spinner("⏳ Gerando CNAB 240..."):
                    # Para cada filial, vamos preparar e gerar o CNAB
                    filial_unica = edited_df['Abreviatura'].unique()

                    # Vamos gerar só para a primeira filial, ou pode fazer em loop (ajuste conforme quiser)
                    filial = filial_unica[0]
                    df_filial = edited_df[edited_df['Abreviatura'] == filial].copy()
                    df_filial['totais'] = df_filial['Valor a Creditar'].count()

                    # Ajustar os valores do jeito que o CNAB espera, exemplo:
                    #df_filial['Valor a Creditar'] = df_filial['Valor a Creditar'].apply(lambda x: int(float(x)*100))  # valor em centavos, inteiro

                    # Se necessário, ajustar outras colunas conforme o formato esperado pelo cnab240_exec
                    colunas_ajustadas = [
                        'Banco', 'Agencia', 'Ag_dv', 'C/C', 'Conta_dv',
                        'Cliente', 'Valor a Creditar', 'data', 'CNPJ Cliente',
                        'Numero Convenio', 'Codigo_Filial', 'Abreviatura',
                        'Local', 'GTV', 'CNPJ Filial', 'totais',
                        'Remetente', 'Finalidade'
                    ]
                    df_filial = df_filial[colunas_ajustadas]
                    resultado = cnab240_exec.processar_dataframe(
                        df=df_filial,              # Passa o DF filtrado e ajustado
                        conf="minhaempresa",       # Seu config real
                        driver="csv"               # Seu driver real
                    )

                    if not isinstance(resultado, tuple) or len(resultado) != 2:
                        st.error("❌ Retorno inesperado da geração CNAB.")
                    else:
                        conteudo, nome_arquivo = resultado

                        if conteudo.startswith("❌") or conteudo.startswith("⚠️"):
                            conteudo = conteudo.replace("\n", "\r\n")
                            st.error(conteudo)
                        else:
                            st.success(f"✅ CNAB 240 gerado com sucesso! Arquivo: {nome_arquivo}")

                            # Garante quebra de linha Windows (CRLF) e encode correto
                            conteudo_corrigido = conteudo.replace('\r\n', '\n').replace('\n', '\r\n')
                            conteudo_bytes = conteudo_corrigido.encode('utf-8')  # ou 'latin1' se necessário

                            st.download_button(
                                label="📥 Baixar CNAB 240",
                                data=conteudo_bytes,
                                file_name=nome_arquivo,
                                mime="text/plain"
                            )
        with btn_col3:
            if st.button("Gerar TXT TED"):
                with st.spinner("⏳ Gerando CNAB 240 TED..."):
                    filial_unica = edited_df['Abreviatura'].unique()

                    if len(filial_unica) == 0:
                        st.warning("⚠️ Nenhuma filial encontrada nos dados.")
                    else:
                        filial = filial_unica[0]
                        df_filial = edited_df[edited_df['Abreviatura'] == filial].copy()
                        df_filial['totais'] = df_filial['Valor a Creditar'].count()

                        # Ajustar as colunas para o cnab240_ted
                        colunas_ajustadas = [
                            'Banco', 'Agencia', 'Ag_dv', 'C/C', 'Conta_dv',
                            'Cliente', 'Valor a Creditar', 'data', 'CNPJ Cliente',
                            'Numero Convenio', 'Codigo_Filial', 'Abreviatura',
                            'Local', 'GTV', 'CNPJ Filial', 'totais',
                            'Remetente', 'Finalidade'
                        ]
                        df_filial = df_filial[colunas_ajustadas]

                        resultado = cnab240_exec_ted.processar_dataframe(
                            df=df_filial,
                            conf="minhaempresa",  # ajuste conforme sua config
                            driver="csv"          # ajuste conforme seu driver
                        )

                        if not isinstance(resultado, str):
                            st.error("❌ Retorno inesperado da geração TED.")
                        elif resultado.startswith("❌") or resultado.startswith("⚠️"):
                            st.error(resultado.replace("\n", "\r\n"))
                        else:
                            st.success("✅ CNAB 240 TED gerado com sucesso!")

                            conteudo_corrigido = resultado.replace('\r\n', '\n').replace('\n', '\r\n')
                            conteudo_bytes = conteudo_corrigido.encode('utf-8')
                            nome_arquivo = f"OCTCPSCBPTED{datetime.now().strftime('%d%m')}.txt"
                            #nome_arquivo = f"CNAB240_TED_{filial}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

                            st.download_button(
                                label="📥 Baixar CNAB 240 TED",
                                data=conteudo_bytes,
                                file_name=nome_arquivo,
                                mime="text/plain"
                            )
