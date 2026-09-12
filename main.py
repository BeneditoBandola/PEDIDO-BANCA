import base64
from datetime import datetime
from fpdf import FPDF
import json
import os
import re
import requests
import tempfile
from flask import Flask, jsonify, request

app = Flask(__name__)

ARQUIVO_HISTORICO = "historico_pedidos.json"

# Número de telefone autorizado
NUMERO_AUTORIZADO = "3598464384"


def limpiar_texto_pdf(texto):
  if not texto:
    return ""
  return re.sub(
      r"[^\w\s\-\(\)\.,/:;áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]", "", str(texto)
  ).strip()


def interpretar_e_gerar_pedido(texto_wpp, nome_cliente="Cliente WhatsApp"):
  carrinho = {}
  linhas = texto_wpp.strip().split("\n")
  obs_cliente = "Pedido via WhatsApp Automático"

  for linha in linhas:
    linha_inf = linha.lower().strip()
    if not linha_inf:
      continue
    if any(
        w in linha_inf
        for w in [
            "bom dia",
            "boa tarde",
            "boa noite",
            "olá",
            "ola",
            "p hj",
            "para hoje",
            "por favor",
            "favor",
        ]
    ):
      if len(linha_inf) > 15:
        obs_cliente = linha.strip()
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
    elif "ervilha" in linha_inf or "ervlha" in linha_inf:
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
      nums = re.findall(r"\d+", linha_inf)
      qtd_num = nums[0] if nums else "1"
      if "dz" in linha_inf or "dúzia" in linha_inf:
        q_str = (
            f"{qtd_num} Dúzia(s)"
            if int(qtd_num) > 1
            else "Caixa com 12 (Dúzia)"
        )
      elif "cx" in linha_inf or "caixa" in linha_inf:
        q_str = f"{qtd_num} Caixa(s)"
      elif "k" in linha_inf or "kg" in linha_inf:
        q_str = f"{qtd_num} KG"
      else:
        q_str = (
            f"{qtd_num} Unidade"
            if int(qtd_num) == 1
            else f"{qtd_num} Unidades"
        )
      carrinho[produto_encontrado] = q_str

  if not carrinho:
    return False, "Nenhum produto identificado."

  data_hoje = datetime.now().strftime("%d/%m/%Y")
  dados_existentes = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_existentes = json.load(f)
    except:
      dados_existentes = []

  pedidos_hoje = [
      p
      for p in dados_existentes
      if p.get("data_hora", "").startswith(datetime.now().strftime("%Y-%m-%d"))
  ]
  numero_sequencial = len(pedidos_hoje) + 1
  codigo_pedido = f"#{numero_sequencial:02d} / {data_hoje}"

  novo_pedido = {
      "codigo": codigo_pedido,
      "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "cliente": nome_cliente,
      "endereco": "Encaminhado via WhatsApp",
      "telefone": nome_cliente,
      "email": "",
      "observacao": obs_cliente,
      "itens": carrinho,
  }
  dados_existentes.append(novo_pedido)
  with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
    json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

  # Geração do PDF local
  class PDF(FPDF):

    def header(self):
      if os.path.exists("logo.png"):
        self.image("logo.png", 10, 10, 22)
        self.set_xy(35, 12)
      else:
        self.set_xy(10, 12)
      self.set_font("Arial", "B", 13)
      self.set_text_color(30, 61, 47)
      self.cell(0, 5, "BANCA DO MANÉ - FRUTAS, VERDURAS E LEGUMES", 0, 1, "L")
      self.set_x(35 if os.path.exists("logo.png") else 10)
      self.set_font("Arial", "", 8)
      self.set_text_color(100, 100, 100)
      self.cell(
          0,
          4,
          "Mercado Municipal - Box 43 a 48 | Poços de Caldas - MG",
          0,
          1,
          "L",
      )
      self.ln(6)

    def footer(self):
      self.set_y(-20)
      self.set_font("Arial", "I", 8)
      self.set_text_color(150, 150, 150)
      self.cell(
          0, 10, f"Comprovante Automático - Página {self.page_no()}", 0, 0, "C"
      )

  pdf = PDF()
  pdf.add_page()
  pdf.set_auto_page_break(auto=True, margin=20)

  pdf.set_font("Arial", "B", 10)
  pdf.set_fill_color(30, 61, 47)
  pdf.set_text_color(255, 255, 255)
  pdf.cell(
      190,
      7,
      limpiar_texto_pdf(f" PEDIDO AUTOMATICO: {codigo_pedido}"),
      1,
      1,
      "C",
      fill=True,
  )

  pdf.set_font("Arial", "B", 9)
  pdf.set_text_color(0, 0, 0)
  pdf.set_fill_color(245, 247, 246)
  pdf.cell(
      150,
      6,
      limpiar_texto_pdf(f" CLIENTE / ORIGEM: {nome_cliente}"),
      1,
      0,
      "L",
      fill=True,
  )
  pdf.cell(40, 6, f" DATA: {data_hoje}", 1, 1, "L", fill=True)
  pdf.cell(190, 6, limpiar_texto_pdf(f" OBS: {obs_cliente}"), 1, 1, "L", fill=True)
  pdf.ln(6)

  pdf.set_fill_color(30, 61, 47)
  pdf.set_text_color(255, 255, 255)
  pdf.cell(100, 7, "  Produto Solicitado", 1, 0, "L", fill=True)
  pdf.cell(50, 7, "Quantidade / Ponto", 1, 0, "C", fill=True)
  pdf.cell(40, 7, "Valor (R$)", 1, 1, "C", fill=True)

  pdf.set_font("Arial", "", 9)
  pdf.set_text_color(50, 50, 50)

  fill_toggle = False
  for p, q in carrinho.items():
    (
        pdf.set_fill_color(250, 250, 250)
        if fill_toggle
        else pdf.set_fill_color(255, 255, 255)
    )
    pdf.cell(100, 6, limpiar_texto_pdf(f"  {p}"), 1, 0, "L", fill=True)
    pdf.cell(50, 6, limpiar_texto_pdf(f"{q}"), 1, 0, "C", fill=True)
    pdf.cell(40, 6, "R$ ________", 1, 1, "C", fill=True)
    fill_toggle = not fill_toggle

  tmp_dir = tempfile.gettempdir()
  nome_arquivo_pdf = f"pedido_{codigo_pedido.replace('/', '_').replace('#', '').strip()}.pdf"
  pdf_path = os.path.join(tmp_dir, nome_arquivo_pdf)
  pdf.output(pdf_path)

  # Converte o PDF em Base64 para enviar via JSON para o Make
  with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

  # Dispara para o Make com os dados e o PDF embutido
  webhook_url = os.environ.get("WEBHOOK_MAKE_URL", "")
  if not webhook_url:
    return False, "WEBHOOK_MAKE_URL não configurada no Render."

  payload = {
      "codigo": codigo_pedido,
      "cliente": nome_cliente,
      "observacao": obs_cliente,
      "itens": carrinho,
      "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
      "pdf_base64": pdf_base64,
      "pdf_nome": nome_arquivo_pdf,
  }

  try:
    response = requests.post(webhook_url, json=payload, timeout=15)
    if response.status_code == 200:
      return True, codigo_pedido
    else:
      return (
          False,
          f"Erro no Make (Status {response.status_code}): {response.text}",
      )
  except Exception as e:
    return False, str(e)


@app.route("/webhook-whatsapp", methods=["POST"])
def receber_mensagem():
  try:
    dados = request.get_json(silent=True)
    if not dados:
      return jsonify({"status": "erro", "detalhe": "JSON inválido ou ausente"}), 200

    remetente = str(dados.get("telefone", ""))

    if NUMERO_AUTORIZADO not in remetente:
      return jsonify({"status": "ignorado", "motivo": "Número não autorizado"}), 200

    texto = dados.get("mensagem", "")
    if not texto:
      return jsonify({"status": "erro", "detalhe": "Campo mensagem não encontrado"}), 200

    sucesso, msg_retorno = interpretar_e_gerar_pedido(texto, remetente)
    if sucesso:
      return jsonify({"status": "sucesso", "pedido": msg_retorno}), 200
    else:
      return jsonify({"status": "erro", "detalhe": msg_retorno}), 200
  except Exception as e:
    return jsonify({"status": "erro_critico", "detalhe": str(e)}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
