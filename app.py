import os

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import folium

# Inicia o aplicativo Flask e configura o banco de dados
app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Obtém o caminho absoluto do diretório onde o app.py está
basedir = os.path.abspath(os.path.dirname(__file__))
# Define o caminho da pasta database
db_folder = os.path.join(basedir, 'database')
# Cria a pasta database se ela não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Configura a URL do banco de dados usando o caminho absoluto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_folder, 'pontos_alerta.db')
db = SQLAlchemy(app)


# Cria a tabela 'PontoAlerta' que vai armazenar os dados dos pontos
class PontoAlerta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Coluna para o tipo de alerta (ex: alagamento, deslizamento)
    tipo = db.Column(db.String(50), nullable=False)
    # Coluna para a descrição do problema
    descricao = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<PontoAlerta {self.tipo}>'


# carrega a página com o mapa
@app.route('/')
def home():
    # Renderiza o template index.html
    return render_template('index.html')

#carregar os pontos existentes no mapa (usado pelo JavaScript)
@app.route('/api/pontos_alerta', methods=['GET'])
def get_pontos():
    # Busca todos os pontos do banco de dados
    pontos = PontoAlerta.query.all()
    # Converte a lista de objetos para um formato JSON que o JavaScript entende
    pontos_json = [{
        'id': p.id,
        'tipo': p.tipo,
        'descricao': p.descricao,
        'latitude': p.latitude,
        'longitude': p.longitude
    } for p in pontos]
    return jsonify(pontos_json)

#salvar um novo ponto no banco de dados (usado pelo JavaScript)
@app.route('/api/salvar_ponto', methods=['POST'])
def salvar_ponto():
    dados = request.get_json()
    novo_ponto = PontoAlerta(
        tipo=dados['tipo'],
        descricao=dados['descricao'],
        latitude=dados['latitude'],
        longitude=dados['longitude']
    )
    # Adiciona o novo ponto à sessão do banco de dados
    db.session.add(novo_ponto)

    db.session.commit()

    return jsonify({'mensagem': 'Ponto salvo com sucesso!'}), 201

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    # Cria o banco de dados e as tabelas (se ainda não existirem)
    with app.app_context():
        db.create_all()
    # Inicia o servidor em modo de depuração (debug)
    app.run(debug=True)