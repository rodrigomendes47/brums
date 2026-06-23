# Sistema de Análise BRUMS (Brunel Mood Scale)

Este é um sistema desenvolvido para automatizar a avaliação psicológica baseada na escala **BRUMS (Brunel Mood Scale)**. A aplicação processa dados coletados de questionários de atletas, calcula os escores brutos, faz o mapeamento para T-Escores utilizando tabelas normativas, gera arquivos formatados para ferramentas de BI (Business Intelligence) e plota relatórios individuais em PDF contendo gráficos do perfil de humor ao longo do tempo.

---

## 🧠 O que é o BRUMS e Como Funciona?

O **BRUMS (Brunel Mood Scale)** é um instrumento de avaliação psicológica adaptado para medir estados de humor de forma rápida em populações adultas e atletas. Ele avalia 24 indicadores de humor subjetivos divididos em **6 fatores principais**:

1. **Tensão** (Fator de Humor Negativo): Mede sentimentos de ansiedade, preocupação e nervosismo.
   * *Itens correspondentes:* Ansioso, preocupado, tenso e apavorado.
2. **Depressão** (Fator de Humor Negativo): Mede sentimentos de tristeza, desânimo e autodepreciação.
   * *Itens correspondentes:* Deprimido, desanimado, triste e infeliz.
3. **Raiva** (Fator de Humor Negativo): Mede sentimentos de hostilidade, irritação e fúria.
   * *Itens correspondentes:* Irritado, zangado, com raiva e mal-humorado.
4. **Vigor** (Fator de Humor **Positivo**): Mede sentimentos de vitalidade, energia ativa e alerta mental.
   * *Itens correspondentes:* Animado, com disposição, com energia e alerta.
5. **Fadiga** (Fator de Humor Negativo): Mede esgotamento físico, cansaço e falta de energia.
   * *Itens correspondentes:* Esgotado, exausto, sonolento e cansado.
6. **Confusão** (Fator de Humor Negativo): Mede sentimentos de incerteza, indecisão e instabilidade emocional.
   * *Itens correspondentes:* Confuso, inseguro, desorientado e indeciso.

### Regras de Cálculo
* Cada um dos 24 itens é avaliado em uma escala Likert de **0 a 4** (0 = Nada; 4 = Extremamente).
* O **Escore Bruto (EB)** para cada um dos 6 fatores é a soma direta dos 4 itens associados a ele (variando de 0 a 16).
* O **T-Escore** é obtido mapeando o Escore Bruto contra uma tabela de normas populacionais predefinida (aba "Percentil").
* Um perfil considerado ideal no esporte é o **"Perfil de Iceberg"**, onde o Vigor (positivo) está acima do T-Escore 50 e os fatores negativos (Tensão, Depressão, Raiva, Fadiga, Confusão) estão bem abaixo de 50.

---

## 🖥️ Descrição da Aplicação Streamlit

A aplicação possui uma interface web amigável desenvolvida em **Streamlit** organizada em duas modalidades de uso:

### 1. Processamento em Lote (Excel)
* **Como funciona:** O usuário faz o upload de uma planilha Excel (contendo as abas `entrada` para os dados dos questionários e `Percentil` para as tabelas normativas de T-Escore).
* **Filtros:** É possível aplicar um filtro de data opcional para processar apenas registros a partir de um dia específico.
* **Modal e Barra de Progresso:** Ao clicar em processar, um modal (`st.dialog`) se abre exibindo um _spinner_ de carregamento e uma barra de progresso em tempo real que calcula o percentual de relatórios PDF gerados por atleta.
* **Download:** Ao finalizar, o modal oferece o download de um arquivo compactado `.zip` contendo os relatórios em formato PDF e duas planilhas formatadas (`BI_BRUMS_Wide.csv` e `BI_BRUMS_Long.csv`) prontas para consumo em dashboards do Power BI, Tableau ou Looker Studio.

### 2. Entrada Manual
* **Como funciona:** Permite que o psicólogo ou avaliador preencha os dados do atleta (ID, Nome, CPF, Data) e as respostas de 0 a 4 para cada um dos 24 sentimentos diretamente na tela.
* **Download:** Gera o PDF de análise individual na hora para download imediato.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**: Linguagem de programação principal.
* **Streamlit**: Framework para construção de interfaces web rápidas e interativas.
* **Pandas**: Biblioteca para manipulação, limpeza e análise de dados tabulares.
* **Matplotlib**: Biblioteca para geração dos gráficos de linha e formatação estética dos PDFs.
* **Openpyxl**: Engine de leitura e processamento de arquivos do Microsoft Excel (.xlsx).

---

## 🚀 Como Executar Localmente

### Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado na sua máquina.

### Passo 1: Clonar ou Baixar o Repositório
Copie os arquivos do projeto para uma pasta em seu computador.

### Passo 2: Instalar as Dependências
Abra o seu terminal/prompt de comando na pasta do projeto e execute:
```bash
pip install -r requirements.txt
```
*Caso o arquivo `requirements.txt` esteja em branco, você pode instalar as dependências manualmente rodando:*
```bash
pip install streamlit pandas matplotlib openpyxl
```

### Passo 3: Executar a Aplicação Streamlit
No terminal, execute o seguinte comando:
```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador padrão no endereço `http://localhost:8501`.

---

## 📁 Estrutura do Projeto

* `app.py`: O frontend do Streamlit, contendo o fluxo de telas, o modal de processamento e os componentes interativos.
* `main.py`: O motor lógico que realiza a consolidação das notas e calcula os T-Escores.
* `generate_pdf.py`: Script responsável por gerar o layout estético e salvar o gráfico como um relatório em formato PDF.
* `dados_brums_exemplo.xlsx`: Exemplo da estrutura necessária da planilha Excel com os dados de entrada e tabelas normativas.
* `assets/`: Pasta com imagens de cabeçalho (`cabecalho.png`) e logos institucionais.
