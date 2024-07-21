import os
import re
import json
import pdfplumber

def limpar_caracteres_especiais(texto):
    # Substituindo caracteres especiais por suas formas legíveis
    texto_limpo = texto.encode('utf-8', 'replace').decode('utf-8', 'replace')
    return texto_limpo

def procurar_valor_por_padrao(linhas, padrao, fallback_padrao=None, ignore_first=False):
    # Procurando pelo padrão em cada linha e retorna o valor encontrado
    contador = 0
    for linha in linhas:
        correspondencia = re.search(padrao, linha)
        if correspondencia:
            if ignore_first and contador == 0:
                contador += 1
            else:
                valor = limpar_caracteres_especiais(correspondencia.group().strip())
                return valor

    # Se não encontrar o padrão principal, o fallback_padrao deve atuar 
    if fallback_padrao:
        for linha in linhas:
            correspondencia_fallback = re.search(fallback_padrao, linha)
            if correspondencia_fallback:
                valor_fallback = limpar_caracteres_especiais(correspondencia_fallback.group().strip())
                return valor_fallback

    return ""

def extrair_dados_txt(linhas):
    dados = {
        "cabecalho": {
            "doc": "FORMULÁRIO PARA SOLICITAÇÃO DE NOVO COMPARTILHAMENTO E AMPLIAÇÃO",
            "type": "SCI",
            "number": procurar_valor_por_padrao(linhas, r'(?<= - ).*?(?=-)'),
            "data_solicitacao": procurar_valor_por_padrao(linhas, r'(?<=Data da Solicitação:).*?(?=\sCompartilhamento:)'),
            "compartilhamento": procurar_valor_por_padrao(linhas, r'(?<=Compartilhamento:).*'),
        },
        "identificacao_do_site": {
            "cliente": procurar_valor_por_padrao(linhas, r'(?<=Cliente Solicitante:).*?(?=\sEndereço do Site:)'),
            "endereco_do_site": procurar_valor_por_padrao(linhas, r'(?<=Endereço do Site:).*'),
            "nome_solicitante": procurar_valor_por_padrao(linhas, r'(?<=Nome Solicitante:).*'),
            "nome": procurar_valor_por_padrao(linhas, r'(?<=/ Site -).*'),
            "id_detentora": procurar_valor_por_padrao(linhas, r'(?<=ID Detentora:).*'),
            "cidade": procurar_valor_por_padrao(linhas, r'(?<=Cidade:).*?(?=\sSite:)'),
            "site": procurar_valor_por_padrao(linhas, r'(?<=Site:).*', r'(?<=Site:).*', ignore_first=True),
            "estado": procurar_valor_por_padrao(linhas, r'(?<=Estado:).*'),
            "latitude": procurar_valor_por_padrao(linhas, r'(?<=Latitude:).*?(?=\sEstado:)'),
            "longitude": procurar_valor_por_padrao(linhas, r'(?<=Longitude:).*'),
            "finalidade": procurar_valor_por_padrao(linhas, r'(?<=Finalidade:).*'),
            "registro_1": procurar_valor_por_padrao(linhas, r'(?<=Registro 1:).*?(?=\sRegistro 2:)'),
            "registro_2": procurar_valor_por_padrao(linhas, r'(?<=Registro 2:).*'),
            "registro_3": procurar_valor_por_padrao(linhas, r'(?<=Registro 3:).*?(?=\sRegistro 4:)'),
            "registro_4": procurar_valor_por_padrao(linhas, r'(?<=Registro 4:).*'),
        },
        "identificacao_da_tecnologia": {
            "tec": procurar_valor_por_padrao(linhas, r'(?<=\[x\]).*?(?=\[ ])', r'(?<=\[x\]).*'),
        }
    }
    return dados

def extrair_dados_pdf_e_json(caminho_pdf, pasta_destino):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        encontrado = False

        # Itera pelas páginas do PDF
        for pagina in pdf.pages:
            # Extrai o texto da página
            texto_pagina = pagina.extract_text()

            # Adiciona o texto da página à variável de texto completo
            texto_completo += texto_pagina

        # Se o texto foi extraído, processa os dados
        if texto_completo:
            linhas = texto_completo.split('\n')
            dados_json = extrair_dados_txt(linhas)

            # Criando o caminho do arquivo JSON de destino
            nome_arquivo = os.path.splitext(os.path.basename(caminho_pdf))[0]
            caminho_destino_json = os.path.join(pasta_destino, f"{nome_arquivo}.json")

            # Salvando o JSON no arquivo de destino
            with open(caminho_destino_json, 'w', encoding='utf-8') as json_file:
                json.dump(dados_json, json_file, indent=2, ensure_ascii=False)

            print(f"Arquivo JSON salvo em: {caminho_destino_json}")
        else:
            print("Não foi possível extrair texto do PDF.")

def processar_pasta_pdf(pasta_origem, pasta_destino):
    # Garantindo que a pasta de destino existe
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Iterando sobre os arquivos na pasta de origem
    for arquivo in os.listdir(pasta_origem):
        if arquivo.lower().endswith('.pdf'):
            caminho_pdf = os.path.join(pasta_origem, arquivo)
            extrair_dados_pdf_e_json(caminho_pdf, pasta_destino)

# Caminho da pasta com arquivos PDF
pasta_origem_pdf = 'C:/PDF TO JSON/arqv PDF'

# Pasta de destino para os arquivos JSON
pasta_destino_json = 'C:/PDF TO JSON/arqv JSON'

# Processando a pasta de arquivos PDF
processar_pasta_pdf(pasta_origem_pdf, pasta_destino_json)
