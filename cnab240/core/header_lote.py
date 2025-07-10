import collections

def header_lote(dic_lote):

    #merge
    merged_dict = dic_lote# default_header_arquivo().update( dic_header )
    header_str = '{:0>3.3}{:0>4.4}{:<1.1}{:<1.1}{:<2.2}{:<2.2}{:<3.3}{:<1.1}{:<1.1}{:<14.14}{:<20.20}{:0>5.5}{:<1.1}{:0>12.12}{:<1.1}{:<1.1}{:<30.30}{:<40.40}{:<30.30}{:<5.5}{:<15.15}{:<20.20}{:<5.5}{:<3.3}{:<2.2}{:<2.2}{:<6.6}{:<10.10}'
    
    return header_str.format(*merged_dict.values())

def default_header_lote():
    
    odict = collections.OrderedDict()

    odict['banco'] = '237' #G001
    odict['lote'] = '1' #G002
    odict['registro'] = '1' #G003
    odict['operacao'] = 'C' #G028
    odict['servico'] = '20' #G025
    odict['forma_lancamento'] = '45'  #G029
    odict['versao_layout_lote'] = '045' #G030
    odict['cnab_081'] = '' #G004
    odict['empresa_inscricao_tipo'] ='2' #1 Pessoa Fisica, 2 Pessoa Juridica
    odict['empresa_inscricao_numero'] ='' #G006
    odict['empresa_convenio'] ='' #G007
    odict['empresa_conta_corrente_agencia'] ='' #G008
    odict['empresa_conta_corrente_agencia_dv'] ='' #G009
    odict['empresa_conta_corrente_conta_numero'] ='' #G010
    odict['empresa_conta_corrente_conta_dv'] ='' #G011
    odict['empresa_conta_corrente_digito_verificador'] ='' #G012 
    odict['empresa_nome'] ='' #G013
    odict['mensagem'] ='' #G031
    odict['empresa_endereco_logradouro'] ='' #G032
    odict['empresa_endereco_numero'] ='' #G032
    odict['empresa_endereco_complemento'] ='' #G032   
    odict['empresa_endereco_cidade'] =''#G033
    odict['empresa_endereco_cep'] ='' #G034
    odict['empresa_endereco_cep_complemento'] ='' #G035
    odict['empresa_endereco_estado'] ='' #G036
    odict['indicativo_forma_pagamento_servico'] = '01' #P014
    odict['cnab_271'] = '' #G004
    odict['codigo_ocorrencias_retorno'] = '' #G059

    return odict