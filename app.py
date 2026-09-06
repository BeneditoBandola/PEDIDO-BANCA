import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os

st.set_page_config(
    page_title="Banca do Mané - Pedido Oficial",
    page_icon="🍌",
    layout="centered"
)

# Título principal
st.markdown("<h1 style='text-align: center; color: #1e3d2f;'>🍌 Banca do Mané 🍅</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>", unsafe_allow_html=True)
st.markdown("---")

# Catálogo organizado por categorias
catalogo = {
    "🍎 Frutas": [
        "ABACATE", "ABACAXI HAVAÍ", "ABACAXI PÉROLA", "AMEIXA AMARELA", "AMEIXA VERM.", 
        "ATEMÓIA", "PITAYA", "BANANA NANICA", "BANANA PRATA", "CAQUI", "CARAMBOLA", 
        "FIGO", "GOIABA", "LARANJA BAIANA", "LARANJA LIMA", "LARANJA PERA", "LIMA DA PÉRSIA", 
        "LIMÃO CRAVO", "LIMÃO GALEGO", "LIMÃO SICILIANO", "LIMÃO TAITI", "MAÇÃ ARGENTINA", 
        "MAÇÃ NAC. FUJI", "MAÇÃ NAC. GALA", "MAÇÃ VERDE", "MAMÃO A. PAPAYA", "MAMÃO FORMOSA", 
        "MANGA", "MANGA COMUM", "MARACUJÁ", "MELANCIA", "MELÃO", "MEXERICA CRAVO", 
        "MEXERICA MURG.", "MEXERICA POKÃ", "MORANGO", "NECTARINA", "NONA", "PERA", 
        "PÊSSEGO AMAR.", "PÊSSEGO BCO.", "UVA", "UVA COMUM", "KIWI"
    ],
    "🥬 Verduras e Temperos": [
        "ACELGA", "AGRIÃO", "ALFACE AMERICANA", "ALFACE CRESPA", "ALFACE HIDROP.", 
        "ALFACE LISA", "ALFACE MIMOSA", "ALHO PORÓ", "ALMEIRÃO", "BRÓCOLIS", "CATALÔNIA", 
        "CHEIRO VERDE", "CHICÓRIA", "COENTRO", "COUVE", "ESPINAFRE", "HORTELÃ", 
        "RABANETE", "REPOLHO", "RÚCULA", "SALSA", "SALSÃO", "MANJERICÃO", "GENGIBRE", 
        "FARINHA DE MILHO", "FEIJÃO", "OVOS BRANCOS", "OVOS CAIPIRA", "OVOS CODORNA", 
        "OVOS VERMELHOS", "COCO", "PALMITO", "PORTO BELO", "PARIS", "SHITAKE", 
        "SHIMEGI", "TOFU", "BROTOS", "POLPA DE FRUTAS"
    ],
    "🥔 Legumes e Tubérculos": [
        "ALHO", "ABÓBORA MADURA", "ABOBRINHA CAIPIRA", "ABOBRINHA ITÁLIA", "BATATA DOCE", 
        "BATATA", "BATATA PIRULITO", "BERINGELA", "BETERRABA", "CABOTIÁ", "CEBOLA ROXA", 
        "CEBOLA", "CENOURA", "COUVE-FLOR", "CHUCHU", "ERVILHA DEBUIADA", "ERVILHA TORTA", 
        "INHAME", "JILÓ", "MANDIOCA", "MANDIQUINHA", "MILHO VERDE", "MORANGA", "MUGANGO", 
        "PIMENTA D. DE MOÇA", "PIMENTA GODÊ", "PIMENTÃO VERDE", "PIMENTÃO VERM.", "PEPINO", 
        "QUIABO", "TOMATÃO", "TOMATE CEREJA", "TOMATE MOLHO", "TOMATE SALADA", "VAGEM"
    ]
}

# Inicializa o carrinho e dados do cliente na sessão
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}
if "cliente_nome" not in st.session_state:
    st.session_state.cliente_nome = ""
if "cliente_end" not in st.session_state:
    st.session_state.cliente_end = ""
if "cliente_tel" not in st.session_state:
    st.session_state.cliente_tel = ""

# Seleção de Categoria em Abas Nativas
aba_selecionada = st.radio("Escolha o setor:", list(catalogo.keys()), horizontal=True)
st.markdown("---")

