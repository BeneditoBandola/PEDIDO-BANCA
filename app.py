import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Banca do Mané - Faça seu Pedido",
    page_icon="🍎",
    layout="wide"
)

# Estilo visual limpo e amigável
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #2c3e50;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🍌 Banca do Mané 🍅</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>', unsafe_allow_html=True)

# Dicionário estruturado com todos os produtos do talão
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

# Inicializar carrinho na sessão do Streamlit
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

# Layout principal em abas para não ficar maçante
aba_pedido, aba_busca = st.tabs(["🛒 Fazer Pedido por Categoria", "🔍 Busca Rápida de Produtos"])

with aba_busca:
    st.subheader("Busque o produto desejado:")
    termo_busca = st.text_input("Digite o nome da fruta, legume ou verdura (ex: tomate, banana...):", "").upper()
    
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
                    qtd = st.text_input(f"Qtd/Peso p/ {prod}", key=f"busca_{prod}", placeholder="ex: 1kg, 2 bandeijas")
                    if qtd:
                        st.session_state.carrinho[prod] = qtd
        else:
            st.warning("Nenhum produto encontrado com esse nome.")

with aba_pedido:
    st.markdown("Selecione a categoria abaixo para adicionar os itens:")
    categoria_selecionada = st.radio("Categoria:", list(catalogo.keys()), horizontal=True)
    
    st.divider()
    
    # Exibição organizada em colunas para facilitar o clique/preenchimento rápido
    produtos_da_categoria = catalogo[categoria_selecionada]
    
    # Criando grid dinâmico
    cols_por_linha = 2
    linhas = [produtos_da_categoria[i:i + cols_por_linha] for i in range(0, len(produtos_da_categoria), cols_por_linha)]
    
    for linha in linhas:
        cols = st.columns(cols_por_linha)
        for idx, produto in enumerate(linha):
            with cols[idx]:
                valor_atual = st.session_state.carrinho.get(produto, "")
                quantidade = st.text_input(
                    label=produto,
                    value=valor_atual,
                    placeholder="Ex: 1kg, 6 unidades, 1 maço",
                    key=f"cat_{produto}"
                )
                if quantidade.strip():
                    st.session_state.carrinho[produto] = quantidade
                elif produto in st.session_state.carrinho and not quantidade.strip():
                    del st.session_state.carrinho[produto]

# --- BARRA LATERAL: RESUMO DO PEDIDO E FINALIZAÇÃO ---
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
            st.rerun()
            
        st.divider()
        st.subheader("Dados para Entrega")
        nome_cliente = st.text_input("Seu Nome:")
        endereco_cliente = st.text_input("Endereço / Bairro:")
        telefone_cliente = st.text_input("Telefone de Contato:")
        
        if st.button("📤 Enviar Pedido via WhatsApp", type="primary"):
            if not nome_cliente or not endereco_cliente:
                st.error("Por favor, preencha seu Nome e Endereço!")
            else:
                # Monta a mensagem formatada para o WhatsApp da Banca
                msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
                msg += f"👤 *Cliente:* {nome_cliente}\n"
                msg += f"📍 *Endereço:* {endereco_cliente}\n"
                msg += f"📞 *Telefone:* {telefone_cliente}\n\n"
                msg += f"*ITENS SOLICITADOS:*\n"
                for p, q in st.session_state.carrinho.items():
                    msg += f"- {p}: {q}\n"
                
                import urllib.parse
                msg_encoded = urllib.parse.quote(msg)
                # Número da Banca do Mané extraído do talão: (35) 9 9846-4384
                whatsapp_url = f"https://wa.me/5535998464384?text={msg_encoded}"
                
                st.markdown(f'<meta http-equiv="refresh" content="0;url={whatsapp_url}">', unsafe_allow_html=True)
                st.success("Pedido pronto! Redirecionando para o WhatsApp...")
                st.markdown(f"[Clique aqui se não abrir automaticamente]({whatsapp_url})", unsafe_allow_html=True)
