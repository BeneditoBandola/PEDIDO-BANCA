import streamlit as st
import pandas as pd
json_module = json = __import__('json')
from fpdf import FPDF
import tempfile
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re

st.set_page_config(
    page_title="Banca do Mané - Fazer Pedido",
    page_icon="🍌",
    layout="centered"
)

# Título principal
st.markdown("<h1 style='text-align: center; color: #1e3d2f;'>🍌 Banca do Mané 🍅</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG</p>", unsafe_allow_html=True)
st.markdown("---")

# Funções de Gerenciamento de Clientes (JSON)
ARQUIVO_CLIENTES = "clientes.json"

def carregar_clientes():
    if os.path.exists(ARQUIVO_CLIENTES):
        try:
            with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_cliente(telefone, nome, endereco, email, obs):
    clientes = carregar_clientes()
    clientes[telefone] = {
        "nome": nome,
        "endereco": endereco,
        "email": email,
        "obs": obs
    }
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)

# Função para limpar emojis e garantir compatibilidade com o PDF (evita UnicodeEncodeException)
def limpar_texto_pdf(texto):
    if not texto:
        return ""
    # Remove emojis e caracteres fora do padrão latin-1/ascii se necessário
    texto_limpo = re.sub(r'[^\w\s\-\(\)\.,/:;áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]', '', str(texto))
    return texto_limpo.strip()

# Opções padronizadas + Opção livre
op_maturacao = ["Normal", "Mais verde", "Mais maduro"]
op_peso_kg = ["1 KG", "2 KG", "3 KG", "Meio KG (500 gr)", "Unidade", "✏️ Outra quantidade (Digitar livremente)"]
op_peso_kg_simples = ["1 KG", "2 KG", "3 KG", "Meio KG (500 gr)", "✏️ Outra quantidade (Digitar livremente)"]
op_gramas_limpas = ["100 gr", "200 gr", "300 gr", "400 gr", "500 gr", "600 gr", "700 gr", "800 gr", "900 gr", "1 KG", "2 KG", "✏️ Outra quantidade (Digitar livremente)"]

