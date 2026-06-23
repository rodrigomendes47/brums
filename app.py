import streamlit as st
import pandas as pd
import os
import io
import zipfile
import tempfile
from datetime import datetime

from main import processar_dados_brums, calcular_escores
from generate_pdf import criar_relatorios_brums_pdf

# ==========================================
# CONSTANTES DE TEMA
# ==========================================
PRIMARY_COLOR = "#1a4331"  # Verde Escuro

# Configuração da Página
st.set_page_config(
    page_title="BRUMS - Avaliação Psicológica",
    page_icon="🧠",
    layout="centered"
)

# Injetar CSS customizado para forçar algumas cores e fontes
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #ffffff;
    }}
    .css-1d391kg, .css-1dp5vir {{
        background-color: {PRIMARY_COLOR};
    }}
    h1, h2, h3 {{
        color: {PRIMARY_COLOR} !important;
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #2c6e49;
        color: white;
        border-color: #2c6e49;
    }}
    .stDownloadButton>button {{
        background-color: #2c6e49;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }}
    .stDownloadButton>button:hover {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ITENS DO BRUMS
# ==========================================
BRUMS_ITEMS = [
    "ansioso", "preocupado", "tenso", "apavorado",
    "deprimido", "desanimado", "triste", "infeliz",
    "irritado", "zangado", "com_raiva", "mal_humorado",
    "animado", "com_disposição", "com_energia", "alerta",
    "esgotado", "exausto", "sonolento", "cansado",
    "confuso", "inseguro", "desorientado", "indeciso"
]

# ==========================================
# CABEÇALHO
# ==========================================
# Verificar se logo existe
logo_path = os.path.join("assets", "cmepp-logo.png")
if os.path.exists(logo_path):
    # Exibir logo centralizada (Streamlit usa columns)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo_path, use_container_width=True)

st.markdown("<h1 style='text-align: center;'>Sistema de Análise BRUMS</h1>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# MODAL DE PROCESSAMENTO
# ==========================================
@st.dialog("Resultados do Processamento")
def processar_lote_modal(upload_file, data_inicio, data_fim, filtro_cpf):
    # Inicializar as variáveis de estado se não existirem
    if "lote_zip_buffer" not in st.session_state:
        st.session_state.lote_zip_buffer = None
    if "lote_num_relatorios" not in st.session_state:
        st.session_state.lote_num_relatorios = None

    # Se ainda não foi processado, executa o processamento
    if st.session_state.lote_zip_buffer is None:
        with st.spinner("Preparando dados..."):
            try:
                # Usar um diretório temporário para gerar os arquivos
                with tempfile.TemporaryDirectory() as tmpdirname:
                    saida_bi_dir = os.path.join(tmpdirname, "saida_bi")
                    os.makedirs(saida_bi_dir, exist_ok=True)
                    
                    # Processar os dados usando main.py (passando o arquivo do upload)
                    df_entrada = pd.read_excel(upload_file, sheet_name='entrada')
                    
                    # Filtrar por CPF se especificado
                    if filtro_cpf.strip():
                        if 'CPF' in df_entrada.columns:
                            cpf_filtro_digitos = "".join(c for c in filtro_cpf if c.isdigit())
                            if cpf_filtro_digitos:
                                df_entrada = df_entrada[df_entrada['CPF'].astype(str).str.replace(r'\D', '', regex=True) == cpf_filtro_digitos].copy()
                            else:
                                df_entrada = df_entrada[df_entrada['CPF'].astype(str).str.contains(filtro_cpf.strip(), case=False, na=False)].copy()

                    if 'data' in df_entrada.columns:
                        df_entrada['data'] = pd.to_datetime(df_entrada['data'], errors='coerce')
                        if data_inicio is not None:
                            df_entrada = df_entrada[df_entrada['data'] >= data_inicio].copy()
                        if data_fim is not None:
                            df_entrada = df_entrada[df_entrada['data'] <= data_fim].copy()
                    
                    # Reset file pointer to read another sheet
                    upload_file.seek(0)
                    df_percentil = pd.read_excel(upload_file, sheet_name='Percentil')
                    
                    df_wide, df_long = calcular_escores(df_entrada, df_percentil, saida_bi_dir)
                    
                    if df_wide is not None and not df_wide.empty:
                        pdf_dir = os.path.join(tmpdirname, "relatorios_pdf")
                        os.makedirs(pdf_dir, exist_ok=True)
                        
                        csv_path = os.path.join(saida_bi_dir, 'BI_BRUMS_Wide.csv')
                        header_path = os.path.join("assets", "cabecalho.png")
                        
                        # Gerar PDFs
                        progress_text = "Gerando relatórios PDF..."
                        progress_bar = st.progress(0, text=progress_text)
                        
                        def update_progress(atual, total):
                            percentual = int((atual / total) * 100)
                            progress_bar.progress(atual / total, text=f"{progress_text} {atual}/{total} ({percentual}%)")

                        criar_relatorios_brums_pdf(csv_path, header_path, pdf_dir, progress_callback=update_progress)
                        
                        # Criar ZIP em memória
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            # Adicionar CSVs
                            for f in os.listdir(saida_bi_dir):
                                f_path = os.path.join(saida_bi_dir, f)
                                zip_file.write(f_path, arcname=f"saida_bi/{f}")
                            
                            # Adicionar PDFs
                            for f in os.listdir(pdf_dir):
                                f_path = os.path.join(pdf_dir, f)
                                zip_file.write(f_path, arcname=f"relatorios_pdf/{f}")
                        
                        zip_buffer.seek(0)
                        
                        st.session_state.lote_zip_buffer = zip_buffer
                        st.session_state.lote_num_relatorios = len(os.listdir(pdf_dir))
                    else:
                        st.warning("Nenhum dado encontrado para processar ou erro no cálculo.")
                        
            except Exception as e:
                st.error(f"Erro Crítico: {str(e)}")

    # Se já processou, mostra o botão de download e fechar
    if st.session_state.lote_zip_buffer is not None:
        st.success(f"Processamento concluído! {st.session_state.lote_num_relatorios} relatórios gerados.")
        
        col_down, col_close = st.columns(2)
        # with col_down:
        if st.download_button(
            label="⬇️ Baixar BRUMS_Resultados.zip",
            data=st.session_state.lote_zip_buffer,
            file_name="BRUMS_Resultados.zip",
            mime="application/zip",
            key="download_lote_btn",
            use_container_width=True
        ):
                # Limpa o estado e reinicia (fecha o modal)
                st.session_state.lote_processando = False
                st.session_state.lote_zip_buffer = None
                st.session_state.lote_num_relatorios = None
                st.rerun()
        
        # with col_close:
        #     if st.button("Fechar", key="close_lote_btn", use_container_width=True):
        #         # Limpa o estado e reinicia (fecha o modal)
        #         st.session_state.lote_processando = False
        #         st.session_state.lote_zip_buffer = None
        #         st.session_state.lote_num_relatorios = None
        #         st.rerun()

# ==========================================
# ABAS
# ==========================================
tab_lote, tab_manual = st.tabs(["Processamento em Lote", "Entrada Manual"])

# ==========================================
# ABA: PROCESSAMENTO EM LOTE
# ==========================================
with tab_lote:
    st.subheader("Processamento em Lote")
    st.write("Faça o upload do arquivo Excel contendo as abas 'entrada' e 'Percentil'. Ao processar, você receberá um arquivo `.zip` com os relatórios e planilhas BI.")
    upload_lote = st.file_uploader("Arquivo Excel (dados_brums.xlsx)", type=["xlsx", "xls"], key="lote_upload")
    # Colunas para filtros opcionais
    col_filtro_data_ini, col_filtro_data_fim, col_filtro_cpf = st.columns(3)
    
    filtro_data_ini = col_filtro_data_ini.text_input("Data de Início (opcional):", key="lote_data_ini", placeholder="DD/MM/YYYY")
    filtro_data_fim = col_filtro_data_fim.text_input("Data Máxima (opcional):", key="lote_data_fim", placeholder="DD/MM/YYYY")
    filtro_cpf = col_filtro_cpf.text_input("CPF do Atleta (opcional - somente numeros):", key="lote_cpf", placeholder="Apenas números")
    
    # Calcular data_inicio e data_fim fora do botão para estar disponível nas reruns do modal
    data_inicio = None
    if filtro_data_ini.strip():
        try:
            data_inicio = pd.to_datetime(filtro_data_ini.strip(), format='%d/%m/%Y')
        except ValueError:
            st.error("Formato de Data de Início inválido! Use dd/mm/aaaa.")
            st.stop()
            
    data_fim = None
    if filtro_data_fim.strip():
        try:
            data_fim = pd.to_datetime(filtro_data_fim.strip(), format='%d/%m/%Y')
        except ValueError:
            st.error("Formato de Data Máxima inválido! Use dd/mm/aaaa.")
            st.stop()
            
    if st.button("Processar Arquivo e Gerar ZIP", key="btn_lote"):
        if not upload_lote:
            st.error("Por favor, selecione o arquivo Excel de entrada.")
        else:
            # Ativa o modal e reseta o buffer de cache
            st.session_state.lote_processando = True
            st.session_state.lote_zip_buffer = None
            st.session_state.lote_num_relatorios = None
            st.rerun()
            
    # Chama o modal se estiver ativo no estado
    if st.session_state.get("lote_processando", False):
        processar_lote_modal(upload_lote, data_inicio, data_fim, filtro_cpf)
    st.write("**NOTA:** Nenhum dado será armazenado ou compartilhado. Todo o processamento é feito em memória e os dados são excluídos IMEDIATAMENTE após o processamento.")

# ==========================================
# ABA: ENTRADA MANUAL
# ==========================================
with tab_manual:
    st.subheader("Entrada Manual")
    
    with st.container():
        st.write("### Dados do Atleta")
        col_id, col_nome, col_cpf, col_data = st.columns(4)
        man_id = col_id.text_input("ID", key="man_id")
        man_nome = col_nome.text_input("Nome", key="man_nome")
        man_cpf = col_cpf.text_input("CPF", key="man_cpf")
        man_data = col_data.text_input("Data (dd/mm/aaaa)", value=datetime.now().strftime("%d/%m/%Y"), key="man_data")
        
    st.write("### Questionário BRUMS (0 a 4)")
    
    # Criar grid 6x4 para os 24 itens
    valores_manuais = {}
    
    # Agrupar itens de 4 em 4
    for i in range(0, 24, 4):
        cols = st.columns(4)
        for j in range(4):
            item = BRUMS_ITEMS[i+j]
            label_formatada = item.capitalize().replace("_", " ")
            valores_manuais[item] = cols[j].selectbox(label_formatada, options=[0, 1, 2, 3, 4], index=0, key=f"sel_{item}")
            
    st.markdown("---")
    st.write("### Arquivo Base")
    upload_perc = st.file_uploader("Selecione o arquivo Excel base contendo a aba 'Percentil' (ex: dados_brums.xlsx):", type=["xlsx", "xls"], key="man_upload")
    
    if st.button("Processar e Gerar PDF", key="btn_manual"):
        if not upload_perc:
            st.error("Por favor, selecione o arquivo base de percentil.")
        else:
            with st.spinner("Calculando T-Escores e gerando PDF..."):
                try:
                    # Validar data
                    try:
                        data_val = pd.to_datetime(man_data, format="%d/%m/%Y")
                    except ValueError:
                        st.error("Data inválida. Use dd/mm/aaaa.")
                        st.stop()
                    
                    # Montar DataFrame de 1 linha
                    dict_entrada = {
                        'ID': [man_id],
                        'Nome': [man_nome],
                        'CPF': [man_cpf],
                        'data': [data_val]
                    }
                    for item in BRUMS_ITEMS:
                        dict_entrada[item] = [valores_manuais[item]]
                        
                    df_entrada = pd.DataFrame(dict_entrada)
                    
                    # Carregar Percentil
                    df_percentil = pd.read_excel(upload_perc, sheet_name='Percentil')
                    
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        saida_bi_dir = os.path.join(tmpdirname, "saida_bi_manual")
                        os.makedirs(saida_bi_dir, exist_ok=True)
                        
                        df_wide, _ = calcular_escores(df_entrada, df_percentil, saida_bi_dir)
                        
                        if df_wide is not None and not df_wide.empty:
                            pdf_dir = os.path.join(tmpdirname, "relatorios_pdf_manual")
                            os.makedirs(pdf_dir, exist_ok=True)
                            
                            csv_path = os.path.join(saida_bi_dir, 'BI_BRUMS_Wide.csv')
                            header_path = os.path.join("assets", "cabecalho.png")
                            
                            criar_relatorios_brums_pdf(csv_path, header_path, pdf_dir)
                            
                            # Recuperar o PDF gerado
                            arquivos_pdf = os.listdir(pdf_dir)
                            if arquivos_pdf:
                                nome_pdf = arquivos_pdf[0]
                                caminho_pdf = os.path.join(pdf_dir, nome_pdf)
                                
                                with open(caminho_pdf, "rb") as f:
                                    pdf_bytes = f.read()
                                
                                st.success(f"Relatório gerado com sucesso!")
                                st.download_button(
                                    label=f"⬇️ Baixar {nome_pdf}",
                                    data=pdf_bytes,
                                    file_name=nome_pdf,
                                    mime="application/pdf"
                                )
                                st.rerun()
                            else:
                                st.error("Erro desconhecido ao gerar o arquivo PDF.")
                        else:
                            st.error("Falha no cálculo dos T-Escores.")
                            
                except Exception as e:
                    st.error(f"Erro Crítico: {str(e)}")
