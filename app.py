import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Banca do Mané - Faça seu Pedido",
    page_icon="🍎",
    layout="wide"
)

# Estilização para fundo claro, fontes maiores e boa legibilidade
st.markdown("""
    <style>
    /* Força o fundo geral claro e limpo */
    .stApp {
        background-color: #fcfcfc;
        color: #2b2b2b;
    }
    
    /* Cabeçalhos maiores e destacados */
    .main-header {
        font-size: 2.5rem;
        color: #1e3d2f;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .sub-header {
        text-align: center;
        color: #555555;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Aumenta o tamanho dos rótulos (nomes dos produtos) e caixas de texto para facilitar a leitura */
    .stTextInput label {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
    }
    
    /* Melhora o destaque dos inputs */
    input {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🍌 Banca do Mané 🍅</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG 📦 Entrega em Domicílio</p>', unsafe_allow_html=True)

# Dicionário estruturado com todos os produtos do talão
catalogo = {
    "🍎 Frutas Frescas": [
        "ABACATE", "ABACAXI HAVAÍ", "ABACAXI PÉROLA", "AMEIXA AMARELA", "AMEIXA VERM.", 
        "ATEMÓIA", "PITAYA", "BANANA NANICA", "BANANA PRATA", "CAQUI", "CARAMBOLA", 
        "FIGO", "GOIABA", "LARANJA BAIANA", "LARANJA LIMA", "LARANJA PERA", "LIMA DA PÉRSIA", 
        "LIMÃO CRAVO", "LIMÃO GALEGO", "LIMÃO SICILIANO", "LIMÃO TAITI", "MAÇÃ ARGENTINA", 
        "MAÇÃ NAC. FUJI", "MAÇÃ NAC. GALA", "MAÇÃ VERDE", "MAMÃO A. PAPAYA", "MAMÃO FORMOSA", 
        "MANGA", "MANGA COMUM", "MARACUJÁ", "MELANCIA", "MELÃO", "MEXERICA CRAVO", 
        "MEXERICA MURG.", "MEXERICA POKÃ", "MORANGO", "NECTARINA", "NONA", "PERA", 
        "PÊSSEGO AMAR.", "PÊSSEGO BCO.", "UVA", "UVA COMUM", "KIWI"
    ],
    "🥬 Verduras, Temperos e Outros": [
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

# Inicializar estado da sessão
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

if "pedido_gerado" not in st.session_state:
    st.session_state.pedido_gerado = ""

# Layout principal em abas
aba_pedido, aba_busca = st.tabs(["🛒 Fazer Pedido por Categoria", "🔍 Busca Rápida de Produtos"])

with aba_busca:
    st.subheader("🔍 Busque o produto desejado:")
    termo_busca = st.text_input("Digite o nome da fruta, legume ou verdura:", "").upper()
    
    if termo_busca:
        encontrados = []
        for cat, itens in catalogo.items():
            for item in itens:
                if termo_busca in item:
                    encontrados.append((item, cat))
        
        if encontrados:
            st.success(f"Encontramos {len(encontrados)} item(ns):")
            for prod, categoria in encontrados:
                cols = st.columns([3, 2])
                with cols[0]:
                    st.write(f"**{prod}** *({categoria})*")
                with cols[1]:
                    qtd = st.text_input(f"Quantidade para {prod}", key=f"busca_{prod}", placeholder="ex: 1kg, 2 bandeijas")
                    if qtd:
                        st.session_state.carrinho[prod] = qtd
        else:
            st.warning("Nenhum produto encontrado com esse nome.")

with aba_pedido:
    st.markdown("### Selecione a categoria e digite a quantidade desejada:")
    categoria_selecionada = st.radio("Escolha o setor:", list(catalogo.keys()), horizontal=True)
    
    st.divider()
    
    produtos_da_categoria = catalogo[categoria_selecionada]
    cols_por_linha = 2
    linhas = [produtos_da_categoria[i:i + cols_por_linha] for i in range(0, len(produtos_da_categoria), cols_por_linha)]
    
    for linha in linhas:
        cols = st.columns(cols_por_linha)
        for idx, produto in enumerate(linha):
            with cols[idx]:
                valor_atual = st.session_state.carrinho.get(produto, "")
                quantidade = st.text_input(
                    label=f"📦 {produto}",
                    value=valor_atual,
                    placeholder="Ex: 1kg, 6 un, 1 maço",
                    key=f"cat_{produto}"
                )
                if quantidade.strip():
                    st.session_state.carrinho[produto] = quantidade
                elif produto in st.session_state.carrinho and not quantidade.strip():
                    del st.session_state.carrinho[produto]

# --- BARRA LATERAL: CARRINHO E FINALIZAÇÃO ---
with st.sidebar:
    st.header("📋 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio. Selecione os produtos nas abas ao lado.")
    else:
        st.write(f"Total de itens escolhidos: **{len(st.session_state.carrinho)}**")
        
        for prod, qtd in list(st.session_state.carrinho.items()):
            c1, c2 = st.columns([3, 1])
            c1.text(f"• {prod}: {qtd}")
            if c2.button("❌", key=f"del_{prod}"):
                del st.session_state.carrinho[prod]
                st.rerun()
                
        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = {}
            st.session_state.pedido_gerado = ""
            st.rerun()
            
        st.divider()
        st.subheader("📍 Dados para Entrega")
        nome_cliente = st.text_input("Seu Nome:")
        endereco_cliente = st.text_input("Endereço / Bairro:")
        telefone_cliente = st.text_input("Telefone de Contato:")
        
        if st.button("📦 Fechar Pedido", type="primary"):
            if not nome_cliente or not endereco_cliente:
                st.error("Por favor, preencha seu Nome e Endereço!")
            else:
                msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
                msg += f"👤 *Cliente:* {nome_cliente}\n"
                msg += f"📍 *Endereço:* {endereco_cliente}\n"
                msg += f"📞 *Telefone:* {telefone_cliente}\n\n"
                msg += f"*ITENS SOLICITADOS:*\n"
                for p, q in st.session_state.carrinho.items():
                    msg += f"- {p}: {q}\n"
                
                st.session_state.pedido_gerado = msg
                st.success("Pedido gerado com sucesso!")

        if st.session_state.pedido_gerado:
            st.markdown("---")
            st.markdown("### 📲 Enviar para a Banca")
            st.text_area("Confira o texto abaixo:", value=st.session_state.pedido_gerado, height=150)
            
            import urllib.parse
            msg_encoded = urllib.parse.quote(st.session_state.pedido_gerado)
            # Número da Banca do Mané: (35) 9 9846-4384
            whatsapp_url = f"https://wa.me/5535998464384?text={msg_encoded}"
            
            st.markdown(
                f'<div style="text-align: center; margin-top: 10px;">'
                f'<a href="{whatsapp_url}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; display: block; font-size: 1.1rem;">Abrir WhatsApp com o Pedido 🚀</a>'
                f'</div>',
                unsafe_allow_html=True
            )