# Catálogo reestruturado
catalogo = {
    "🍎 Frutas": [
        ("🥑 ABACATE", op_peso_kg, True),
        ("🥑 AVOCADO", op_peso_kg, True),
        ("🍍 ABACAXI PÉROLA", ["Unidade", "2 Unidades", "3 Unidades", "✏️ Outra quantidade (Digitar livremente)"], True),
        ("🍑 AMEIXA AMARELA", op_peso_kg, True),
        ("🍑 AMEIXA VERMELHA", op_peso_kg, True),
        ("🍈 ATEMÓIA", op_peso_kg, True),
        ("🌵 PITAYA", op_peso_kg, True),
        ("🍌 BANANA NANICA", ["Unidade", "Penca", "2 Pencas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍌 BANANA PRATA", ["Unidade", "Penca", "2 Pencas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥭 CAQUI", ["Bandeja", "2 Bandejas", "Unidade", "✏️ Outra quantidade (Digitar livremente)"], True),
        ("⭐ CARAMBOLA", ["Bandeja", "2 Bandejas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("FIGO", ["Bandeja", "2 Bandejas", "✏️ Outra quantidade (Digitar livremente)"], False), 
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
        ("🥭 MANGA PALMER", ["Unidade", "2 Unidades", "✏️ Outra quantidade (Digitar livremente)"], True),
        ("🥭 MANGA TOMMY", ["Unidade", "2 Unidades", "✏️ Outra quantidade (Digitar livremente)"], True),
        ("🟣 MARACUJÁ", op_peso_kg, False),
        ("🍉 MELANCIA", ["Inteira", "Meia", "Um Quarto", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍉 MELANCIA BABY", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍈 MELÃO", ["Unidade", "2 Unidades", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍊 MEXERICA CRAVO", op_peso_kg, False),
        ("🍊 MEXERICA MURGOTE", op_peso_kg, False),
        ("🍊 MEXERICA POKÃ", op_peso_kg, False),
        ("🍊 MEXERICA CHEIROSINHA", op_peso_kg, False),
        ("🍓 MORANGO", ["Bandeja", "2 Bandejas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍑 NECTARINA", op_peso_kg, True),
        ("🍐 PERA", op_peso_kg, True),
        ("🍑 PÊSSEGO BRANCO", op_peso_kg, True),
        ("🍑 PÊSSEGO AMARELO", op_peso_kg, True),
        ("🍇 UVA SEM SEMENTE VERDE", ["Bandeja", "2 Bandejas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍇 UVA SEM SEMENTE ROXA", ["Bandeja", "2 Bandejas", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🍇 UVA COMUM", op_peso_kg_simples, False),
        ("🥝 KIWI", op_peso_kg, True)
    ],
    "🥬 Verduras e Temperos": [
        ("🥬 ACELGA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 AGRIÃO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥗 ALFACE AMERICANA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥗 ALFACE CRESPA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥗 ALFACE ROXA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥗 ALFACE LISA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥗 ALFACE MIMOSA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🧅 ALHO PORÓ", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 ALMEIRÃO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥦 BRÓCOLIS COMUM", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥦 BRÓCOLIS JAPONÊS", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 CHEIRO VERDE", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥬 CHICÓRIA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 COENTRO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥬 COUVE", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 ESPINAFRE", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 HORTELÃ", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🔴 RABANETE", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🥬 REPOLHO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 RÚCULA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 SALSA", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 SALSÃO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 MANJERICÃO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 ALECRIM", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🌿 TOMILHO", ["Unidade", "✏️ Outra quantidade (Digitar livremente)"], False),
        ("🫚 GENGIBRE", op_peso_kg, False),
        ("🌽 FARINHA DE MILHO", ["Pacote 500 gr", "2 Pacotes 500 gr"], False),
        ("🫘 FEIJÃO CARIOQUINHA", op_peso_kg_simples, False),
        ("🥚 OVO CAIPIRA", ["Caixa com 12 (Dúzia)", "2 Caixas"], False),
        ("🥚 OVO VERMELHO", ["Caixa com 12 (Dúzia)", "2 Caixas"], False),
        ("🥥 COCO VERDE", ["Unidade", "2 Unidades"], False),
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
        ("🎃 ABÓBORA MADURA", ["2 dedos", "3 dedos", "1 KG", "2 KG", "Meio KG (500 gr)", "✏️ Outra quantidade (Digitar livremente)"], False),
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
        ("🍠 MANDIOCA DESCASCADA CONGELADA", ["Pacote 1 KG", "2 Pacotes 1 KG"], False),
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
if "cliente_tel" not in st.session_state:
    st.session_state.cliente_tel = ""
if "cliente_nome" not in st.session_state:
    st.session_state.cliente_nome = ""
if "cliente_end" not in st.session_state:
    st.session_state.cliente_end = ""
if "cliente_email" not in st.session_state:
    st.session_state.cliente_email = ""
if "cliente_obs" not in st.session_state:
    st.session_state.cliente_obs = ""
if "etapa" not in st.session_state:
    st.session_state.etapa = "pedido"

def salvar_historico_json():
    json_path = "historico_pedidos.json"
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    novo_pedido = {
        "data_hora": data_hora,
        "cliente": st.session_state.cliente_nome,
        "endereco": st.session_state.cliente_end,
        "telefone": st.session_state.cliente_tel,
        "email": st.session_state.cliente_email,
        "observacao": st.session_state.cliente_obs,
        "itens": st.session_state.carrinho
    }
    
    dados_existentes = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                dados_existentes = json.load(f)
        except:
            dados_existentes = []
            
    dados_existentes.append(novo_pedido)
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

def enviar_email_banca(pdf_path, cliente_nome):
    """Envia o PDF do pedido automaticamente para os e-mails da banca usando Secrets"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
        remetente = st.secrets["email"]["remetente"]
        senha_app = st.secrets["email"]["senha_app"]
    except Exception as e:
        st.error("Erro: Credenciais de e-mail não configuradas nos Secrets do Streamlit.")
        return False
    
    destinatarios = ["andreiabolzanmenezes@gmail.com", "beneditobandola@gmail.com"]
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remetente, senha_app)
        
        for destinatario in destinatarios:
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = f"🛒 Novo Pedido de {cliente_nome} - Banca do Mané"
            
            corpo = f"Olá!\n\nUm novo pedido foi realizado no sistema da Banca do Mané pelo cliente {cliente_nome}.\nO comprovante em PDF segue em anexo para separação e conferência.\n\nAtenciosamente,\nSistema Banca do Mané"
            msg.attach(MIMEText(corpo, 'plain'))
            
            with open(pdf_path, "rb") as f:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                parte.add_header('Content-Disposition', f'attachment; filename="pedido_{cliente_nome.replace(" ", "_")}.pdf"')
                msg.attach(parte)
                
            server.sendmail(remetente, destinatario, msg.as_string())
            
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# Motor Dinâmico e Robusto para Mensagens do WhatsApp
def importar_texto_whatsapp(texto):
    linhas = texto.strip().split("\n")
    
    if not st.session_state.cliente_nome:
        st.session_state.cliente_nome = "Cliente WhatsApp"
    if not st.session_state.cliente_end:
        st.session_state.cliente_end = "Mercado Municipal (Retirada / Entrega WhatsApp)"
    if not st.session_state.cliente_tel:
        st.session_state.cliente_tel = "(35) 99999-9999"
        
    for linha in linhas:
        linha_inf = linha.lower().strip()
        if not linha_inf:
            continue
            
        if any(w in linha_inf for w in ["bom dia", "boa tarde", "boa noite", "olá", "ola", "p hj", "para hoje", "por favor", "favor"]):
            if len(linha_inf) > 15:
                st.session_state.cliente_obs = linha.strip()
            continue
            
        produto_encontrado = None
        
        if "limão" in linha_inf or "limao" in linha_inf:
            produto_encontrado = "LIMÃO TAITI"
        elif "abacaxi" in linha_inf:
            produto_encontrado = "ABACAXI PÉROLA"
        elif "morango" in linha_inf:
            produto_encontrado = "MORANGO"
        elif "manga" in linha_inf:
            produto_encontrado = "MANGA PALMER"
        elif "pepino" in linha_inf:
            produto_encontrado = "PEPINO JAPONÊS"
        elif "tomate cereja" in linha_inf:
            produto_encontrado = "TOMATE CEREJA"
        elif "tomate" in linha_inf:
            produto_encontrado = "TOMATE SALADA"
        elif "couve flor" in linha_inf or "couve-flor" in linha_inf:
            produto_encontrado = "COUVE-FLOR"
        elif "couve" in linha_inf:
            produto_encontrado = "COUVE"
        elif "jiló" in linha_inf or "jilo" in linha_inf:
            produto_encontrado = "JILÓ"
        elif "quiabo" in linha_inf:
            produto_encontrado = "QUIABO"
        elif "ervilha" in linha_inf:
            produto_encontrado = "ERVILHA DEBULHADA CONGELADA"
        elif "salsinha" in linha_inf or "salsa" in linha_inf:
            produto_encontrado = "SALSA"
        elif "agrião" in linha_inf or "agriao" in linha_inf:
            produto_encontrado = "AGRIÃO"
        elif "rúcula" in linha_inf or "rucula" in linha_inf:
            produto_encontrado = "RÚCULA"
        elif "repolho" in linha_inf:
            produto_encontrado = "REPOLHO"
        elif "banana" in linha_inf:
            produto_encontrado = "BANANA PRATA"
        elif "goiaba" in linha_inf:
            produto_encontrado = "GOIABA"
        elif "pêra" in linha_inf or "pera" in linha_inf:
            produto_encontrado = "PERA"
        elif "mamão" in linha_inf or "mamao" in linha_inf:
            produto_encontrado = "MAMÃO FORMOSA"
        elif "maçã" in linha_inf or "maca" in linha_inf:
            produto_encontrado = "MAÇÃ NACIONAL GALA"
        elif "cebola" in linha_inf:
            produto_encontrado = "CEBOLA"
        elif "alho" in linha_inf:
            produto_encontrado = "ALHO"
        elif "mandioquinha" in linha_inf:
            produto_encontrado = "MANDIOQUINHA"
        elif "cenoura" in linha_inf:
            produto_encontrado = "CENOURA"
        elif "batata" in linha_inf:
            produto_encontrado = "BATATA LAVADA"
        elif "cheiro verde" in linha_inf:
            produto_encontrado = "CHEIRO VERDE"
        elif "beterraba" in linha_inf:
            produto_encontrado = "BETERRABA"
            
        if produto_encontrado:
            nums = re.findall(r'\d+', linha_inf)
            qtd_num = nums[0] if nums else "1"
            
            if "dz" in linha_inf or "dúzia" in linha_inf:
                q_str = f"{qtd_num} Dúzia(s)" if int(qtd_num) > 1 else "Caixa com 12 (Dúzia)"
            elif "cx" in linha_inf or "caixa" in linha_inf:
                q_str = f"{qtd_num} Caixa(s)"
            elif "k" in linha_inf or "kg" in linha_inf:
                q_str = f"{qtd_num} KG"
            elif produto_encontrado in ["CHEIRO VERDE", "COUVE", "AGRIÃO", "RÚCULA", "REPOLHO"]:
                q_str = f"{qtd_num} Unidade(s)"
            else:
                q_str = f"{qtd_num} Unidades"
                
            st.session_state.carrinho[produto_encontrado] = q_str

# --- TELA 2: TELA DE REVISÃO E ENVIO AUTOMÁTICO ---
if st.session_state.etapa == "revisao":
    salvar_historico_json()
    
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
    pdf.cell(150, 6, limpiar_texto_pdf(f" CLIENTE: {st.session_state.cliente_nome}"), 1, 0, "L", fill=True)
    pdf.cell(40, 6, f" DATA: {data_atual}", 1, 1, "L", fill=True)
    
    pdf.cell(190, 6, limpiar_texto_pdf(f" ENDEREÇO: {st.session_state.cliente_end}"), 1, 1, "L", fill=True)
    pdf.cell(100, 6, limpiar_texto_pdf(f" FONE: {st.session_state.cliente_tel}"), 1, 0, "L", fill=True)
    pdf.cell(90, 6, limpiar_texto_pdf(f" E-MAIL: {st.session_state.cliente_email if st.session_state.cliente_email else '-'}"), 1, 1, "L", fill=True)
    pdf.cell(190, 6, limpiar_texto_pdf(f" OBS: {st.session_state.cliente_obs if st.session_state.cliente_obs else '-'}"), 1, 1, "L", fill=True)
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
        
        pdf.cell(100, 6, limpiar_texto_pdf(f"  {p}"), 1, 0, "L", fill=True)
        pdf.cell(50, 6, limpiar_texto_pdf(f"{q}"), 1, 0, "C", fill=True)
        pdf.cell(40, 6, "R$ ________", 1, 1, "C", fill=True)
        fill_toggle = not fill_toggle

    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, "Agradecemos a preferencia! Banca do Mane - Qualidade e Tradicao.", 0, 1, "C")

    tmp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(tmp_dir, "pedido_banca_do_mane.pdf")
    pdf.output(pdf_path)

    enviar_email_banca(pdf_path, st.session_state.cliente_nome)

    st.success("🎉 Pedido enviado com sucesso para a Banca do Mané!")
    st.info("Recebemos suas informações. Em breve entraremos em contato para confirmar a entrega.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Fazer Novo Pedido", use_container_width=True):
        st.session_state.carrinho = {}
        st.session_state.etapa = "pedido"
        st.rerun()

# --- TELA 1: ESCOLHA DOS PRODUTOS E BARRA LATERAL ---
else:
    aba_selecionada = st.radio("Escolha o setor:", list(catalogo.keys()), horizontal=True)
    st.markdown("---")
    
    st.markdown(f"### 📋 Lista de {aba_selecionada}")
    st.markdown("<small>Escolha os itens desejados ou digite livremente e clique em <b>Inserir no Pedido</b>.</small>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    produtos_da_categoria = catalogo[aba_selecionada]

    for item in produtos_da_categoria:
        produto = item[0]
        opcoes_medida = item[1]
        permite_maturacao = item[2]

        if permite_maturacao:
            c_nome, c_mat, c_tipo, c_btn = st.columns([2.2, 1.4, 1.9, 1.1])
        else:
            c_nome, c_tipo, c_btn = st.columns([2.8, 2.1, 1.1])
        
        with c_nome:
            st.markdown(f"**{produto}**")
            if produto in st.session_state.carrinho:
                st.markdown(f"<small style='color: green;'>✔ Carrinho: <b>{st.session_state.carrinho[produto]}</b></small>", unsafe_allow_html=True)
                
        if permite_maturacao:
            with c_mat:
                m_val = st.selectbox(f"Mat {produto}", op_maturacao, key=f"m_{produto}", label_visibility="collapsed")
            with c_tipo:
                t_val = st.selectbox(f"Tipo {produto}", opcoes_medida, key=f"t_{produto}", label_visibility="collapsed")
        else:
            with c_tipo:
                t_val = st.selectbox(f"Tipo {produto}", opcoes_medida, key=f"t_{produto}", label_visibility="collapsed")
        
        livre_val = ""
        if "Outra quantidade" in t_val:
            livre_val = st.text_input(f"Especifique {produto}", placeholder="Ex: 1kg e meio...", key=f"livre_{produto}")
            
        with c_btn:
            if st.button("Inserir ➕", key=f"btn_{produto}", use_container_width=True):
                qtd_final = livre_val if "Outra quantidade" in t_val and livre_val else t_val
                
                if permite_maturacao and m_val != "Normal":
                    st.session_state.carrinho[produto] = f"{qtd_final} ({m_val})"
                else:
                    st.session_state.carrinho[produto] = f"{qtd_final}"
                st.rerun()

        st.markdown("<hr style='margin: 5px 0px; border-color: #eee;'>", unsafe_allow_html=True)

    # --- BARRA LATERAL: CARRINHO E CADASTRO INTELIGENTE + IMPORTADOR WHATSAPP ---
    with st.sidebar:
        st.header("🛒 Seu Carrinho")
        
        with st.expander("📲 Importar Pedido do WhatsApp"):
            st.markdown("<small>Cole a lista enviada pelo cliente abaixo:</small>", unsafe_allow_html=True)
            texto_wpp = st.text_area("Texto do WhatsApp", placeholder="3 dz de limão\n2 abacaxi\n2 cx de morango...", label_visibility="collapsed")
            if st.button("Converter em Pedido", use_container_width=True):
                if texto_wpp.strip():
                    importar_texto_whatsapp(texto_wpp)
                    st.success("Itens e dados preenchidos com sucesso!")
                    st.rerun()
                else:
                    st.warning("Cole o texto do pedido primeiro.")
        
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
            st.subheader("👤 Identificação do Cliente")
            st.markdown("<small>Digite seu telefone para carregar dados ou cadastrar:</small>", unsafe_allow_html=True)
            
            telefone_digitado = st.text_input("Telefone (WhatsApp):", value=st.session_state.cliente_tel)
            
            if telefone_digitado != st.session_state.cliente_tel:
                st.session_state.cliente_tel = telefone_digitado
                clientes_cadastrados = carregar_clientes()
                if telefone_digitado in clientes_cadastrados:
                    dados = clientes_cadastrados[telefone_digitado]
                    st.session_state.cliente_nome = dados.get("nome", "")
                    st.session_state.cliente_end = dados.get("endereco", "")
                    st.session_state.cliente_email = dados.get("email", "")
                    st.session_state.cliente_obs = dados.get("obs", "")
                    st.rerun()

            nome = st.text_input("Seu Nome:", value=st.session_state.cliente_nome)
            endereco = st.text_input("Endereço e Bairro:", value=st.session_state.cliente_end)
            email = st.text_input("E-mail (Opcional):", value=st.session_state.cliente_email)
            observacao = st.text_area("Observações (Troco, portão, etc.):", value=st.session_state.cliente_obs)
            
            st.session_state.cliente_nome = nome
            st.session_state.cliente_end = endereco
            st.session_state.cliente_email = email
            st.session_state.cliente_obs = observacao
            
            st.divider()
            
            if st.button("📦 Fechar e Enviar Pedido", type="primary", use_container_width=True):
                if not nome or not endereco or not telefone_digitado:
                    st.error("Preencha Telefone, Nome e Endereço!")
                else:
                    salvar_cliente(telefone_digitado, nome, endereco, email, observacao)
                    st.session_state.etapa = "revisao"
                    st.rerun()
