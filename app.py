from flask import Flask, render_template
import os

# Importar blueprints
from routes.email_routes import email_bp
from routes.document_routes import document_bp
from routes.context_routes import context_bp
from routes.chat_routes import chat_bp

app = Flask(__name__)
# Crear directorio para contextos guardados si no existe
if not os.path.exists('contextos_guardados'):
    os.makedirs('contextos_guardados')

# Registrar blueprints
app.register_blueprint(email_bp)
app.register_blueprint(document_bp)
app.register_blueprint(context_bp)
app.register_blueprint(chat_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)