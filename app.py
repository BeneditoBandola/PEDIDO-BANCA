import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Banca do Mané - Faça seu Pedido",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Força o tema claro via configuração do Streamlit e CSS limpo
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
        color: #222222;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #1e3d2f !important;
    }
    /* Estilo para os cards de produtos */
    .product-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center;">🍌 Banca do Mané 🍅</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>', unsafe_allow_html=True)

# Catálogo organizado
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

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

if "pedido_gerado" not in st.session_state:
    st.session_state.pedido_gerado = ""

# Abas principais
aba_pedido, aba_busca = st.tabs(["🛒 Escolher por Categoria", "🔍 Busca Rápida"])

with aba_busca:
    st.subheader("Digite o que procura:")
    termo = st.text_input("Ex: Tomate, Banana, Alface...", "").upper()
    if termo:
        encontrados = [ (item, cat) for cat, itens in catalogo.items() for item in itens if termo in item ]
        if encontrados:
            for prod, cat in encontrados:
                cols = st.columns([2, 2, 1])
                cols[0].markdown(f"**{prod}** <br><small>{cat}</small>", unsafe_allow_html=True)
                qtd = cols[1].selectbox("Quantidade:", ["Selecione...", "1 kg", "500g", "2 kg", "1 unidade", "1 maço", "1 bandeja"], key=f"b_{prod}")
                if cols[2].button("Adicionar", key=f"add_{prod}") and qtd != "Selecione...":
                    st.session_state.carrinho[prod] = qtd
                    st.success(f"Adicionado!")
        else:
            st.warning("Produto não encontrado.")

with aba_pedido:
    cat_escolhida = st.radio("Selecione o setor:", list(catalogo.keys()), horizontal=True)
    st.divider()
    
    produtos = catalogo[cat_escolhida]
    
    # Exibe em colunas organizadas com seletor limpo para cada item
    for i in range(0, len(produtos), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(produtos):
                p1 = produtos[i]
                c_a, c_b = st.columns([2, 2])
                c_a.markdown(f"**{p1}**")
                val1 = c_b.selectbox("Qtd:", ["-", "1 kg", "500g", "2 kg", "1 unidade", "1 maço", "1 bandeja", "Outro"], key=f"sel_{p1}")
                if val1 != "-":
                    if val1 == "Outro":
                        custom = st.text_input(f"Qtd exata para {p1}", key=f"custom_{p1}")
                        if custom: st.session_state.carrinho[p1] = custom
                    else:
                        st.session_state.carrinho[p1] = val1
                elif p1 in st.session_state.carrinho:
                    del st.session_state.carrinho[p1]

        with col2:
            if i + 1 < len(produtos):
                p2 = produtos[i+1]
                c_a, c_b = st.columns([2, 2])
                c_a.markdown(f"**{p2}**")
                val2 = c_b.selectbox("Qtd:", ["-", "1 kg", "500g", "2 kg", "1 unidade", "1 maço", "1 bandeja", "Outro"], key=f"sel_{p2}")
                if val2 != "-":
                    if val2 == "Outro":
                        custom2 = st.text_input(f"Qtd exata para {p2}", key=f"custom_{p2}")
                        if custom2: st.session_state.carrinho[p2] = custom2
                    else:
                        st.session_state.carrinho[p2] = val2
                elif p2 in st.session_state.carrinho:
                    del st.session_state.carrinho[p2]

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("Nenhum item selecionado ainda.")
    else:
        st.write(f"Itens selecionados: **{len(st.session_state.carrinho)}**")
        for prod, qtd in list(st.session_state.carrinho.items()):
            c1, c2 = st.columns([3, 1])
            c1.text(f"• {prod}: {qtd}")
            if c2.button("❌", key=f"del_{prod}"):
                del st.session_state.carrinho[prod]
                st.rerun()
                
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.carrinho = {}
            st.session_state.pedido_gerado = ""
            st.rerun()
            
        st.divider()
        st.subheader("📍 Dados de Entrega")
        nome = st.text_input("Seu Nome:")
        endereco = st.text_input("Endereço e Bairro:")
        telefone = st.text_input("Telefone:")
        
        if st.button("📦 Fechar Pedido", type="primary"):
            if not nome or not endereco:
                st.error("Preencha Nome e Endereço!")
            else:
                msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
                msg += f"👤 *Cliente:* {nome}\n"
                msg += f"📍 *Endereço:* {endereco}\n"
                msg += f"📞 *Telefone:* {telefone}\n\n"
                msg += f"*ITENS:*\n"
                for p, q in st.session_state.carrinho.items():
                    msg += f"- {p}: {q}\n"
                st.session_state.pedido_gerado = msg
                st.success("Pronto! Veja abaixo para enviar.")

        if st.session_state.pedido_gerado:
            st.markdown("---")
            st.text_area("Texto do Pedido:", value=st.session_state.pedido_gerado, height=130)
            
            import urllib.parse
            link_wpp = f"https://wa.me/5535998464384?text={urllib.parse.quote(st.session_state.pedido_gerado)}"
            st.markdown(
                f'<a href="{link_wpp}" target="_blank" style="background-color: #25D366; color: white; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: bold; display: block; text-align: center;">Enviar para o WhatsApp 🚀</a>',
                unsafe_allow_html=True
            )
