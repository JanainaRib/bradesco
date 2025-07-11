from datetime import datetime
import cnab240_TED.core.header_arquivo as ha
import cnab240_TED.core.header_lote as hl
import cnab240_TED.core.trailer_arquivo as ta
import cnab240_TED.core.segmento_a as sega
import cnab240_TED.core.segmento_b as segb
import cnab240_TED.core.trailer_lote as tl

def generate(odict_entrada, conf=None):
    if conf is None:
        print("Código do banco é um campo obrigatório")
        return None, None

    try:
        codigo_banco = conf['banco']
        str_header = ha.header_arquivo(odict_entrada['header_arquivo'])
        conteudo_lotes = []
        total_registros_arquivo = 2  # Header de arquivo + Trailer de arquivo

        if codigo_banco == '237':
            # ✅ Um único lote para Bradesco
            lote = '1'
            print(f"➡️ Gerando header do lote único para banco 237...")
            str_header_lote = hl.header_lote(odict_entrada['header_lote'])
            list_segmentos = []
            somatoria_de_valores = 0
            sequencial_registro = 0

            for conta in odict_entrada['segmento_a_contas']:
                print(f"🧾 Processando conta: {conta['cpf']}")
                odic_sega = sega.default()
                odic_sega['banco'] = codigo_banco
                odic_sega['sequencial_registro_lote'] = str(sequencial_registro + 1)
                odic_sega['banco_fv'] = conta['banco']
                odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
                odic_sega['empresa_conta_corrente_conta_dv'] = conf['empresa_conta_corrente_conta_dv']
                odic_sega['empresa_conta_corrente_agencia1'] = codigo_banco
                odic_sega['favorecido_conta_corrente_agencia_codigo'] = conta['agencia']
                odic_sega['favorecido_conta_corrente_agencia_dv'] = conta['agencia_dv']
                odic_sega['favorecido_conta_corrente_conta_numero'] = conta['conta']
                odic_sega['favorecido_nome'] = conta['favorecido_nome']
                seu_numero_complemento = str(datetime.now().strftime("%y")) + str(datetime.now().timetuple().tm_yday) + str(datetime.now().strftime("%H%M"))
                odic_sega['credito_seu_numero'] = conta.get('credito_seu_numero', conta['cpf'] + seu_numero_complemento)[:9]
                str_seg_a = sega.parse(odic_sega)

                odic_segb = segb.default()
                odic_segb['sequencial_registro_lote'] = str(sequencial_registro + 2)
                odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
                odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
                str_seg_b = segb.parse(odic_segb)

                list_segmentos.append(str_seg_a)
                list_segmentos.append(str_seg_b)

                sequencial_registro += 2
                somatoria_de_valores += conta['valor_centavos']

            print("➡️ Gerando trailer do lote único...")
            odic_trailer_lote = tl.default()
            odic_trailer_lote['banco'] = codigo_banco
            odic_trailer_lote['lote'] = lote
            odic_trailer_lote['quantidade_registro_lote'] = sequencial_registro + 2
            odic_trailer_lote['somatoria_valores'] = somatoria_de_valores
            str_trailer_lote = tl.parse(odic_trailer_lote)

            conteudo_lotes.append(f"{str_header_lote}\n" + '\n'.join(list_segmentos) + f"\n{str_trailer_lote}")
            total_registros_arquivo += sequencial_registro + 2  # Header + Segmentos + Trailer

        else:
            # 🔄 Um lote por conta para outros bancos
            lote = 1
            for conta in odict_entrada['segmento_a_contas']:
                print(f"🧾 Gerando lote {lote} para banco diferente de 237...")
                header_lote = odict_entrada['header_lote'].copy()
                header_lote['lote'] = str(lote)
                str_header_lote = hl.header_lote(header_lote)

                odic_sega = sega.default()
                odic_sega['banco'] = codigo_banco
                odic_sega['sequencial_registro_lote'] = '1'
                odic_sega['banco_fv'] = conta['banco']
                odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
                odic_sega['empresa_conta_corrente_conta_dv'] = conf['empresa_conta_corrente_conta_dv']
                odic_sega['empresa_conta_corrente_agencia1'] = codigo_banco
                odic_sega['favorecido_conta_corrente_agencia_codigo'] = conta['agencia']
                odic_sega['favorecido_conta_corrente_agencia_dv'] = conta['agencia_dv']
                odic_sega['favorecido_conta_corrente_conta_numero'] = conta['conta']
                odic_sega['favorecido_nome'] = conta['favorecido_nome']
                seu_numero_complemento = str(datetime.now().strftime("%y")) + str(datetime.now().timetuple().tm_yday) + str(datetime.now().strftime("%H%M"))
                odic_sega['credito_seu_numero'] = conta.get('credito_seu_numero', conta['cpf'] + seu_numero_complemento)[:9]
                str_seg_a = sega.parse(odic_sega)

                odic_segb = segb.default()
                odic_segb['sequencial_registro_lote'] = '2'
                odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
                odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
                str_seg_b = segb.parse(odic_segb)

                print("➡️ Gerando trailer do lote...")
                odic_trailer_lote = tl.default()
                odic_trailer_lote['banco'] = codigo_banco
                odic_trailer_lote['lote'] = str(lote)
                odic_trailer_lote['quantidade_registro_lote'] = 4
                odic_trailer_lote['somatoria_valores'] = conta['valor_centavos']
                str_trailer_lote = tl.parse(odic_trailer_lote)

                conteudo_lotes.append(f"{str_header_lote}\n{str_seg_a}\n{str_seg_b}\n{str_trailer_lote}")
                total_registros_arquivo += 4  # Header lote + 2 segmentos + trailer lote
                lote += 1

        print("➡️ Gerando trailer do arquivo...")
        odic_trailer_arquivo = ta.default()
        odic_trailer_arquivo['banco'] = codigo_banco
        odic_trailer_arquivo['lote'] = '9999'
        odic_trailer_arquivo['quantidade_registros'] = total_registros_arquivo
        str_trailer_arquivo = ta.parse(odic_trailer_arquivo)

        print("✅ Geração concluída")
        conteudo = f"{str_header}\n" + '\n'.join(conteudo_lotes) + f"\n{str_trailer_arquivo}"
        filename = f"OCTCPSC{datetime.now().strftime('%d')}5.txt"
        return conteudo

    except Exception as e:
        print("❌ ERRO DURANTE A GERAÇÃO:", e)
        raise

    


