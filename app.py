import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Banca do Mané - Faça seu Pedido",
    page_icon="🍌",
    layout="centered"
)

# Título principal limpo e direto
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

# Inicializa o carrinho
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

# Seleção de Categoria em Abas Nativas
aba_selecionada = st.radio("Escolha o setor:", list(catalogo.keys()), horizontal=True)
st.markdown("---")

st.markdown(f"### 📋 Lista de {aba_selecionada}")
st.markdown("<small>Digite a quantidade desejada ao lado do item (ex: *1kg*, *3 unidades*, *1 maço*). Se deixar em branco, o item não entra no pedido.</small>", unsafe_allow_html=True)

# Exibe cada produto em uma linha limpa e legível (Nome na esquerda, Campo na direita)
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

# --- BARRA LATERAL (CARRINHO E ENVIO) ---
with st.sidebar:
    st.header("🛒 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("Nenhum item adicionado ainda. Digite as quantidades nas categorias ao lado.")
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
        st.subheader("📍 Dados para Entrega")
        nome = st.text_input("Seu Nome:")
        endereco = st.text_input("Endereço e Bairro:")
        telefone = st.text_input("Telefone (WhatsApp):")
        
        if st.button("📦 Fechar Pedido", type="primary"):
            if not nome or not endereco:
                st.error("Por favor, preencha seu Nome e Endereço!")
            else:
                msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
                msg += f"👤 *Cliente:* {nome}\n"
                msg += f"📍 *Endereço:* {endereco}\n"
                msg += f"📞 *Telefone:* {telefone}\n\n"
                msg += f"*ITENS DO PEDIDO:*\n"
                for p, q in st.session_state.carrinho.items():
                    msg += f"- {p}: {q}\n"
                
                st.session_state.pedido_gerado = msg
                st.success("Pedido gerado com sucesso!")

        if "pedido_gerado" in st.session_state and st.session_state.pedido_gerado:
            st.markdown("---")
            st.markdown("### 📲 Enviar no WhatsApp")
            st.text_area("Confira o texto:", value=st.session_state.pedido_gerado, height=140)
            
            import urllib.parse
            link_wpp = f"https://wa.me/5535998464384?text={urllib.parse.quote(st.session_state.pedido_gerado)}"
            st.markdown(
                f'<a href="{link_wpp}" target="_blank" style="background-color: #25D366; color: white; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: bold; display: block; text-align: center;">Enviar Pedido Agora 🚀</a>',
                unsafe_allow_html=True
            )
