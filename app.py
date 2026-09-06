import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="Banca do Mané - Fazer Pedido",
    page_icon="🍌",
    layout="centered"
)

# Título principal
st.markdown("<h1 style='text-align: center; color: #1e3d2f;'>🍌 Banca do Mané 🍅</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>", unsafe_allow_html=True)
st.markdown("---")

# Opções padronizadas e limpas com KG e gr
op_maturacao = ["Padrão", "Mais verde", "Mais maduro"]
op_peso_kg = ["1 KG", "Meio KG (500 gr)", "Unidade"]
op_peso_kg_simples = ["1 KG", "Meio KG (500 gr)"]
op_gramas_limpas = ["100 gr", "200 gr", "300 gr", "400 gr", "500 gr", "600 gr", "700 gr", "800 gr", "900 gr", "1 KG"]

# Catálogo reestruturado especificando o tipo de unidade base para cada item
catalogo = {
    "🍎 Frutas": [
        ("🥑 ABACATE", op_peso_kg, True),
        ("🥑 AVOCADO", op_peso_kg, True),
        ("🍍 ABACAXI PÉROLA", ["Unidade"], True),
        ("🍑 AMEIXA AMARELA", op_peso_kg, True),
        ("🍑 AMEIXA VERMELHA", op_peso_kg, True),
        ("🍈 ATEMÓIA", op_peso_kg, True),
        ("🌵 PITAYA", op_peso_kg, True),
        ("🍌 BANANA NANICA", ["Unidade", "Penca"], False),
        ("🍌 BANANA PRATA", ["Unidade", "Penca"], False),
        ("🥭 CAQUI", ["Bandeja", "Unidade"], True),
        ("⭐ CARAMBOLA", ["Bandeja"], False),
        ("FIGO", ["Bandeja"], False), 
        ("🍐 GOIABA", op_peso_kg, True),
        ("🍊 LARANJA BAIANA", op_peso_kg, False),
        ("🍊 LARANJA LIMA", op_peso_kg, False),
        ("🍊 LARANJA PERA", op_peso_kg, False),
        ("🍋 LIMA DA PÉRSIA", op_peso_kg, False),
        ("🍋 LIMÃO CRAVO", op_peso_kg, False),
        ("🍋 LIMÃO SICILIANO", op_peso_kg, False),
        ("🍋 LIMÃO TAITI", op_peso_kg, False),
        ("🍏 MAÇÃ ARGENTINA", op_peso_kg, False),
        ("🍎 MAÇÃ NAC. FUJI", op_peso_kg, False),
        ("🍎 MAÇÃ NACIONAL GALA", op_peso_kg, False),
        ("🍏 MAÇÃ VERDE", op_peso_kg, False),
        ("🍈 MAMÃO PAPAYA", op_peso_kg, True),
        ("🍈 MAMÃO FORMOSA", op_peso_kg, True),
        ("🥭 MANGA PALMER", ["Unidade"], True),
        ("🥭 MANGA TOMMY", ["Unidade"], True),
        ("🟣 MARACUJÁ", op_peso_kg, False),
        ("🍉 MELANCIA", ["Inteira", "Meia", "Um Quarto"], False),
        ("🍉 MELANCIA BABY", ["Unidade"], False),
        ("🍈 MELÃO", ["Unidade"], False),
        ("🍊 MEXERICA CRAVO", op_peso_kg, False),
        ("🍊 MEXERICA MURGOTE", op_peso_kg, False),
        ("🍊 MEXERICA POKÃ", op_peso_kg, False),
        ("🍊 MEXERICA CHEIROSINHA", op_peso_kg, False),
        ("🍓 MORANGO", ["Bandeja"], False),
        ("🍑 NECTARINA", op_peso_kg, True),
        ("🍐 PERA", op_peso_kg, True),
        ("🍑 PÊSSEGO BRANCO", op_peso_kg, True),
        ("🍑 PÊSSEGO AMARELO", op_peso_kg, True),
        ("🍇 UVA SEM SEMENTE VERDE", ["Bandeja"], False),
        ("🍇 UVA SEM SEMENTE ROXA", ["Bandeja"], False),
        ("🍇 UVA COMUM", op_peso_kg_simples, False),
        ("🥝 KIWI", op_peso_kg, True)
    ],
    "🥬 Verduras e Temperos": [
        ("🥬 ACELGA", ["Unidade"], False),
        ("🌿 AGRIÃO", ["Unidade"], False),
        ("🥗 ALFACE AMERICANA", ["Unidade"], False),
        ("🥗 ALFACE CRESPA", ["Unidade"], False),
        ("🥗 ALFACE ROXA", ["Unidade"], False),
        ("🥗 ALFACE LISA", ["Unidade"], False),
        ("🥗 ALFACE MIMOSA", ["Unidade"], False),
        ("🧅 ALHO PORÓ", ["Unidade"], False),
        ("🌿 ALMEIRÃO", ["Unidade"], False),
        ("🥦 BRÓCOLIS COMUM", ["Unidade"], False),
        ("🥦 BRÓCOLIS JAPONÊS", ["Unidade"], False),
        ("🌿 CHEIRO VERDE", ["Unidade"], False),
        ("🥬 CHICÓRIA", ["Unidade"], False),
        ("🌿 COENTRO", ["Unidade"], False),
        ("🥬 COUVE", ["Unidade"], False),
        ("🌿 ESPINAFRE", ["Unidade"], False),
        ("🌿 HORTELÃ", ["Unidade"], False),
        ("🔴 RABANETE", ["Unidade"], False),
        ("🥬 REPOLHO", ["Unidade"], False),
        ("🌿 RÚCULA", ["Unidade"], False),
        ("🌿 SALSA", ["Unidade"], False),
        ("🌿 SALSÃO", ["Unidade"], False),
        ("🌿 MANJERICÃO", ["Unidade"], False),
        ("🌿 ALECRIM", ["Unidade"], False),
        ("🌿 TOMILHO", ["Unidade"], False),
        ("🫚 GENGIBRE", op_peso_kg, False),
        ("🌽 FARINHA DE MILHO", ["Pacote 500 gr"], False),
        ("🫘 FEIJÃO CARIOQUINHA", op_peso_kg_simples, False),
        ("🥚 OVO CAIPIRA", ["Caixa com 12 (Dúzia)"], False),
        ("🥚 OVO VERMELHO", ["Caixa com 12 (Dúzia)"], False),
        ("🥥 COCO VERDE", ["Unidade"], False),
        ("🫙 PALMITO", ["Vidro"], False),
        ("🍄 CÓGUMELO PORTOBELO", ["Bandeja"], False),
        ("🍄 COGUMELO PARIS", ["Bandeja"], False),
        ("🍄 COGUMELO SHITAKE", ["Bandeja"], False),
        ("🍄 COGUMELO SHIMEGI", ["Bandeja"], False),
        ("🧊 TOFU", ["Unidade"], False),
        ("🌱 BROTO", ["Unidade"], False),
        ("🌸 FLOR COMESTÍVEL", ["Bandeja"], False),
        ("🥤 POLPA DE FRUTAS", ["Pacote 100 gr"], False)
    ],
    "🥔 Legumes e Tubérculos": [
        ("🧄 ALHO", op_peso_kg, False),
        ("🎃 ABÓBORA MADURA", ["2 dedos", "3 dedos", "1 KG", "Meio KG (500 gr)"], False),
        ("🥒 ABOBRINHA CAIPIRA", op_peso_kg, False),
        ("🥒 ABOBRINHA ITÁLIA", op_peso_kg, False),
        ("🍠 BATATA DOCE", op_peso_kg, False),
        ("🥔 BATATA LAVADA", op_peso_kg, False),
        ("🥔 BATATA SUJA", op_peso_kg, False),
        ("🥔 BATATA ASTERIX", op_peso_kg, False),
        ("🥔 BATATA PIRULITO", op_peso_kg, False),
        ("🍆 BERINGELA", op_peso_kg, False),
        ("🟣 BETERRABA", op_peso_kg, False),
        ("🎃 ABÓBORA CABOTIÃ", ["Inteira", "Metade", "Um Quarto"], False),
        ("🎃 ABÓBORA CABOTIÃ PICADA", ["Bandeja"], False),
        ("🧅 CEBOLA ROXA", op_peso_kg, False),
        ("🧅 CEBOLA", op_peso_kg, False),
        ("🥕 CENOURA", op_peso_kg, False),
        ("🥦 COUVE-FLOR", ["Unidade"], False),
        ("🥒 CHUCHU", op_peso_kg, False),
        ("🫛 ERVILHA DEBULHADA CONGELADA", ["Pacote 200 gr"], False),
        ("🫛 ERVILHA TORTA", ["Bandeja 200 gr"], False),
        ("🥔 INHAME", op_peso_kg, False),
        ("🟢 JILÓ", op_peso_kg, False),
        ("🍠 MANDIOCA DESCASCADA CONGELADA", ["Pacote 1 KG"], False),
        ("🥕 MANDIOQUINHA", op_peso_kg, False),
        ("🌽 MILHO VERDE", ["Bandeja com 5 unidades"], False),
        ("🎃 MUGANGO", ["Unidade"], False),
        ("🌶️ PIMENTA DEDO DE MOÇA", op_peso_kg, False),
        ("🌶️ PIMENTA GODÊ", op_peso_kg, False),
        ("🫑 PIMENTÃO VERDE", op_peso_kg, False),
        ("🫑 PIMENTÃO AMARELO", op_peso_kg, False),
        ("🫑 PIMENTÃO VERMELHO", op_peso_kg, False),
        ("🥒 PEPINO COMUM", op_peso_kg, False),
        ("🥒 PEPINO JAPONÊS", op_peso_kg, False),
        ("🟢 QUIABO", op_gramas_limpas, False),
        ("🍅 TOMATE CEREJA", op_gramas_limpas, False),
        ("🍅 TOMATE MOLHO", op_peso_kg, False),
        ("🍅 TOMATE SALADA", op_peso_kg, False),
        ("🍅 TOMATE HOLANDÊS", op_peso_kg, False),
        ("🍅 TOMATE COQUETEL", op_gramas_limpas, False),
        ("🫛 VAGEM", op_gramas_limpas, False)
    ]
}

