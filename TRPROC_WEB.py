import sys
import os

# Adiciona o diretório principal do TRPROC ao sys.path para conseguirmos importar models e config!
MAIN_PROJECT_DIR = r"C:\xampp\htdocs\trproc-main-trproc"
if MAIN_PROJECT_DIR not in sys.path:
    sys.path.insert(0, MAIN_PROJECT_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente (usando o .env do projeto principal)
load_dotenv(os.path.join(MAIN_PROJECT_DIR, ".env"))

app = Flask(__name__)
CORS(app)

# Configurações do Banco de Dados
# Usa o mesmo banco do projeto principal
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/trproc')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_super_secret')

# Inicializa o banco (usando a instância do db do projeto principal, se necessário)
from models.db import db
db.init_app(app)

# Registra a rota do Test Hub
from routes.tester import tester_bp
app.register_blueprint(tester_bp, url_prefix='/dev/tester')

@app.route('/')
def index():
    return "IA Admin Toolkit - TRPROC LicitaPRO (Running on Port 5001)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
