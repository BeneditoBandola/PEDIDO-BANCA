from datetime import datetime
import json
import os
import re
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

ARQUIVO_HISTORICO = "historico_pedidos.json"
NUMERO_AUTORIZADO = "3598464384"


def interpretar_e_gerar_pedido(texto_wpp, nome_cliente="Cliente WhatsApp"):
  carrinho = {}
  linhas = texto_wpp.strip().split("\n")
  obs_cliente = "Nenhuma observação"

  for linha in linhas:
    linha_inf = linha.lower().strip()
    if not linha_inf:
      continue

    # Identifica se é saudação ou instrução inicial para tratar como observação real se necessário,
    # mas ignorando frases genéricas longas de "por favor separar"
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
      # Só guarda como observação se for uma instrução curta específica, senão ignora a saudação pura
      if len(linha_inf) > 15 and not any(
          termo in linha_inf
          for term in ["separar", "pedido", "entrega", "urgente"]
      ):
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

  texto_itens_formatado = ""
  for produto, qtd in carrinho.items():
    texto_itens_formatado += f"• {qtd} - {produto}\n"

  novo_pedido = {
      "codigo": codigo_pedido,
      "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "cliente": nome_cliente,
      "observacao": obs_cliente,
      "itens": carrinho,
  }
  dados_existentes.append(novo_pedido)
  with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
    json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

  webhook_url = os.environ.get("WEBHOOK_MAKE_URL", "")
  if not webhook_url:
    return False, "WEBHOOK_MAKE_URL não configurada no Render."

  payload = {
      "codigo": codigo_pedido,
      "cliente": nome_cliente,
      "observacao": obs_cliente,
      "itens": texto_itens_formatado.strip(),
      "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
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
      return jsonify({"status": "erro", "detalhe": "JSON inválido"}), 200
    remetente = str(dados.get("telefone", ""))
    if NUMERO_AUTORIZADO not in remetente:
      return jsonify({"status": "ignorado"}), 200
    texto = dados.get("mensagem", "")
    sucesso, msg_retorno = interpretar_e_gerar_pedido(texto, remetente)
    if sucesso:
      return jsonify({"status": "sucesso", "pedido": msg_retorno}), 200
    else:
      return jsonify({"status": "erro", "detalhe": msg_retorno}), 200
  except Exception as e:
    return jsonify({"status": "erro_critico", "detalhe": str(e)}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
