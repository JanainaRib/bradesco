import collections
from datetime import datetime 

def parse(dic_lote):

    #merge
    merged_dict = dic_lote# default_header_arquivo().update( dic_header )
    header_str = '{:0>3.3}{:0>4.4}{:0>1.1}{:0>5.5}{:1.1}{:<3.3}{:0>1.1}{:0>14.14}{:<30.30}{:0>5.5}{:<15.15}{:<15.15}{:<20.20}{:0>5.5}{:<3.3}{:<2.2}{:0>8.8}{:0>15.15}{:0>15.15}{:0>15.15}{:0>15.15}{:0>15.15}{:<15.15}{:>1.1}{:>6.6}{:>8.8}'
    
    return header_str.format(*merged_dict.values())
datetime_now = datetime.now()
def default():

    odict = collections.OrderedDict()
    
    odict['banco'] = '237' #G001
    odict['lote'] = '1'#G002
    odict['registro'] = '3' #G003
    odict['sequencial_registro_lote'] = '1' #G038
    odict['constante'] = 'B'#G039
    odict['tipo_chave'] = '' #G100 #“01” – Chave Pix – tipo Telefone “02” – Chave Pix – tipo Email “03” – Chave Pix – tipo CPF/CNPJ “04” – Chave Aleatoria “05” - Dados Bancários
    odict['dados_complementares_favorecido_inscricao_tipo'] = '2' #G005
    odict['dados_complementares_favorecido_inscricao_numero'] = '' #cpf ou cnpj

    odict['dados_complementares_favorecido_logradouro'] = '' #
    odict['dados_complementares_favorecido_numero'] = '' #
    odict['dados_complementares_favorecido_complemento'] = '' #
    odict['dados_complementares_favorecido_bairro'] = '' #
    odict['dados_complementares_favorecido_cidade'] = '' #
    odict['dados_complementares_favorecido_cep'] = '' #
    odict['dados_complementares_favorecido_cep_complemento'] = '' #
    odict['dados_complementares_favorecido_estado'] = '' #
    odict['dados_complementares_pagamento_vencimento'] = datetime_now.strftime("%d%m%Y") #
    odict['dados_complementares_pagamento_valor_documento'] = '' #
    odict['dados_complementares_pagamento_abatimento'] = '' #
    odict['dados_complementares_pagamento_desconto'] = '' #
    odict['dados_complementares_pagamento_mora'] = '' #
    odict['dados_complementares_pagamento_multa'] = '' #
    odict['dados_complementares_codigo_documento_favorecido'] = '' #
    odict['aviso'] = '0' 
    odict['UG'] = '' #P012
    odict['ISPB'] = ''#P015


    return odict