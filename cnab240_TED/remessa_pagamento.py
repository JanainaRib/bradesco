def generate(odict_entrada, conf=None):
    if conf is None:
        print("Código do banco é um campo obrigatório")
        return None, None

    try:
        codigo_banco_empresa = conf['banco']
        str_header = ha.header_arquivo(odict_entrada['header_arquivo'])
        conteudo_lotes = []
        total_registros_arquivo = 2  # Header + Trailer do arquivo

        lote_num = 1
        sequencial_registro = 0
        somatoria_de_valores_237 = 0
        lista_237_segmentos = []

        contas_237 = []
        contas_outros = []

        for conta in odict_entrada['segmento_a_contas']:
            if conta['banco'] == '237':
                contas_237.append(conta)
            else:
                contas_outros.append(conta)

        # ✅ Lote único para contas do banco 237
        if contas_237:
            print("➡️ Gerando lote único para banco 237")
            header_lote = odict_entrada['header_lote'].copy()
            header_lote['lote'] = str(lote_num)
            str_header_lote = hl.header_lote(header_lote)

            for conta in contas_237:
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
                str_seg_a = sega.parse(odic_sega)

                odic_segb = segb.default()
                odic_segb['sequencial_registro_lote'] = str(sequencial_registro + 2)
                odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
                odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
                str_seg_b = segb.parse(odic_segb)

                lista_237_segmentos.append(str_seg_a)
                lista_237_segmentos.append(str_seg_b)

                sequencial_registro += 2
                somatoria_de_valores_237 += conta['valor_centavos']

            trailer_lote = tl.default()
            trailer_lote['banco'] = codigo_banco_empresa
            trailer_lote['lote'] = str(lote_num)
            trailer_lote['quantidade_registro_lote'] = sequencial_registro + 2
            trailer_lote['somatoria_valores'] = somatoria_de_valores_237
            str_trailer_lote = tl.parse(trailer_lote)

            conteudo_lotes.append(f"{str_header_lote}\n" + '\n'.join(lista_237_segmentos) + f"\n{str_trailer_lote}")
            total_registros_arquivo += sequencial_registro + 2
            lote_num += 1

        # 🔄 Lote individual para os demais bancos
        for conta in contas_outros:
            print(f"➡️ Gerando lote individual para banco {conta['banco']}")
            header_lote = odict_entrada['header_lote'].copy()
            header_lote['lote'] = str(lote_num)
            str_header_lote = hl.header_lote(header_lote)

            odic_sega = sega.default()
            odic_sega['banco'] = codigo_banco_empresa
            odic_sega['sequencial_registro_lote'] = '1'
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
            str_seg_a = sega.parse(odic_sega)

            odic_segb = segb.default()
            odic_segb['sequencial_registro_lote'] = '2'
            odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']
            odic_segb['dados_complementares_pagamento_valor_documento'] = str(conta['valor_centavos'])
            str_seg_b = segb.parse(odic_segb)

            trailer_lote = tl.default()
            trailer_lote['banco'] = codigo_banco_empresa
            trailer_lote['lote'] = str(lote_num)
            trailer_lote['quantidade_registro_lote'] = 4
            trailer_lote['somatoria_valores'] = conta['valor_centavos']
            str_trailer_lote = tl.parse(trailer_lote)

            conteudo_lotes.append(f"{str_header_lote}\n{str_seg_a}\n{str_seg_b}\n{str_trailer_lote}")
            total_registros_arquivo += 4
            lote_num += 1

        # 🎯 Trailer do arquivo
        trailer_arquivo = ta.default()
        trailer_arquivo['banco'] = codigo_banco_empresa
        trailer_arquivo['lote'] = '9999'
        trailer_arquivo['quantidade_registros'] = total_registros_arquivo
        str_trailer_arquivo = ta.parse(trailer_arquivo)

        print("✅ Geração concluída")
        conteudo = f"{str_header}\n" + '\n'.join(conteudo_lotes) + f"\n{str_trailer_arquivo}"
        filename = f"OCTCPSC{datetime.now().strftime('%d')}5.txt"
        return conteudo

    except Exception as e:
        print("❌ ERRO DURANTE A GERAÇÃO:", e)
        raise