st.markdown(f"### 📋 Lista de {aba_selecionada}")
st.markdown("<small>Digite a quantidade desejada ao lado do item (ex: *1kg*, *3 unidades*, *1 maço*).</small>", unsafe_allow_html=True)

# Exibe cada produto em uma linha limpa e legível
produtos_da_categoria = catalogo[aba_selecionada]

for produto in produtos_da_categoria:
    col_nome, col_qtd = st.columns([2, 2])
    with col_nome:
        st.markdown(f"**{produto}**")
    with col_qtd:
        valor_atual = st.session_state.carrinho.get(produto, "")
        quantidade = st.text_input(
            label=f"Qtd {produto}",
            label_visibility="collapsed",
            value=valor_atual,
            placeholder="Ex: 1kg, 3 un, 1 maço",
            key=f"input_{produto}"
        )
        if quantidade.strip():
            st.session_state.carrinho[produto] = quantidade
        elif produto in st.session_state.carrinho and not quantidade.strip():
            del st.session_state.carrinho[produto]

# --- BARRA LATERAL: CADASTRO E GERADOR DE PDF ---
with st.sidebar:
    st.header("🛒 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("Nenhum item adicionado ainda.")
    else:
        st.success(f"Itens selecionados: **{len(st.session_state.carrinho)}**")
        
        for prod, qtd in list(st.session_state.carrinho.items()):
            c1, c2 = st.columns([3, 1])
            c1.text(f"• {prod}: {qtd}")
            if c2.button("❌", key=f"del_{prod}"):
                del st.session_state.carrinho[prod]
                st.rerun()
                
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.carrinho = {}
            st.rerun()
            
        st.divider()
        st.subheader("👤 Seus Dados (Cadastro)")
        st.markdown("<small>Preencha uma vez para salvar no seu navegador.</small>", unsafe_allow_html=True)
        
        nome = st.text_input("Seu Nome:", value=st.session_state.cliente_nome)
        endereco = st.text_input("Endereço e Bairro:", value=st.session_state.cliente_end)
        telefone = st.text_input("Telefone:", value=st.session_state.cliente_tel)
        
        # Salva na sessão do Streamlit
        st.session_state.cliente_nome = nome
        st.session_state.cliente_end = endereco
        st.session_state.cliente_tel = telefone
        
        st.divider()
        
        if st.button("📄 Gerar Pedido em PDF", type="primary"):
            if not nome or not endereco:
                st.error("Preencha Nome e Endereço para gerar o PDF!")
            else:
                # Criação do PDF formatado estilo talão da Banca
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "BANCA DO MANÉ - PEDIDO", 0, 1, "C")
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, "Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG", 0, 1, "C")
                pdf.cell(0, 6, "Fone: (35) 3721-0088 / (35) 9 9846-4384", 0, 1, "C")
                pdf.line(10, 28, 200, 28)
                pdf.ln(5)
                
                # Dados do Cliente
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 6, "DADOS DO CLIENTE:", 0, 1)
                pdf.set_font("Arial", "", 11)
                pdf.cell(0, 6, f"Nome: {nome}", 0, 1)
                pdf.cell(0, 6, f"Endereço: {endereco}", 0, 1)
                pdf.cell(0, 6, f"Telefone: {telefone}", 0, 1)
                pdf.ln(5)
                
                # Itens do Pedido
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 6, "ITENS SOLICITADOS:", 0, 1)
                pdf.set_font("Arial", "", 11)
                
                for p, q in st.session_state.carrinho.items():
                    pdf.cell(120, 6, f"- {p}", 0, 0)
                    pdf.cell(50, 6, f"Qtd: {q}", 0, 1)
                
                pdf.ln(10)
                pdf.set_font("Arial", "I", 9)
                pdf.cell(0, 6, "Pedido gerado digitalmente via App da Banca do Mané.", 0, 1, "C")
                
                # Salva o arquivo temporariamente
                tmp_dir = tempfile.gettempdir()
                pdf_path = os.path.join(tmp_dir, "pedido_banca_do_mane.pdf")
                pdf.output(pdf_path)
                
                st.success("PDF gerado com sucesso!")
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Baixar PDF do Pedido",
                        data=pdf_file,
                        file_name="pedido_banca_do_mane.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
