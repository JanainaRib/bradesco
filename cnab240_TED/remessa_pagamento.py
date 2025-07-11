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
        codigo_banco_empresa = conf['banco']
        str_header = ha.header_arquivo(odict_entrada['header_arquivo'])

        contas_237 = []
        contas_outros = []

        for conta in odict_entrada['segmento_a_contas']:
            if conta['banco'] == '237':
                contas_237.append(conta)
            else:
                contas_outros.append(conta)

        conteudo_lotes = []
        total_registros_arquivo = 2  # header_arquivo + trailer_arquivo
        lote_num = 1

        def processar_lote(contas, numero_lote, forma_lancamento):
            list_segmentos = []
            somatoria = 0
            sequencial_registro = 0

            header_lote = hl.default()
            header_lote.update(odict_entrada['header_lote'])
            header_lote['lote'] = str(numero_lote)
            header_lote['forma_lancamento'] = forma_lancamento
            str_header_lote = hl.header_lote(header_lote)

            for conta in contas:
                odic_sega = sega.default()
                odic_sega['banco'] = codigo_banco_empresa
                odic_sega['sequencial_registro_lote'] = str(sequencial_registro + 1)
                odic_sega['banco_fv'] = conta['banco']
                odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
                odic_sega['empresa_conta_corrente_conta_dv'] = conf['empresa_conta_corrente_conta_dv']
                odic_sega['empresa_conta_corrente_agencia1'] = codigo_banco_empresa
                odic_sega['favorecido_conta_corrente_agencia_codigo'] = conta['agencia']
                odic_sega['favorecido_conta_corrente_agencia_dv'] = conta['agencia_dv']
                odic_sega['favorecido_conta_corrente_conta_numero'] = conta['conta']
                odic_sega['favorecido_nome'] = conta['favorecido_nome']
                seu_numero_complemento = str(datetime.now().strftime("%y")) + str(datetime.now().timetuple().tm_yday) + str(datetime.now().strftime("%H%M"))
                odic_sega['credito_seu_numero'] = conta.get('credito_seu_numero', conta['cpf'] + seu_numero_complemento)[:9]

                # Campos TED obrigatórios
                odic_sega['finalidade_ted'] = '    '
                odic_sega['finalidade_complementar'] = '  '

                str_seg_a = sega.parse(odic_sega)

                odic_segb = segb.default()
                odic_segb['sequencial_registro_lote'] = str(sequencial_registro + 2)
                odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
                odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
                str_seg_b = segb.parse(odic_segb)

                list_segmentos.append(str_seg_a)
                list_segmentos.append(str_seg_b)

                sequencial_registro += 2
                somatoria += conta['valor_centavos']

            trailer_lote = tl.default()
            trailer_lote['banco'] = codigo_banco_empresa
            trailer_lote['lote'] = str(numero_lote)
            trailer_lote['quantidade_registro_lote'] = sequencial_registro + 2  # +2 do header + trailer
            trailer_lote['somatoria_valores'] = somatoria
            str_trailer_lote = tl.parse(trailer_lote)

            lote_completo = f"{str_header_lote}\n" + '\n'.join(list_segmentos) + f"\n{str_trailer_lote}"
            return lote_completo, sequencial_registro + 2

        # Lote 1: Banco 237
        if contas_237:
            print("➡️ Processando lote para banco 237")
            lote_237, reg_237 = processar_lote(contas_237, lote_num, forma_lancamento='01')  # Crédito em conta corrente
            conteudo_lotes.append(lote_237)
            total_registros_arquivo += reg_237
            lote_num += 1

        # Lote 2: Outros bancos
        if contas_outros:
            print("➡️ Processando lote para outros bancos")
            lote_outros, reg_outros = processar_lote(contas_outros, lote_num, forma_lancamento='41')  # TED
            conteudo_lotes.append(lote_outros)
            total_registros_arquivo += reg_outros
            lote_num += 1

        trailer_arquivo = ta.default()
        trailer_arquivo['banco'] = codigo_banco_empresa
        trailer_arquivo['lote'] = '9999'
        trailer_arquivo['quantidade_registros'] = total_registros_arquivo
        str_trailer_arquivo = ta.parse(trailer_arquivo)

        conteudo = f"{str_header}\n" + '\n'.join(conteudo_lotes) + f"\n{str_trailer_arquivo}"
        print("✅ Geração concluída")
        return conteudo

    except Exception as e:
        print("❌ ERRO DURANTE A GERAÇÃO:", e)
        raise

