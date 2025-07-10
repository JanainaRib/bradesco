import collections

def parse(dic_lote):

    #merge
    merged_dict = dic_lote# default_header_arquivo().update( dic_header )
    header_str = '{:0>3.3}{:0>4.4}{:0>1.1}{:0>5.5}{:<1.1}{:<3.3}{:<1.1}{:0>14.14}{:<35.35}{:<60.60}{:<99.99}{:0>6.6}{:0>8.8}'
    
    return header_str.format(*merged_dict.values())

def default():

    odict = collections.OrderedDict()
    
    odict['banco'] = '237' #G001
    odict['lote'] = '1'#G002
    odict['registro'] = '3' #G003
    odict['sequencial_registro_lote'] = '1' #G038
    odict['constante'] = 'B'#G039
    odict['tipo_chave'] = '05' #G100 #“01” – Chave Pix – tipo Telefone “02” – Chave Pix – tipo Email “03” – Chave Pix – tipo CPF/CNPJ “04” – Chave Aleatoria “05” - Dados Bancários
    odict['tipo_incricao'] = '2' #G005
    odict['dados_complementares_favorecido_inscricao_numero'] = '' #G006
    odict['info10'] = '' #brancos 
    odict['info11'] = '' #brancos
    odict['info12'] = '01' #chavepix ou 01 CONTA CORRENTE
    odict['UG'] = '' #P012
    odict['ISPB'] = ''#P015


    return odict