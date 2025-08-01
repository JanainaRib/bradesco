from datetime import datetime
import cnab240.core.header_arquivo as ha
import cnab240.core.header_lote as hl
import cnab240.core.trailer_arquivo as ta
import cnab240.core.segmento_a as sega
import cnab240.core.segmento_b as segb
import cnab240.core.trailer_lote as tl


def generate(odict_entrada, conf=None):

    if conf is None:
        print("Código do banco é um campo obrigatório")
        return None, None
    
    codigo_banco = conf['banco']
    lote = '1'

    str_header = ha.header_arquivo(odict_entrada['header_arquivo'])
    str_header_lote = hl.header_lote(odict_entrada['header_lote'])

    list_segmento_a = []
    somatoria_de_valores = 0
    sequencial_registro = 0

    for conta in odict_entrada['segmento_a_contas']:
        odic_sega = sega.default()
        odic_sega['banco'] = codigo_banco
        odic_segb = segb.default()
        odic_sega['sequencial_registro_lote'] = str(sequencial_registro + 1)
        odic_sega['banco_fv'] = conta['banco']
        odic_segb['sequencial_registro_lote'] = str(sequencial_registro + 2)
        odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
        odic_sega['empresa_conta_corrente_conta_dv'] = conf['empresa_conta_corrente_conta_dv']  
        odic_sega['empresa_conta_corrente_agencia1'] = codigo_banco
        
        odic_sega['favorecido_conta_corrente_agencia_codigo'] = conta['agencia']
        odic_sega['favorecido_conta_corrente_agencia_dv'] = conta['agencia_dv']
        odic_sega['favorecido_conta_corrente_conta_numero'] = conta['conta']
        odic_sega['favorecido_nome'] = conta['favorecido_nome']
        odic_sega['valor_pagamento'] = str(conta['valor_centavos'])
        infopix = conta['cpf'] + "6074694801"
        odic_sega['info_pix'] =  infopix

        seu_numero_complemento = str(datetime.now().strftime("%y")) + str(datetime.now().timetuple().tm_yday) + str(datetime.now().strftime("%H%M"))
        if 'credito_seu_numero' in conta.keys():
            odic_sega['credito_seu_numero'] = conta['credito_seu_numero'][:9]
        else:
            odic_sega['credito_seu_numero'] = conta['cpf'] + seu_numero_complemento

        odic_segb['dados_complementares_favorecido_inscricao_numero'] = conta['cpf']

        list_segmento_a.append(sega.parse(odic_sega))
        list_segmento_a.append(segb.parse(odic_segb))
        # Note que segc não está sendo usado para montar o arquivo, confirme se precisa adicionar

        sequencial_registro += 2
        somatoria_de_valores += conta['valor_centavos']

    odic_trailer_lote = tl.default()
    odic_trailer_lote['banco'] = codigo_banco
    odic_trailer_lote['lote'] = lote
    odic_trailer_lote['quantidade_registro_lote'] = sequencial_registro + 2  # Header + trailer lote
    odic_trailer_lote['somatoria_valores'] = somatoria_de_valores
    str_trailer_lote = tl.parse(odic_trailer_lote)

    odic_trailer_arquivo = ta.default()
    odic_trailer_arquivo['banco'] = codigo_banco
    odic_trailer_arquivo['lote'] = '9999'
    odic_trailer_arquivo['quantidade_registros'] = 1 + 1 + 1 + 1 + sequencial_registro
    str_trailer_arquivo = ta.parse(odic_trailer_arquivo)

    str_segmento = '\n'.join(list_segmento_a)
    conteudo = f"{str_header}\n{str_header_lote}\n{str_segmento}\n{str_trailer_lote}\n{str_trailer_arquivo}"

    # Gerar nome do arquivo baseado no primeiro conta (pode ajustar)
    filename = f"OCTCPSCBPPIX{datetime.now().strftime('%d%m')}.txt"

    # Retorna o conteúdo e o nome do arquivo
    return conteudo, filename

    


