from datetime import datetime, timedelta, timezone
import json
import os
import re
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

ARQUIVO_HISTORICO = "historico_pedidos.json"
NUMERO_AUTORIZADO = "3598464384"

# Fuso horário de Brasília (UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))

CATALOGO_PRODUTOS = {
    "BATATA LAVADA": ["batata", "batata lavada"],
    "TOMATE SALADA": ["tomate", "tomate salada"],
    "TOMATE CEREJA": ["tomate cereja", "cereja"],
    "ABACAXI PÉROLA": ["abacaxi", "abacaxi perola"],
    "CENOURA": ["cenoura"],
    "LIMÃO TAITI": ["limao", "limão", "limoes", "limões", "taiti"],
    "CEBOLA": ["cebola"],
    "ALHO": ["alho", "cabeca de alho", "cabeças de alho"],
    "MANDIOQUINHA": ["mandioquinha", "batata baroa"],
    "BETERRABA": ["beterraba"],
    "REPOLHO": ["repolho"],
    "COUVE": ["couve", "maco de couve", "maços de couve"],
    "COUVE-FLOR": ["couve flor", "couve-flor"],
    "MORANGO": ["morango", "morangos"],
    "MANGA PALMER": ["manga palmer", "palmer"],
    "MANGA TOMMY": ["manga tommy", "tommy", "manga"],
    "BANANA PRATA": ["banana", "banana prata", "dz de banana", "dúzia de banana"],
    "MAMÃO FORMOSA": ["mamao", "mamão", "mamao formosa", "mamão formosa"],
    "GOIABA": ["goiaba"],
    "PERA": ["pera", "pêra"],
    "MAÇÃ NACIONAL GALA": ["maca", "maçã", "maca gala", "maçã gala"],
    "SALSA": ["salsa", "salsinha"],
    "CHEIRO VERDE": ["cheiro verde", "cheiro-verde"],
    "AGRIÃO": ["agriao", "agrião"],
    "RÚCULA": ["rucula", "rúcula"],
    "PEPINO JAPONÊS": ["pepino", "pepino japones", "pepino japonês"],
    "JILÓ": ["jilo", "jiló"],
    "QUIABO": ["quiabo"],
    "ERVILHA DEBULHADA CONGELADA": ["ervilha", "ervilha congelada", "ervilha debulhada"],
    "UVA NIÁGARA": ["uva niagara", "niagara"],
    "UVA VITÓRIA": ["uva vitoria", "vitoria"],
    "UVA": ["uva", "uvas"],
    "MELANCIA": ["melancia", "melancias"],
}


def identificar_produto(linha_inf):
  for produto_oficial, sinonimos in CATALOGO_PRODUTOS.items():
    for sinonimo in sinonimos:
      if sinonimo in linha_inf:
        return produto_oficial
  return None


def interpretar_e_gerar_pedido(texto_wpp, nome_cliente="Cliente WhatsApp"):
  carrinho = {}
  linhas = texto_wpp.strip().split("\n")
  obs_cliente = "Nenhuma observação"
  observacoes_encontradas = []

  # Pega a data e hora atual ajustada para o horário de Brasília
  agora_brasilia = datetime.now(FUSO_BRASILIA)

  for linha in linhas:
    linha_original = linha.strip()
    linha_inf = linha_original.lower()
    if not linha_inf:
      continue

    produto_encontrado = identificar_produto(linha_inf)

    if produto_encontrado:
      nums = re.findall(r"\d+[\.,]?\d*", linha_inf)
      qtd_num = nums[0] if nums else "1"

      if any(u in linha_inf for u in ["dz", "duzia", "dúzia"]):
        q_str = (
            f"{qtd_num} Dúzia(s)"
            if float(qtd_num.replace(",", ".")) > 1
            else "Caixa com 12 (Dúzia)"
        )
      elif any(u in linha_inf for u in ["cx", "caixa"]):
        q_str = f"{qtd_num} Caixa(s)"
      elif any(u in linha_inf for u in ["k", "kg"]):
        q_str = f"{qtd_num} KG"
      elif any(u in linha_inf for u in ["pct", "pacote"]):
        q_str = f"{qtd_num} Pacote(s)"
      else:
        q_str = (
            f"{qtd_num} Unidade"
            if float(qtd_num.replace(",", ".")) == 1
            else f"{qtd_num} Unidades"
        )
      carrinho[produto_encontrado] = q_str
    else:
      if any(
          termo in linha_inf for termo in ["obs", "observacao", "observação", "teste"]
      ) or len(linha_inf) > 8:
        limpo = re.sub(
            r"obs(ervacao|erenação)?[:\s\-]*", "", linha_original, flags=re.IGNORECASE
        )
        if limpo.strip():
          observacoes_encontradas.append(limpo.strip())

  if observacoes_encontradas:
    obs_cliente = " - ".join(observacoes_encontradas)

  if not carrinho:
    return False, "Nenhum produto identificado."

  data_hoje = agora_brasilia.strftime("%d/%m/%Y")
  dados_existentes = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_existentes = json.load(f)
    except:
      dados_existentes = []

  # Filtra os pedidos do dia considerando a data de Brasília
  data_str_iso = agora_brasilia.strftime("%Y-%m-%d")
  pedidos_hoje = [
      p for p in dados_existentes if p.get("data_hora", "").startswith(data_str_iso)
  ]
  numero_sequencial = len(pedidos_hoje) + 1
  codigo_pedido = f"#{numero_sequencial:02d} / {data_hoje}"

  texto_itens_formatado = ""
  for produto, qtd in carrinho.items():
    texto_itens_formatado += f"• {qtd} - {produto}\n"

  novo_pedido = {
      "codigo": codigo_pedido,
      "data_hora": agora_brasilia.strftime("%Y-%m-%d %H:%M:%S"),
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
      "data": agora_brasilia.strftime("%d/%m/%Y %H:%M:%S"),
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
