import collections
from datetime import datetime 

def parse(dic_lote):

    #merge
    merged_dict = dic_lote# default_header_arquivo().update( dic_header )
    header_str = '{:0>3.3}{:0>4.4}{:<1.1}{:0>5.5}{:<1.1}{:<1.1}{:<2.2}{:0>3.3}{:0>3.3}{:0>5.5}{:0>1.1}{:0>13.13}{:<1.1}{:<30.30}{:0>15.15}{:0>5.5}{:<8.8}{:<3.3}{:0>15.15}{:0>15.15}{:0>20.20}{:<8.8}{:0>15.15}{:<40.40}{:<2.2}{:0>5.5}{:<2.2}{:<3.3}{:0>1.1}{:<10.10}'
    #'{:0>1.1}{:0>4.4}{:<2.2}{:0>5.5}{:<1.1}{:<6.6}{:<35.35}{:<13.13}{:<1.1}{:0>13.13}{:<1.1}{:0>5.5}{:<1.1}{:<6.6}'
    return header_str.format(*merged_dict.values())

datetime_now = datetime.now()
def default():
    
    odict = collections.OrderedDict()
    odict['banco'] = '237' #G001
    odict['lote'] = '1' #G002
    odict['registro'] = '3' #G003
    odict['sequencial_registro_lote'] = '1' #G038
    odict['constante'] = 'A'#G039
    odict['tipo_movimento'] = '0' #G060
    odict['cód_instrucao_movimento'] = '09' #G061
    odict['cód_camara'] = '018' #P001 #TED 018 E PIX 009
    odict['banco_fv'] = '' #P002
    odict['favorecido_conta_corrente_agencia_codigo'] = '' #G008
    odict['favorecido_conta_corrente_agencia_dv'] = ''
    odict['favorecido_conta_corrente_conta_numero'] = '' #G010
    odict['zero'] = '' #G012
    odict['favorecido_nome'] = ''  #G013
    odict['credito_seu_numero'] = '' #G064
    odict['zero1'] = '00000' #G064
    odict['arquivo_data_geracao'] = datetime_now.strftime("%d%m%Y") #P009
    odict['moeda'] = 'BRL' #G040
    odict['zero2'] = '' #G040
    odict['valor_pagamento'] = '' #P010
    odict['cnab_1aa'] = '                    ' #G043
    odict['arquivo_data_efetivacao'] = datetime_now.strftime("%d%m%Y") #P003
    odict['total_cheque'] ='' #P004
    odict['info_pix'] = ''
    odict['G004'] = ''
    odict['finalidade_ted'] = '1'
    odict['finalidade_complementar'] = 'CC'
    odict['G004_1'] = ''
    odict['aviso'] = '0'
    odict['ocorrencias'] = ''
    return odict
