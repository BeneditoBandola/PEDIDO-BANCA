from datetime import datetime, timedelta, timezone
import json
import os
import re
import requests
from flask import Flask, jsonify, render_template_string, request

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


def interpretar_e_gerar_pedido(texto_wpp, nome_cliente="Painel Manual"):
  carrinho = {}
  linhas = texto_wpp.strip().split("\n")
  obs_cliente = "Nenhuma observação"
  observacoes_encontradas = []

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
    return False, "Nenhum produto identificado na mensagem."

  data_hoje = agora_brasilia.strftime("%d/%m/%Y")
  dados_existentes = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_existentes = json.load(f)
    except:
      dados_existentes = []

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


# Rota da Página Web (Painel Manual)
@app.route("/", methods=["GET", "POST"])
def index():
  mensagem_status = None
  sucesso_status = False
  if request.method == "POST":
    texto_pedido = request.form.get("mensagem", "")
    nome_cliente_input = request.form.get("cliente", "Painel Manual")
    if texto_pedido.strip():
      sucesso_status, mensagem_status = interpretar_e_gerar_pedido(
          texto_pedido, nome_cliente_input
      )

  html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Banca do Mané - Processador de Pedidos</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 600px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
            label { font-weight: bold; display: block; margin-top: 15px; margin-bottom: 5px; }
            input[type="text"], textarea { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
            textarea { height: 180px; resize: vertical; }
            button { background-color: #27ae60; color: white; border: none; padding: 14px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 20px; font-weight: bold; }
            button:hover { background-color: #219653; }
            .alert { padding: 15px; margin-top: 20px; border-radius: 4px; text-align: center; font-weight: bold; }
            .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🥬 Banca do Mané - Gerador de Pedidos</h2>
            <form method="POST">
                <label for="cliente">Nome do Cliente / Telefone:</label>
                <input type="text" id="cliente" name="cliente" value="Cliente Balcão / WhatsApp" required>

                <label for="mensagem">Cole a mensagem do pedido aqui:</label>
                <textarea id="mensagem" name="mensagem" placeholder="Ex:&#10;3 kg de batata lavada&#10;2 cx de tomate salada&#10;obs: entrega urgente" required></textarea>

                <button type="submit">Processar e Enviar Pedido por E-mail</button>
            </form>

            {% if mensagem_status %}
                {% if sucesso_status %}
                    <div class="alert alert-success">Pedido gerado e enviado com sucesso! Código: {{ mensagem_status }}</div>
                {% else %}
                    <div class="alert alert-error">Erro ao processar: {{ mensagem_status }}</div>
                {% endif %}
            {% endif %}
        </div>
    </body>
    </html>
    """
  return render_template_string(
      html_template,
      mensagem_status=mensagem_status,
      sucesso_status=sucesso_status,
  )


# Rota antiga de Webhook mantida funcionando 100%
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
