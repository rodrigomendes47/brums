import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os

def criar_relatorios_brums_pdf(caminho_csv, caminho_header, diretorio_saida, progress_callback=None):
    """
    Gera relatórios PDF individuais do BRUMS a partir da tabela Wide.
    """
    # 1. Carrega os dados Wide já processados
    print("Lendo a base de dados...")
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig')
    
    # Cria o diretório de saída para os PDFs
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # Converte a coluna de datas se existir para ordenação cronológica
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df = df.sort_values(by='data')

    fatores_colunas = ['Tensão', 'Depressão', 'Raiva', 'Vigor*', 'Fadiga', 'Confusão']
    labels_eixo_x = ['Ten.', 'Dep.', 'Raiva', 'Vig.', 'Fad.', 'Conf.']

    # Agrupa os dados pelo CPF (cada CPF terá um relatório com 1 ou mais linhas)
    agrupado_por_cpf = df.groupby('CPF')
    total_atletas = len(agrupado_por_cpf)

    print(f"Gerando relatórios para {total_atletas} atleta(s)...")

    # 2. Itera sobre cada indivíduo para gerar seu relatório
    for i, (cpf_atleta, grupo) in enumerate(agrupado_por_cpf):
        # Pega o nome do primeiro registro
        nome_atleta = grupo['Nome'].iloc[0]
        
        # 3. Configuração da Figura (Tamanho A4 retrato aproximadamente)
        fig, ax = plt.subplots(figsize=(8, 11))
        
        # 4. Adiciona a imagem de cabeçalho com 100% de largura
        header_height_fraction = 0.12  # Valor padrão de fallback
        try:
            header_img = mpimg.imread(caminho_header)
            h, w = header_img.shape[:2]
            aspect_ratio = h / w
            fig_width_inches, fig_height_inches = fig.get_size_inches()
            # Calcula a proporção exata para cobrir 100% da largura mantendo o aspect ratio
            header_height_fraction = (fig_width_inches * aspect_ratio) / fig_height_inches
            
            # Adiciona os eixos cobrindo de x=0 a x=1 no topo
            ax_header = fig.add_axes([0, 1.0 - header_height_fraction, 1, header_height_fraction])
            ax_header.imshow(header_img, aspect='auto')
            ax_header.axis('off')
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o cabeçalho '{caminho_header}': {e}")
            header_height_fraction = 0.10

        # 5. Adiciona Nome do Atleta abaixo do cabeçalho
        y_atleta = 1.0 - header_height_fraction - 0.04
        y_cpf = 1.0 - header_height_fraction - 0.07
        
        plt.figtext(0.08, y_atleta, f"Atleta: {nome_atleta}", ha="left", fontsize=14, fontweight='bold', color='#2c3e50')
        plt.figtext(0.08, y_cpf, f"CPF: {cpf_atleta}", ha="left", fontsize=11, color='#777777')
        
        # Ajusta a posição do gráfico para ficar perfeitamente centralizado
        # Deixando uma margem dinâmica de acordo com a altura do cabeçalho
        top_chart = 1.0 - header_height_fraction - 0.13
        plt.subplots_adjust(top=top_chart, bottom=0.22, left=0.15, right=0.85)

        # 6. Plotagem da Linha para cada data
        for index, row in grupo.iterrows():
            t_escores = row[fatores_colunas].values
            
            # Prepara o rótulo da data para a legenda
            if 'data' in row and pd.notna(row['data']):
                if isinstance(row['data'], str):
                    data_str = row['data']
                else:
                    data_str = row['data'].strftime('%d/%m/%Y')
            else:
                data_str = "Sem Data"

            # Plota a linha dessa avaliação
            linha = ax.plot(labels_eixo_x, t_escores, marker='o', linestyle='-', linewidth=2, markersize=8, label=data_str)

        # Adiciona a legenda identificando as datas (centralizada na parte inferior externa do gráfico)
        ax.legend(title="Data da Avaliação", loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True)

        # 7. Formatação do Eixo Y (Escala de 30 a 80)
        ax.set_ylim(25, 85)
        ax.set_yticks(range(30, 81, 5))
        ax.set_ylabel('T-Escore', fontsize=12, fontweight='bold')
        
        # 8. Linhas de Referência
        ax.axhline(y=50, color='black', linestyle='-', linewidth=2)
        ax.yaxis.grid(True, linestyle='--', color='#d3d3d3', alpha=0.7)
        ax.xaxis.grid(True, linestyle='-', color='#d3d3d3', alpha=1.0)
        
        # Define os ticks antes dos labels para evitar warnings do Matplotlib
        ax.set_xticks(range(len(labels_eixo_x)))
        ax.set_xticklabels(labels_eixo_x, fontsize=12, fontweight='bold')
        ax.set_title("Perfil de Humor", fontsize=14, pad=20)
        
        # 9. Salva o PDF
        # Padrão de nome: BRUMS_Nome_5PrimeirosDoCPF
        cpf_digitos = "".join(c for c in str(cpf_atleta) if c.isdigit())
        cpf_5 = cpf_digitos[:5] if cpf_digitos else str(cpf_atleta)[:5]
        nome_limpo = str(nome_atleta).strip().replace(" ", "_")
        nome_arquivo = f"BRUMS_{nome_limpo}_{cpf_5}.pdf"
        
        # Garante caracteres válidos no nome de arquivo
        nome_arquivo = nome_arquivo.replace("/", "").replace("\\", "")
        caminho_pdf = os.path.join(diretorio_saida, nome_arquivo)
        
        # bbox_inches='tight' garante que elementos externos não sejam cortados
        plt.savefig(caminho_pdf, format='pdf', bbox_inches='tight')
        plt.close(fig)
        
        print(f" -> Relatório gerado: {nome_arquivo} com {len(grupo)} leitura(s).")
        
        if progress_callback:
            progress_callback(i + 1, total_atletas)
        
    print("\nTodos os relatórios PDF foram gerados com sucesso!")

# ==========================================
# Ponto de Execução do Script
# ==========================================
if __name__ == "__main__":
    ARQUIVO_CSV = './saida_bi/BI_BRUMS_Wide.csv'
    ARQUIVO_HEADER = 'assets/cabecalho.png'
    DIRETORIO_PDFS = './relatorios_pdf'
    
    criar_relatorios_brums_pdf(ARQUIVO_CSV, ARQUIVO_HEADER, DIRETORIO_PDFS)
