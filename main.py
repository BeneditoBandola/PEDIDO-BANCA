import os
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
  return jsonify({"status": "ok", "mensagem": "Servidor online e operando!"})


@app.route("/webhook-whatsapp", methods=["POST"])
def webhook():
  try:
    dados = request.get_json(silent=True)
    if not dados:
      return jsonify({"status": "erro", "detalhe": "JSON vazio ou inválido"}), 200
    return jsonify({"status": "sucesso", "recebido": dados}), 200
  except Exception as e:
    return jsonify({"status": "erro_critico", "detalhe": str(e)}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
