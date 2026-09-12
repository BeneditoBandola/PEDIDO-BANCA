from datetime import datetime, timedelta, timezone
import json
import os
import re
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

ARQUIVO_HISTORICO = "historico_pedidos.json"
NUMERO_AUTORIZADO = "3598464384"

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
    "COUVE": ["couve", "maço de couve", "maços de couve", "maco de couve"],
    "COUVE-FLOR": ["couve flor", "couve-flor", "couveflor"],
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
    "ERVILHA DEBULHADA CONGELADA": [
        "ervilha",
        "ervlha",
        "ervilha congelada",
        "ervilha debulhada",
    ],
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

    if (
        linha_inf.startswith("obs:")
        or linha_inf.startswith("observacao:")
        or linha_inf.startswith("observação:")
    ):
      limpo = re.sub(
          r"obs(ervacao|erenação)?[:\s\-]*",
          "",
          linha_original,
          flags=re.IGNORECASE,
      )
      if limpo.strip():
        observacoes_encontradas.append(limpo.strip())
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
      ignorar = [
          "bom dia",
          "boa tarde",
          "boa noite",
          "pedido p hj",
          "pedido para hoje",
          "segue o pedido",
      ]
      if any(ign in linha_inf for ign in ignorar):
        continue

      if len(linha_inf) > 8 and not any(char.isdigit() for char in linha_inf):
        observacoes_encontradas.append(linha_original)

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

  numero_sequencial = len(dados_existentes) + 1
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


