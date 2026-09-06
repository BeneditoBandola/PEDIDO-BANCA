import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import urllib.parse

st.set_page_config(
    page_title="Banca do Mané - Fazer Pedido",
    page_icon="🍌",
    layout="centered"
)

# Título principal
st.markdown("<h1 style='text-align: center; color: #1e3d2f;'>🍌 Banca do Mané 🍅</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>", unsafe_allow_html=True)
st.markdown("---")

# Catálogo reestruturado com as regras exatas informadas
catalogo = {
    "🍎 Frutas": [
        ("ABACATE", ["Quilo", "Unidade"]),
        ("AVOCADO", ["Quilo", "Unidade"]),
        ("ABACAXI PÉROLA", ["Unidade"]),
        ("AMEIXA AMARELA", ["Quilo", "Unidade"]),
        ("AMEIXA VERMELHA", ["Quilo", "Unidade"]),
        ("ATEMÓIA", ["Quilo", "Unidade"]),
        ("PITAYA", ["Quilo", "Unidade"]),
        ("BANANA NANICA", ["Quilo", "Quantidade (Unidade)"]),
        ("BANANA PRATA", ["Quilo", "Unidade"]),
        ("CAQUI", ["Bandeja", "Unidade"]),
        ("CARAMBOLA", ["Bandeja"]),
        ("FIGO", ["Bandeja"]),
        ("GOIABA", ["Quilo", "Unidade"]),
        ("LARANJA BAIANA", ["Quilo", "Unidade"]),
        ("LARANJA LIMA", ["Quilo", "Unidade"]),
        ("LARANJA PERA", ["Quilo", "Unidade"]),
        ("LIMA DA PÉRSIA", ["Quilo", "Unidade"]),
        ("LIMÃO CRAVO", ["Quilo", "Unidade"]),
        ("LIMÃO SICILIANO", ["Quilo", "Unidade"]),
        ("LIMÃO TAITI", ["Quilo", "Unidade"]),
        ("MAÇÃ ARGENTINA", ["Quilo", "Unidade"]),
        ("MAÇÃ NAC. FUJI", ["Quilo", "Unidade"]),
        ("MAÇÃ NAC. GALA", ["Quilo", "Unidade"]),
        ("MAÇÃ VERDE", ["Quilo", "Unidade"]),
        ("MAMÃO PAPAYA", ["Quilo", "Unidade"]),
        ("MAMÃO FORMOSA", ["Quilo", "Unidade"]),
        ("MANGA PALMER", ["Quilo", "Unidade"]),
        ("MANGA TOMMY", ["Quilo", "Unidade"]),
        ("MARACUJÁ", ["Quilo", "Unidade"]),
        ("MELANCIA", ["Inteira", "Meia", "Um Quarto"]),
        ("MELÃO", ["Unidade"]),
        ("MEXERICA CRAVO", ["Quilo", "Unidade"]),
        ("MEXERICA MURGOTE", ["Quilo", "Unidade"]),
        ("MEXERICA POKÃ", ["Quilo", "Unidade"]),
        ("MEXERICA CHEIROSINHA", ["Quilo", "Unidade"]),
        ("MORANGO", ["Bandeja"]),
        ("NECTARINA", ["Quilo", "Unidade"]),
        ("PERA", ["Quilo", "Unidade"]),
        ("PÊSSEGO BRANCO", ["Quilo", "Unidade"]),
        ("PÊSSEGO AMARELO", ["Quilo", "Unidade"]),
        ("UVA SEM SEMENTE", ["Bandeja"]),
        ("UVA COMUM", ["Quilo"]),
        ("KIWI", ["Quilo", "Unidade"])
    ],
    "🥬 Verduras e Temperos": [
        ("ACELGA", ["Unidade"]),
        ("AGRIÃO", ["Unidade"]),
        ("ALFACE AMERICANA", ["Unidade"]),
        ("ALFACE CRESPA", ["Unidade"]),
        ("ALFACE ROXA", ["Unidade"]),
        ("ALFACE LISA", ["Unidade"]),
        ("ALFACE MIMOSA", ["Unidade"]),
        ("ALHO PORÓ", ["Unidade"]),
        ("ALMEIRÃO", ["Unidade"]),
        ("BRÓCOLIS COMUM", ["Unidade"]),
        ("BRÓCOLIS JAPONÊS", ["Unidade"]),
        ("CHEIRO VERDE", ["Unidade"]),
        ("CHICÓRIA", ["Unidade"]),
        ("COENTRO", ["Unidade"]),
        ("COUVE", ["Unidade"]),
        ("ESPINAFRE", ["Unidade"]),
        ("HORTELÃ", ["Unidade"]),
        ("RABANETE", ["Unidade"]),
        ("REPOLHO", ["Quilo", "Unidade"]),
        ("RÚCULA", ["Unidade"]),
        ("SALSA", ["Unidade"]),
        ("SALSÃO", ["Unidade"]),
        ("MANJERICÃO", ["Unidade"]),
        ("ALECRIM", ["Unidade"]),
        ("TOMILHO", ["Unidade"]),
        ("GENGIBRE", ["Quilo", "Unidade"]),
        ("FARINHA DE MILHO", ["Pacote 500g"]),
        ("FEIJÃO CARIOQUINHA", ["Quilo"]),
        ("OVO CAIPIRA", ["Caixa com 12 (Dúzia)"]),
        ("OVO VERMELHO", ["Caixa com 12 (Dúzia)"]),
        ("COCO VERDE", ["Unidade"]),
        ("PALMITO", ["Vidro"]),
        ("COGUMELO PORTOBELO", ["Bandeja"]),
        ("COGUMELO PARIS", ["Bandeja"]),
        ("COGUMELO SHITAKE", ["Bandeja"]),
        ("COGUMELO SHIMEGI", ["Bandeja"]),
        ("TOFU", ["Unidade"]),
        ("BROTO", ["Unidade"]),
        ("FLOR COMESTÍVEL", ["Bandeja"]),
        ("POLPA DE FRUTAS", ["Pacote 100g"])
    ],
    "🥔 Legumes e Tubérculos": [
        ("ALHO", ["Quilo", "Unidade"]),
        ("ABÓBORA MADURA", ["Quilo"]),
        ("ABOBRINHA CAIPIRA", ["Quilo", "Unidade"]),
        ("ABOBRINHA ITÁLIA", ["Quilo", "Unidade"]),
        ("BATATA DOCE", ["Quilo", "Unidade"]),
        ("BATATA LAVADA", ["Quilo", "Unidade"]),
        ("BATATA SUJA", ["Quilo", "Unidade"]),
        ("BATATA ASTERIX", ["Quilo", "Unidade"]),
        ("BATATA PIRULITO", ["Quilo", "Unidade"]),
        ("BERINGELA", ["Quilo", "Unidade"]),
        ("BETERRABA", ["Quilo", "Unidade"]),
        ("ABÓBORA CABOTIÃ", ["Inteira", "Metade", "Um Quarto"]),
        ("ABÓBORA CABOTIÃ PICADA", ["Bandeja"]),
        ("CEBOLA ROXA", ["Quilo", "Unidade"]),
        ("CEBOLA", ["Quilo", "Unidade"]),
        ("CENOURA", ["Quilo", "Unidade"]),
        ("COUVE-FLOR", ["Unidade"]),
        ("CHUCHU", ["Quilo", "Unidade"]),
        ("ERVILHA DEBULHADA CONGELADA", ["Pacote 200g"]),
        ("ERVILHA TORTA", ["Bandeja 200g"]),
        ("INHAME", ["Quilo", "Unidade"]),
        ("JILÓ", ["Quilo", "Unidade"]),
        ("MANDIOCA DESCASCADA CONGELADA", ["Pacote 1kg"]),
        ("MANDIQUINHA", ["Quilo", "Unidade"]),
        ("MILHO VERDE", ["Bandeja com 5 unidades"]),
        ("MUGANGO", ["Unidade"]),
        ("PIMENTA DEDO DE MOÇA", ["Quilo", "Unidade"]),
        ("PIMENTA GODÊ", ["Quilo", "Unidade"]),
        ("PIMENTÃO VERDE", ["Quilo", "Unidade"]),
        ("PIMENTÃO AMARELO", ["Quilo", "Unidade"]),
        ("PIMENTÃO VERMELHO", ["Quilo", "Unidade"]),
        ("PEPINO COMUM", ["Quilo", "Unidade"]),
        ("PEPINO JAPONÊS", ["Quilo", "Unidade"]),
        ("QUIABO", ["100g", "200g", "500g", "1 Quilo"]),
        ("TOMATE CEREJA", ["Bandeja", "Quilo"]),
        ("TOMATE MOLHO", ["Quilo", "Unidade"]),
        ("TOMATE SALADA", ["Quilo", "Unidade"]),
        ("TOMATE HOLANDÊS", ["Quilo", "Unidade"]),
        ("TOMATE COQUETEL", ["100g", "200g", "300g", "500g", "1 Quilo"]),
        ("VAGEM", ["100g", "200g", "300g", "500g", "1 Quilo"])
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
if "etapa" not in st.session_state:
    st.session_state.etapa = "pedido"

# --- TELA 2: TELA DE REVISÃO E CONFIRMAÇÃO DO PEDIDO ---
if st.session_state.etapa == "revisao":
    st.markdown("## 🔍 Conferir Pedido")
    st.markdown("Revise os itens abaixo e os seus dados de entrega antes de enviar:")
    st.markdown("---")
    
    st.markdown("### 👤 Dados de Entrega")
    st.markdown(f"**Nome:** {st.session_state.cliente_nome}")
    st.markdown(f"**Endereço:** {st.session_state.cliente_end}")
    st.markdown(f"**Telefone:** {st.session_state.cliente_tel}")
    
    st.markdown("---")
    st.markdown("### 🛒 Itens Escolhidos")
    for prod, qtd in st.session_state.carrinho.items():
        st.markdown(f"- **{prod}**: {qtd}")
        
    st.markdown("---")
    
    # Monta a mensagem para WhatsApp
    msg = f"*NOVO PEDIDO - BANCA DO MANÉ*\n\n"
    msg += f"👤 *Cliente:* {st.session_state.cliente_nome}\n"
    msg += f"📍 *Endereço:* {st.session_state.cliente_end}\n"
    msg += f"📞 *Telefone:* {st.session_state.cliente_tel}\n\n"
    msg += f"*ITENS SOLICITADOS:*\n"
    for p, q in st.session_state.carrinho.items():
        msg += f"- {p}: {q}\n"
    
    link_wpp = f"https://wa.me/5535998464384?text={urllib.parse.quote(msg)}"
    
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
        # Geração do PDF Comercial Oficial com Logotipo e Mascote
        class PDF(FPDF):
            def header(self):
                has_logo = os.path.exists("logo.png")
                if has_logo:
                    self.image("logo.png", 10, 10, 25)
                    self.set_xy(38, 12)
                else:
                    self.set_xy(10, 12)
                
                self.set_font("Arial", "B", 14)
                self.set_text_color(30, 61, 47) 
                self.cell(0, 6, "BANCA DO MANÉ", 0, 1, "L" if has_logo else "C")
                
                if has_logo:
                    self.set_x(38)
                self.set_font("Arial", "", 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 4, "Frutas, Verduras e Legumes - Mercado Municipal (Box 43 a 48)", 0, 1, "L" if has_logo else "C")
                
                if has_logo:
                    self.set_x(38)
                self.cell(0, 4, "Poços de Caldas - MG | Fone: (35) 3721-0088 / (35) 9 9846-4384", 0, 1, "L" if has_logo else "C")
                
                self.set_y(max(self.get_y(), 32))
                self.ln(2)
                self.set_draw_color(30, 61, 47)
                self.set_line_width(0.8)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(6)

            def footer(self):
                self.set_y(-25)
                if os.path.exists("mascote.png"):
                    try:
                        self.image("mascote.png", 175, self.get_y(), 22)
                    except:
                        pass
                
                self.set_font("Arial", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f"Comprovante de Pedido gerado digitalmente - Página {self.page_no()}", 0, 0, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 7, "COMPROVANTE DE SOLICITAÇÃO DE PEDIDO", 0, 1, "L")
        pdf.ln(2)

        pdf.set_fill_color(245, 247, 246)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "  DADOS DO CLIENTE PARA ENTREGA:", 0, 1, "L", fill=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, f"  Nome: {st.session_state.cliente_nome}", 0, 1, "L", fill=True)
        pdf.cell(0, 5, f"  Endereço: {st.session_state.cliente_end}", 0, 1, "L", fill=True)
        pdf.cell(0, 5, f"  Telefone: {st.session_state.cliente_tel}", 0, 1, "L", fill=True)
        pdf.ln(6)

        pdf.set_fill_color(30, 61, 47)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(130, 7, "  Produto", 1, 0, "L", fill=True)
        pdf.cell(60, 7, "Quantidade", 1, 1, "C", fill=True)

        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(50, 50, 50)
        
        fill_toggle = False
        for p, q in st.session_state.carrinho.items():
            if fill_toggle:
                pdf.set_fill_color(250, 250, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.cell(130, 6, f"  {p}", 1, 0, "L", fill=True)
            pdf.cell(60, 6, f"{q}", 1, 1, "C", fill=True)
            fill_toggle = not fill_toggle

        pdf.ln(10)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 6, "Agradecemos a preferência! Entraremos em contato para confirmar a entrega.", 0, 1, "C")

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
    st.markdown("<small>Escolha a quantidade, selecione a opção desejada e clique em <b>Inserir no Pedido</b>.</small>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    produtos_da_categoria = catalogo[aba_selecionada]

    for produto, opcoes in produtos_da_categoria:
        c_nome, c_qtd, c_tipo, c_btn = st.columns([2.5, 1.2, 1.5, 1.3])
        
        with c_nome:
            st.markdown(f"**{produto}**")
            if produto in st.session_state.carrinho:
                st.markdown(f"<small style='color: green;'>✔ No carrinho: <b>{st.session_state.carrinho[produto]}</b></small>", unsafe_allow_html=True)
                
        with c_qtd:
            q_val = st.text_input(f"Qtd {produto}", value="1", key=f"q_{produto}", label_visibility="collapsed")
            
        with c_tipo:
            t_val = st.selectbox(f"Tipo {produto}", opcoes, key=f"t_{produto}", label_visibility="collapsed")
            
        with c_btn:
            if st.button("Inserir ➕", key=f"btn_{produto}", use_container_width=True):
                if q_val.strip():
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
            
            st.session_state.cliente_nome = nome
            st.session_state.cliente_end = endereco
            st.session_state.cliente_tel = telefone
            
            st.divider()
            
            if st.button("📦 Fechar e Revisar Pedido", type="primary", use_container_width=True):
                if not nome or not endereco:
                    st.error("Preencha Nome e Endereço para continuar!")
                else:
                    st.session_state.etapa = "revisao"
                    st.rerun()