# Inicializa estados na sessão
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}
if "cliente_nome" not in st.session_state:
    st.session_state.cliente_nome = ""
if "cliente_end" not in st.session_state:
    st.session_state.cliente_end = ""
if "cliente_tel" not in st.session_state:
    st.session_state.cliente_tel = ""
if "cliente_obs" not in st.session_state:
    st.session_state.cliente_obs = ""
if "etapa" not in st.session_state:
    st.session_state.etapa = "pedido"

def salvar_historico_pedido():
    historico_path = "historico_pedidos.csv"
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    itens_str = "; ".join([f"{p}: {q}" for p, q in st.session_state.carrinho.items()])
    
    novo_registro = pd.DataFrame([{
        "Data/Hora": data_hora,
        "Cliente": st.session_state.cliente_nome,
        "Endereço": st.session_state.cliente_end,
        "Telefone": st.session_state.cliente_tel,
        "Observação": st.session_state.cliente_obs,
        "Itens": itens_str
    }])
    
    if os.path.exists(historico_path):
        novo_registro.to_csv(historico_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        novo_registro.to_csv(historico_path, mode='w', header=True, index=False, encoding='utf-8-sig')

# --- TELA 2: TELA DE REVISÃO E CONFIRMAÇÃO DO PEDIDO ---
if st.session_state.etapa == "revisao":
    salvar_historico_pedido()
    
    st.markdown("## 🔍 Conferir Pedido")
    st.markdown("Revise os itens abaixo e os seus dados de entrega antes de enviar:")
    st.markdown("---")
    
    st.markdown("### 👤 Dados de Entrega")
    st.markdown(f"**Nome:** {st.session_state.cliente_nome}")
    st.markdown(f"**Endereço:** {st.session_state.cliente_end}")
    st.markdown(f"**Telefone:** {st.session_state.cliente_tel}")
    if st.session_state.cliente_obs:
        st.markdown(f"**Observações:** {st.session_state.cliente_obs}")
    
    st.markdown("### 🗺️ Localização Aproximada de Entrega (Poços de Caldas - MG)")
    df_mapa = pd.DataFrame({
        'lat': [-21.7861],
        'lon': [-46.5619]
    })
    st.map(df_mapa, zoom=13)
    
    st.markdown("---")
    st.markdown("### 🛒 Itens Escolhidos")
    for prod, qtd in st.session_state.carrinho.items():
        st.markdown(f"- **{prod}**: {qtd}")
        
    st.markdown("---")
    
    msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
    msg += f"👤 *Cliente:* {st.session_state.cliente_nome}\n"
    msg += f"📍 *Endereço:* {st.session_state.cliente_end}\n"
    msg += f"📞 *Telefone:* {st.session_state.cliente_tel}\n"
    if st.session_state.cliente_obs:
        msg += f"📝 *Obs:* {st.session_state.cliente_obs}\n"
    msg += f"\n*ITENS SOLICITADOS:*\n"
    for p, q in st.session_state.carrinho.items():
        msg += f"- {p}: {q}\n"
    
    link_wpp = f"https://wa.me/5535991617906?text={urllib.parse.quote(msg)}"
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("✏️ Refazer / Voltar", use_container_width=True):
            st.session_state.etapa = "pedido"
            st.rerun()
            
    with col_b:
        st.markdown(
            f'<a href="{link_wpp}" target="_blank" style="background-color: #25D366; color: white; padding: 9px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; display: block; text-align: center; font-size: 0.9rem;">📲 Enviar WhatsApp</a>',
            unsafe_allow_html=True
        )
        
    with col_c:
        class PDF(FPDF):
            def header(self):
                has_logo = os.path.exists("logo.png")
                if has_logo:
                    self.image("logo.png", 10, 10, 22)
                    self.set_xy(35, 12)
                else:
                    self.set_xy(10, 12)
                
                self.set_font("Arial", "B", 13)
                self.set_text_color(30, 61, 47) 
                self.cell(0, 5, "BANCA DO MANÉ - FRUTAS, VERDURAS E LEGUMES", 0, 1, "L" if has_logo else "C")
                
                if has_logo:
                    self.set_x(35)
                self.set_font("Arial", "", 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 4, "Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG", 0, 1, "L" if has_logo else "C")
                
                if has_logo:
                    self.set_x(35)
                self.cell(0, 4, "Fone: (35) 3721-0088 / (35) 9 9846-4384", 0, 1, "L" if has_logo else "C")
                
                self.set_y(max(self.get_y(), 30))
                self.ln(2)
                self.set_draw_color(30, 61, 47)
                self.set_line_width(0.6)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)

            def footer(self):
                self.set_y(-20)
                if os.path.exists("mascote.png"):
                    try:
                        self.image("mascote.png", 175, self.get_y(), 18)
                    except:
                        pass
                
                self.set_font("Arial", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f"Comprovante de Pedido - Página {self.page_no()}", 0, 0, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(245, 247, 246)
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        pdf.cell(150, 6, f" CLIENTE: {st.session_state.cliente_nome}", 1, 0, "L", fill=True)
        pdf.cell(40, 6, f" DATA: {data_atual}", 1, 1, "L", fill=True)
        
        pdf.cell(190, 6, f" ENDEREÇO: {st.session_state.cliente_end}", 1, 1, "L", fill=True)
        pdf.cell(100, 6, f" FONE: {st.session_state.cliente_tel}", 1, 0, "L", fill=True)
        pdf.cell(90, 6, f" OBS: {st.session_state.cliente_obs if st.session_state.cliente_obs else '-'}", 1, 1, "L", fill=True)
        pdf.ln(6)

        pdf.set_fill_color(30, 61, 47)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(100, 7, "  Produto Solicitado", 1, 0, "L", fill=True)
        pdf.cell(50, 7, "Quantidade / Ponto", 1, 0, "C", fill=True)
        pdf.cell(40, 7, "Valor (R$)", 1, 1, "C", fill=True)

        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(50, 50, 50)
        
        fill_toggle = False
        for p, q in st.session_state.carrinho.items():
            if fill_toggle:
                pdf.set_fill_color(250, 250, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            nome_limpo = p.split(" ", 1)[1] if " " in p else p
            pdf.cell(100, 6, f"  {nome_limpo}", 1, 0, "L", fill=True)
            pdf.cell(50, 6, f"{q}", 1, 0, "C", fill=True)
            pdf.cell(40, 6, "R$ ________", 1, 1, "C", fill=True)
            fill_toggle = not fill_toggle

        pdf.ln(10)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 6, "Agradecemos a preferência! Banca do Mané - Qualidade e Tradição.", 0, 1, "C")

        tmp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(tmp_dir, "pedido_banca_do_mane.pdf")
        pdf.output(pdf_path)
        
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Baixar PDF Oficial",
                data=pdf_file,
                file_name="pedido_banca_do_mane.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- TELA 1: ESCOLHA DOS PRODUTOS E BARRA LATERAL ---
else:
    aba_selecionada = st.radio("Escolha o setor:", list(catalogo.keys()), horizontal=True)
    st.markdown("---")
    
    st.markdown(f"### 📋 Lista de {aba_selecionada}")
    st.markdown("<small>Escolha a quantidade, o ponto de maturação (se aplicável) e clique em <b>Inserir no Pedido</b>.</small>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    produtos_da_categoria = catalogo[aba_selecionada]

    for item in produtos_da_categoria:
        produto = item[0]
        opcoes_medida = item[1]
        permite_maturacao = item[2] # True se aceita ponto de maturação separado

        if permite_maturacao:
            c_nome, c_qtd, c_mat, c_tipo, c_btn = st.columns([2.2, 0.8, 1.2, 1.2, 1.1])
        else:
            c_nome, c_qtd, c_tipo, c_btn = st.columns([2.6, 0.9, 1.5, 1.3])
        
        with c_nome:
            st.markdown(f"**{produto}**")
            if produto in st.session_state.carrinho:
                st.markdown(f"<small style='color: green;'>✔ Carrinho: <b>{st.session_state.carrinho[produto]}</b></small>", unsafe_allow_html=True)
                
        with c_qtd:
            q_val = st.text_input(f"Qtd {produto}", value="1", key=f"q_{produto}", label_visibility="collapsed")
            
        if permite_maturacao:
            with c_mat:
                m_val = st.selectbox(f"Mat {produto}", ["Normal", "Mais verde", "Mais maduro"], key=f"m_{produto}", label_visibility="collapsed")
        
        with c_tipo:
            t_val = st.selectbox(f"Tipo {produto}", opcoes_medida, key=f"t_{produto}", label_visibility="collapsed")
            
        with c_btn:
            if st.button("Inserir ➕", key=f"btn_{produto}", use_container_width=True):
                if q_val.strip():
                    if permite_maturacao and m_val != "Normal":
                        st.session_state.carrinho[produto] = f"{q_val} {t_val} ({m_val})"
                    else:
                        st.session_state.carrinho[produto] = f"{q_val} {t_val}"
                    st.rerun()

        st.markdown("<hr style='margin: 5px 0px; border-color: #eee;'>", unsafe_allow_html=True)

    # --- BARRA LATERAL: CARRINHO E DADOS DE ENTREGA ---
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
            st.markdown("<small>Preencha para salvar no navegador.</small>", unsafe_allow_html=True)
            
            nome = st.text_input("Seu Nome:", value=st.session_state.cliente_nome)
            endereco = st.text_input("Endereço e Bairro:", value=st.session_state.cliente_end)
            telefone = st.text_input("Telefone:", value=st.session_state.cliente_tel)
            observacao = st.text_area("Observações (Troco, portão, etc.):", value=st.session_state.cliente_obs)
            
            st.session_state.cliente_nome = nome
            st.session_state.cliente_end = endereco
            st.session_state.cliente_tel = telefone
            st.session_state.cliente_obs = observacao
            
            st.divider()
            
            if st.button("📦 Fechar e Revisar Pedido", type="primary", use_container_width=True):
                if not nome or not endereco:
                    st.error("Preencha Nome e Endereço para continuar!")
                else:
                    st.session_state.etapa = "revisao"
                    st.rerun()