# Rota Principal (Novo Pedido)
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
        <title>Banca do Mané - Novo Pedido</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 720px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; }
            .nav { text-align: center; margin-bottom: 25px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
            .nav a { background: #34495e; color: white; padding: 7px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; }
            .nav a:hover { background: #2c3e50; }
            .nav a.ativo { background: #27ae60; }
            label { font-weight: bold; display: block; margin-top: 15px; margin-bottom: 5px; }
            input[type="text"], textarea { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
            textarea { height: 160px; resize: vertical; }
            button { background-color: #27ae60; color: white; border: none; padding: 14px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 20px; font-weight: bold; }
            button:hover { background-color: #219653; }
            .alert { padding: 15px; margin-top: 20px; border-radius: 4px; text-align: center; font-weight: bold; }
            .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🥬 Banca do Mané</h2>
            <div class="nav">
                <a href="/" class="ativo">Novo Pedido</a>
                <a href="/historico">📜 Histórico</a>
                <a href="/clientes" style="background: #8e44ad;">👥 Clientes</a>
                <a href="/relatorio" style="background: #2980b9;">📊 Frequência</a>
                <a href="/volume" style="background: #d35400;">📈 Volume Vendido</a>
            </div>
            <form method="POST">
                <label for="cliente">Nome do Cliente / Telefone:</label>
                <input type="text" id="cliente" name="cliente" value="Cliente Balcão" required>

                <label for="mensagem">Cole a mensagem do pedido aqui:</label>
                <textarea id="mensagem" name="mensagem" placeholder="Ex:&#10;3 dz de limão&#10;2 cx de tomate salada&#10;obs: entrega urgente" required></textarea>

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


# Rota do Histórico
@app.route("/historico", methods=["GET"])
def historico():
  historico_pedidos = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        historico_pedidos = json.load(f)
        historico_pedidos.reverse()
    except:
      historico_pedidos = []

  html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Banca do Mané - Histórico</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 720px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; }
            .nav { text-align: center; margin-bottom: 25px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
            .nav a { background: #34495e; color: white; padding: 7px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; }
            .nav a:hover { background: #2c3e50; }
            .nav a.ativo { background: #27ae60; }
            details { background: #fafafa; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 12px; padding: 12px 15px; cursor: pointer; }
            summary { font-weight: bold; color: #2980b9; outline: none; font-size: 15px; display: flex; justify-content: space-between; align-items: center; }
            summary span.data { color: #666; font-weight: normal; font-size: 12px; }
            .pedido-obs { color: #c0392b; font-size: 13px; margin: 10px 0; border-top: 1px dashed #eee; padding-top: 8px; }
            ul { margin: 8px 0 0 20px; padding: 0; font-size: 14px; color: #444; }
            li { padding: 3px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📜 Histórico de Pedidos</h2>
            <div class="nav">
                <a href="/">Novo Pedido</a>
                <a href="/historico" class="ativo">Histórico</a>
                <a href="/clientes" style="background: #8e44ad;">👥 Clientes</a>
                <a href="/relatorio" style="background: #2980b9;">📊 Frequência</a>
                <a href="/volume" style="background: #d35400;">📈 Volume Vendido</a>
            </div>

            {% if historico_pedidos %}
                {% for p in historico_pedidos %}
                    <details>
                        <summary>
                            <span>{{ p.codigo }} — {{ p.cliente }}</span>
                            <span class="data">{{ p.data_hora }}</span>
                        </summary>
                        <div class="pedido-obs"><strong>Observação:</strong> {{ p.observacao }}</div>
                        <ul>
                            {% for prod, qtd in p.itens.items() %}
                                <li><strong>{{ qtd }}</strong> — {{ prod }}</li>
                            {% endfor %}
                        </ul>
                    </details>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #777;">Nenhum pedido registrado até o momento.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
  return render_template_string(
      html_template, historico_pedidos=historico_pedidos
  )


# Rota de Melhores Clientes
@app.route("/clientes", methods=["GET"])
def clientes():
  dados_pedidos = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_pedidos = json.load(f)
    except:
      dados_pedidos = []

  ranking_clientes = {}
  for p in dados_pedidos:
    cliente = str(p.get("cliente", "Cliente Desconhecido")).strip()
    if not cliente:
      cliente = "Cliente Desconhecido"
    if cliente not in ranking_clientes:
      ranking_clientes[cliente] = {"total_pedidos": 0, "ultimo_pedido": ""}
    ranking_clientes[cliente]["total_pedidos"] += 1
    ranking_clientes[cliente]["ultimo_pedido"] = p.get("data_hora", "")

  clientes_ordenados = sorted(
      ranking_clientes.items(),
      key=lambda x: x[1]["total_pedidos"],
      reverse=True,
  )

  html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Banca do Mané - Melhores Clientes</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 720px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; }
            .nav { text-align: center; margin-bottom: 25px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
            .nav a { background: #34495e; color: white; padding: 7px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; }
            .nav a:hover { background: #2c3e50; }
            .nav a.ativo { background: #27ae60; }
            table { width: 100%%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
            th { background-color: #2c3e50; color: white; }
            tr:hover { background-color: #f1f1f1; }
            .pos { font-weight: bold; color: #8e44ad; width: 40px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>👥 Ranking de Melhores Clientes</h2>
            <div class="nav">
                <a href="/">Novo Pedido</a>
                <a href="/historico">📜 Histórico</a>
                <a href="/clientes" class="ativo" style="background: #8e44ad;">👥 Clientes</a>
                <a href="/relatorio" style="background: #2980b9;">📊 Frequência</a>
                <a href="/volume" style="background: #d35400;">📈 Volume Vendido</a>
            </div>

            {% if clientes_ordenados %}
                <table>
                    <thead>
                        <tr>
                            <th style="text-align: center;">#</th>
                            <th>Cliente / Nome</th>
                            <th style="text-align: center;">Total de Pedidos</th>
                            <th style="text-align: center;">Última Compra</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cli, info in clientes_ordenados %}
                            <tr>
                                <td class="pos">{{ loop.index }}º</td>
                                <td><strong>{{ cli }}</strong></td>
                                <td style="text-align: center;">{{ info.total_pedidos }}</td>
                                <td style="text-align: center; color: #666; font-size: 12px;">{{ info.ultimo_pedido }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="text-align: center; color: #777; margin-top: 20px;">Nenhum cliente registrado ainda.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
  return render_template_string(
      html_template, clientes_ordenados=clientes_ordenados
  )


# Rota do Relatório de Frequência
@app.route("/relatorio", methods=["GET"])
def relatorio():
  data_filtro = request.args.get("data", "")
  dados_pedidos = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_pedidos = json.load(f)
    except:
      dados_pedidos = []

  if data_filtro:
    dados_pedidos = [
        p
        for p in dados_pedidos
        if str(p.get("data_hora", "")).startswith(data_filtro)
    ]

  ranking_produtos = {}
  total_pedidos = len(dados_pedidos)

  for p in dados_pedidos:
    itens = p.get("itens", {})
    for produto, qtd_str in itens.items():
      if produto not in ranking_produtos:
        ranking_produtos[produto] = {"frequencia_pedidos": 0}
      ranking_produtos[produto]["frequencia_pedidos"] += 1

  ranking_ordenado = sorted(
      ranking_produtos.items(),
      key=lambda x: x[1]["frequencia_pedidos"],
      reverse=True,
  )

  html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Banca do Mané - Relatório de Frequência</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 720px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; }
            .nav { text-align: center; margin-bottom: 25px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
            .nav a { background: #34495e; color: white; padding: 7px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; }
            .nav a:hover { background: #2c3e50; }
            .nav a.ativo { background: #27ae60; }
            .filter-box { background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
            .filter-box input[type="date"] { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
            .filter-box button, .filter-box a.btn-limpar { padding: 8px 14px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: bold; cursor: pointer; border: none; }
            .filter-box button { background: #27ae60; color: white; }
            .filter-box button:hover { background: #219653; }
            .filter-box a.btn-limpar { background: #e74c3c; color: white; display: inline-block; }
            .filter-box a.btn-limpar:hover { background: #c0392b; }
            .stats-card { background: #e8f4fd; border: 1px solid #bbe1fa; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 20px; font-size: 15px; color: #1d6fa5; font-weight: bold; }
            table { width: 100%%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
            th { background-color: #2c3e50; color: white; }
            tr:hover { background-color: #f1f1f1; }
            .pos { font-weight: bold; color: #2980b9; width: 40px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Relatório de Frequência de Produtos</h2>
            <div class="nav">
                <a href="/">Novo Pedido</a>
                <a href="/historico">📜 Histórico</a>
                <a href="/clientes" style="background: #8e44ad;">👥 Clientes</a>
                <a href="/relatorio" class="ativo" style="background: #2980b9;">📊 Frequência</a>
                <a href="/volume" style="background: #d35400;">📈 Volume Vendido</a>
            </div>

            <form method="GET" class="filter-box">
                <div>
                    <label for="data" style="font-size: 13px; margin-bottom: 3px; display: inline-block;">Filtrar por Data:</label>
                    <input type="date" id="data" name="data" value="{{ data_filtro }}">
                </div>
                <div style="display: flex; gap: 8px; align-items: flex-end;">
                    <button type="submit">Filtrar</button>
                    {% if data_filtro %}
                        <a href="/relatorio" class="btn-limpar">Limpar Filtro</a>
                    {% endif %}
                </div>
            </form>

            <div class="stats-card">
                Total de Pedidos no Período: {{ total_pedidos }}
            </div>

            {% if ranking_ordenado %}
                <table>
                    <thead>
                        <tr>
                            <th style="text-align: center;">#</th>
                            <th>Produto</th>
                            <th style="text-align: center;">Vezes Pedido</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for prod, info in ranking_ordenado %}
                            <tr>
                                <td class="pos">{{ loop.index }}º</td>
                                <td><strong>{{ prod }}</strong></td>
                                <td style="text-align: center;">{{ info.frequencia_pedidos }} pedidos</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="text-align: center; color: #777; margin-top: 20px;">Nenhum dado encontrado para a data selecionada.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
  return render_template_string(
      html_template,
      total_pedidos=total_pedidos,
      ranking_ordenado=ranking_ordenado,
      data_filtro=data_filtro,
  )


# Rota de Volume Vendido com Gráficos e Filtro por Data
@app.route("/volume", methods=["GET"])
def volume():
  data_filtro = request.args.get("data", "")
  dados_pedidos = []
  if os.path.exists(ARQUIVO_HISTORICO):
    try:
      with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        dados_pedidos = json.load(f)
    except:
      dados_pedidos = []

  if data_filtro:
    dados_pedidos = [
        p
        for p in dados_pedidos
        if str(p.get("data_hora", "")).startswith(data_filtro)
    ]

  # Dicionário para somar quantidades agrupadas por unidade de medida (KG, Caixa, Unidade, etc.)
  # Ex: {"BATATA LAVADA": {"KG": 45.0, "Unidades": 0}, ...}
  totais_produtos = {}

  for p in dados_pedidos:
    itens = p.get("itens", {})
    for produto, qtd_str in itens.items():
      if produto not in totais_produtos:
        totais_produtos[produto] = {}

      # Extrai o número e a unidade da string armazenada (ex: "5 KG" -> num=5.0, unidade="KG")
      match = re.search(r"([\d\.,]+)\s*(.*)", qtd_str)
      if match:
        num_str = match.group(1).replace(",", ".")
        unidade = match.group(2).strip().upper()
        try:
          valor = float(num_str)
        except:
          valor = 1.0

        if unidade not in totais_produtos[produto]:
          totais_produtos[produto][unidade] = 0.0
        totais_produtos[produto][unidade] += valor

  # Formata os dados para exibir na tabela e passar para o gráfico
  tabela_volume = []
  for prod, unidades in totais_produtos.items():
    resumo_partes = []
    total_principal = 0
    unidade_principal = ""
    for un, val in unidades.items():
      # Formata bonito (sem .0 desnecessário se for inteiro)
      val_fmt = int(val) if val.is_integer() else val
      resumo_partes.append(f"{val_fmt} {un}")
      total_principal = val_fmt
      unidade_principal = un

    tabela_volume.append({
        "produto": prod,
        "resumo": " + ".join(resumo_partes),
        "total_num": total_principal,
        "unidade": unidade_principal,
    })

  # Ordena pelo maior volume numérico
  tabela_volume = sorted(
      tabela_volume, key=lambda x: x["total_num"], reverse=True
  )

  # Prepara dados para o gráfico (Top 10 produtos)
  top_10 = tabela_volume[:10]
  labels_grafico = [item["produto"] for item in top_10]
  valores_grafico = [item["total_num"] for item in top_10]

  html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Banca do Mané - Volume Vendido</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; background: #fff; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #2c3e50; text-align: center; }
            .nav { text-align: center; margin-bottom: 25px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
            .nav a { background: #34495e; color: white; padding: 7px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; }
            .nav a:hover { background: #2c3e50; }
            .nav a.ativo { background: #27ae60; }
            .filter-box { background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
            .filter-box input[type="date"] { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
            .filter-box button, .filter-box a.btn-limpar { padding: 8px 14px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: bold; cursor: pointer; border: none; }
            .filter-box button { background: #d35400; color: white; }
            .filter-box button:hover { background: #ba4a00; }
            .filter-box a.btn-limpar { background: #e74c3c; color: white; display: inline-block; }
            .filter-box a.btn-limpar:hover { background: #c0392b; }
            .chart-container { position: relative; margin: 30px 0; height: 350px; width: 100%%; }
            table { width: 100%%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }
            th { background-color: #2c3e50; color: white; }
            tr:hover { background-color: #f1f1f1; }
            .pos { font-weight: bold; color: #d35400; width: 40px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📈 Relatório de Volume Vendido (Quilos, Caixas e Unidades)</h2>
            <div class="nav">
                <a href="/">Novo Pedido</a>
                <a href="/historico">📜 Histórico</a>
                <a href="/clientes" style="background: #8e44ad;">👥 Clientes</a>
                <a href="/relatorio" style="background: #2980b9;">📊 Frequência</a>
                <a href="/volume" class="ativo" style="background: #d35400;">📈 Volume Vendido</a>
            </div>

            <form method="GET" class="filter-box">
                <div>
                    <label for="data" style="font-size: 13px; margin-bottom: 3px; display: inline-block;">Filtrar por Data:</label>
                    <input type="date" id="data" name="data" value="{{ data_filtro }}">
                </div>
                <div style="display: flex; gap: 8px; align-items: flex-end;">
                    <button type="submit">Filtrar Volume</button>
                    {% if data_filtro %}
                        <a href="/volume" class="btn-limpar">Limpar Filtro</a>
                    {% endif %}
                </div>
            </form>

            {% if tabela_volume %}
                <!-- Gráfico Visual -->
                <div class="chart-container">
                    <canvas id="graficoVolume"></canvas>
                </div>

                <h3>Detalhamento Completo</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="text-align: center;">#</th>
                            <th>Produto</th>
                            <th>Volume Total Consolidado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in tabela_volume %}
                            <tr>
                                <td class="pos">{{ loop.index }}º</td>
                                <td><strong>{{ item.produto }}</strong></td>
                                <td>{{ item.resumo }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="text-align: center; color: #777; margin-top: 30px;">Nenhum volume registrado para o período selecionado.</p>
            {% endif %}
        </div>

        <script>
            const labelsData = {{ labels_grafico | tojson }};
            const valoresData = {{ valores_grafico | tojson }};

            if (labelsData.length > 0) {
                const ctx = document.getElementById('graficoVolume').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labelsData,
                        datasets: [{
                            label: 'Volume dos Principais Produtos',
                            data: valoresData,
                            backgroundColor: 'rgba(211, 84, 0, 0.7)',
                            borderColor: 'rgba(211, 84, 0, 1)',
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 }
                            }
                        }
                    }
                });
            }
        </script>
    </body>
    </html>
    """
  return render_template_string(
      html_template,
      tabela_volume=tabela_volume,
      labels_grafico=labels_grafico,
      valores_grafico=valores_grafico,
      data_filtro=data_filtro,
  )


@app.route("/webhook-whatsapp", methods=["POST"])
def receber_mensagem():
  try:
    dados = request.get_json(silent=True)
    if not dados:
      return jsonify({"status": "erro", "detalhe": "JSON inválido"}}, 200
    remetente = str(dados.get("telefone", ""))
    if NUMERO_AUTORIZADO not in remetente:
      return jsonify({"status": "ignorado"}}, 200
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
