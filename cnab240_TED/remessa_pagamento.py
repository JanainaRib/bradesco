from datetime import datetime
from cnab240_TED.core import header_arquivo as ha
from cnab240_TED.core.header_lote import header_lote, default_header_lote
from cnab240_TED.core import trailer_arquivo as ta
from cnab240_TED.core.segmento_a import default as default_sega, parse as parse_sega
from cnab240_TED.core.segmento_b import default as default_segb, parse as parse_segb
from cnab240_TED.core.trailer_lote import default as default_trailer_lote, parse as parse_trailer_lote


def generate(odict_entrada, conf=None):
    if conf is None:
        print("Código do banco é um campo obrigatório")
        return None

    try:
        codigo_banco_empresa = conf['banco']
        str_header = ha.header_arquivo(odict_entrada['header_arquivo'])

        # Separar contas 237 e outros bancos
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

            # Pega o header lote padrão e atualiza os campos necessários
            header_lote_dict = default_header_lote()
            header_lote_dict.update(odict_entrada['header_lote'])
            header_lote_dict['lote'] = str(numero_lote)
            header_lote_dict['forma_lancamento'] = forma_lancamento
            str_header_lote = header_lote(header_lote_dict)

            for conta in contas:
                odic_sega = default_sega()
                odic_sega['banco'] = codigo_banco_empresa
                odic_sega['lote'] = str(numero_lote) 
                odic_segb['lote'] = str(numero_lote) 
                odic_sega['sequencial_registro_lote'] = str(sequencial_registro + 1)
                odic_sega['banco_fv'] = conta['banco']
                odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
                odic_sega['empresa_conta_corrente_conta_dv'] = conf['empresa_conta_corrente_conta_dv']
                odic_sega['empresa_conta_corrente_agencia1'] = codigo_banco_empresa
                odic_sega['favorecido_conta_corrente_agencia_codigo'] = conta['agencia']
                odic_sega['favorecido_conta_corrente_agencia_dv'] = conta['agencia_dv']
                odic_sega['favorecido_conta_corrente_conta_numero'] = conta['conta']
                odic_sega['favorecido_nome'] = conta['favorecido_nome']
                seu_numero_complemento = datetime.now().strftime("%y") + str(datetime.now().timetuple().tm_yday) + datetime.now().strftime("%H%M")
                odic_sega['credito_seu_numero'] = conta.get('credito_seu_numero', conta['cpf'] + seu_numero_complemento)[:9]
                # Ajusta finalidades conforme banco
                if conta['banco'] == '237':
                    odic_sega['finalidade_ted'] = '    '  # 4 espaços em branco
                    odic_sega['finalidade_complementar'] = '  '  # 2 espaços em branco
                else:
                    odic_sega['finalidade_ted'] = '00001'
                    odic_sega['finalidade_complementar'] = 'CC'
                str_seg_a = parse_sega(odic_sega)

                odic_segb = default_segb()
                odic_segb['sequencial_registro_lote'] = str(sequencial_registro + 2)
                odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
                odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
                str_seg_b = parse_segb(odic_segb)

                list_segmentos.append(str_seg_a)
                list_segmentos.append(str_seg_b)

                sequencial_registro += 2
                somatoria += conta['valor_centavos']

            trailer_lote_dict = default_trailer_lote()
            trailer_lote_dict['banco'] = codigo_banco_empresa
            trailer_lote_dict['lote'] = str(numero_lote)
            trailer_lote_dict['quantidade_registro_lote'] = sequencial_registro + 2  # header lote + trailer lote + segmentos
            trailer_lote_dict['somatoria_valores'] = somatoria
            str_trailer_lote = parse_trailer_lote(trailer_lote_dict)

            lote_completo = f"{str_header_lote}\n" + '\n'.join(list_segmentos) + f"\n{str_trailer_lote}"
            return lote_completo, sequencial_registro + 2

        # Processa lote para banco 237, se existir
        if contas_237:
            print("➡️ Processando lote para banco 237")
            lote_237, reg_237 = processar_lote(contas_237, lote_num, forma_lancamento='01')
            conteudo_lotes.append(lote_237)
            total_registros_arquivo += reg_237
            lote_num += 1

        # Processa lote para outros bancos, se existir
        if contas_outros:
            print("➡️ Processando lote para outros bancos")
            lote_outros, reg_outros = processar_lote(contas_outros, lote_num, forma_lancamento='41')
            conteudo_lotes.append(lote_outros)
            total_registros_arquivo += reg_outros
            lote_num += 1

        # Montar trailer do arquivo
        trailer_arquivo_dict = ta.default()
        trailer_arquivo_dict['banco'] = codigo_banco_empresa
        trailer_arquivo_dict['lote'] = '9999'
        trailer_arquivo_dict['quantidade_registros'] = total_registros_arquivo
        str_trailer_arquivo = ta.parse(trailer_arquivo_dict)

        conteudo = f"{str_header}\n" + '\n'.join(conteudo_lotes) + f"\n{str_trailer_arquivo}"
        print("✅ Geração concluída")
        return conteudo

    except Exception as e:
        print("❌ ERRO DURANTE A GERAÇÃO:", e)
        raise

