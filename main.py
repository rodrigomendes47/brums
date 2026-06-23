import pandas as pd
import os

def calcular_escores(df_entrada, df_percentil, diretorio_saida=None):
    """
    Calcula escores brutos, converte para T-Escores com base em percentis e estrutura a saída.
    """
    print("- Calculando Escores Brutos...")
    
    # Agrupamento exato conforme regras especificadas
    df_entrada['EB_Tensão'] = df_entrada[['ansioso', 'preocupado', 'tenso', 'apavorado']].sum(axis=1)
    df_entrada['EB_Depressão'] = df_entrada[['deprimido', 'desanimado', 'triste', 'infeliz']].sum(axis=1)
    df_entrada['EB_Raiva'] = df_entrada[['irritado', 'zangado', 'com_raiva', 'mal_humorado']].sum(axis=1)
    df_entrada['EB_Vigor'] = df_entrada[['animado', 'com_disposição', 'com_energia', 'alerta']].sum(axis=1)
    df_entrada['EB_Fadiga'] = df_entrada[['esgotado', 'exausto', 'sonolento', 'cansado']].sum(axis=1)
    df_entrada['EB_Confusão'] = df_entrada[['confuso', 'inseguro', 'desorientado', 'indeciso']].sum(axis=1)

    print("- Mapeando T-Escores...")
    
    col_score_bruto = df_percentil.columns[0] 
    df_percentil = df_percentil.dropna(subset=[col_score_bruto])
    
    map_tensao = dict(zip(df_percentil[col_score_bruto], df_percentil['Tensão']))
    map_depressao = dict(zip(df_percentil[col_score_bruto], df_percentil['Depressão']))
    map_raiva = dict(zip(df_percentil[col_score_bruto], df_percentil['Raiva']))
    map_vigor = dict(zip(df_percentil[col_score_bruto], df_percentil['Vigor*']))
    map_fadiga = dict(zip(df_percentil[col_score_bruto], df_percentil['Fadiga']))
    map_confusao = dict(zip(df_percentil[col_score_bruto], df_percentil['Confusão']))

    df_entrada['Tensão'] = df_entrada['EB_Tensão'].map(map_tensao)
    df_entrada['Depressão'] = df_entrada['EB_Depressão'].map(map_depressao)
    df_entrada['Raiva'] = df_entrada['EB_Raiva'].map(map_raiva)
    df_entrada['Vigor*'] = df_entrada['EB_Vigor'].map(map_vigor)
    df_entrada['Fadiga'] = df_entrada['EB_Fadiga'].map(map_fadiga)
    df_entrada['Confusão'] = df_entrada['EB_Confusão'].map(map_confusao)

    print("- Estruturando DataFrames de Saída...")
    
    colunas_identidade = ['ID', 'Nome', 'CPF', 'data']
    cols_id_presentes = [col for col in colunas_identidade if col in df_entrada.columns]
    fatores = ['Tensão', 'Depressão', 'Raiva', 'Vigor*', 'Fadiga', 'Confusão']
    
    df_wide = df_entrada[cols_id_presentes + fatores].copy()
    
    df_long = pd.melt(
        df_wide,
        id_vars=cols_id_presentes,
        value_vars=fatores,
        var_name='Cat',
        value_name='valor'
    )

    if diretorio_saida:
        os.makedirs(diretorio_saida, exist_ok=True)
        caminho_wide = os.path.join(diretorio_saida, 'BI_BRUMS_Wide.csv')
        caminho_long = os.path.join(diretorio_saida, 'BI_BRUMS_Long.csv')
        
        df_wide.to_csv(caminho_wide, index=False, encoding='utf-8-sig', sep=';')
        df_long.to_csv(caminho_long, index=False, encoding='utf-8-sig', sep=';')
        
        print(f"\n[SUCESSO] Arquivos gerados com sucesso:")
        print(f" -> Tabela Larga: {caminho_wide}")
        print(f" -> Tabela Longa: {caminho_long}")
        
    return df_wide, df_long

def processar_dados_brums(caminho_entrada, diretorio_saida, data_inicio=None):
    """
    Processa dados do questionário BRUMS lendo um arquivo Excel.
    """
    print("Iniciando o processamento dos dados...")
    try:
        print("- Carregando aba 'entrada'...")
        df_entrada = pd.read_excel(caminho_entrada, sheet_name='entrada')
        
        if 'data' in df_entrada.columns:
            df_entrada['data'] = pd.to_datetime(df_entrada['data'], errors='coerce')
            if data_inicio is not None:
                df_entrada = df_entrada[df_entrada['data'] >= data_inicio].copy()
                print(f" -> Filtrando registros a partir de: {data_inicio.strftime('%d/%m/%Y')}")
        
        print("- Carregando aba 'Percentil'...")
        df_percentil = pd.read_excel(caminho_entrada, sheet_name='Percentil')
        
        return calcular_escores(df_entrada, df_percentil, diretorio_saida)

    except Exception as e:
        print(f"\n[ERRO] Falha ao processar os dados: {e}")
        return None, None

# ==========================================
# Ponto de Execução do Script
# ==========================================
if __name__ == "__main__":
    # Substitua pelas strings do nome/caminho correto do seu arquivo Excel
    ARQUIVO_EXCEL_ENTRADA = 'dados_brums.xlsx' 
    DIRETORIO_DE_SAIDA = './saida_bi'
    
    # Solicita a data de início ao usuário
    data_inicio = None
    while True:
        data_input = input("Digite a data de início (dd/mm/aaaa) ou pressione Enter para processar tudo: ").strip()
        if not data_input:
            break
        try:
            data_inicio = pd.to_datetime(data_input, format='%d/%m/%Y')
            break
        except ValueError:
            print("Formato de data inválido! Use dd/mm/aaaa (Exemplo: 15/04/2026).")
    
    # Chama a função com a data de início (caso fornecida)
    df_bi_largo, df_bi_longo = processar_dados_brums(ARQUIVO_EXCEL_ENTRADA, DIRETORIO_DE_SAIDA, data_inicio)
    
    # Pré-visualização rápida do dataframe unpivoted caso tenha processado corretamente
    if df_bi_longo is not None:
        print("\nPrévia da Tabela Longa (Melted):")
        print(df_bi_longo.head(10))
