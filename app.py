import firebase_admin
import serial
import threading
import time
import random

# pyrefly: ignore [missing-import]
import firebase_admin
# pyrefly: ignore [missing-import]
from firebase_admin import credentials
# pyrefly: ignore [missing-import]
from firebase_admin import firestore
# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, render_template_string

cred = credentials.Certificate("arduino_service.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

dados_sensor = {
    "umidade": 0, 
    "timestamp": firestore.SERVER_TIMESTAMP 
    }
PORTA_SERIAL = 'COM5' 
BAUD_RATE = 9600
INTERVALO_SALVAMENTO = 10
UMIDADE_RISCO = 800
UMIDADE_EXCESSO = 400

umidade_atual = 0.0

def salvar_no_firebase(umidade_atual):
    try:
        db.collection("leituras").add({
            "umidade": umidade_atual,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        print(f"Dado transferido para o Firebase Firestore={umidade_atual}")
    except Exception as e:
        print(f"Erro ao salvar no Firebase Firestore: {e}")

def ler_porta_serial():
    global dados_sensor, umidade_atual
    ultimo_salvamento = 0

    while True:
        try:
            ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"Conectado ao Arduino na porta {PORTA_SERIAL}")
            
            while True:
                if ser.in_waiting > 0:
                    linha = ser.readline().decode('utf-8').strip()
                    
                    if "Umidade: " in linha:
                        try:
                            valor_str = linha.split("Umidade: ")[1].strip()
                            umidade_atual = float(valor_str)
                            dados_sensor["umidade"] = umidade_atual
                            dados_sensor["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S')

                            agora = time.time()
                            if agora - ultimo_salvamento >= INTERVALO_SALVAMENTO:
                                if umidade_atual > UMIDADE_RISCO:
                                    salvar_no_firebase(UMIDADE_RISCO)
                                elif umidade_atual < UMIDADE_EXCESSO:
                                    salvar_no_firebase(UMIDADE_EXCESSO)
                                else:
                                    salvar_no_firebase(umidade_atual)
                        except ValueError:
                            pass
                else:
                    time.sleep(0.1)
        except Exception as e:
            print(f'Erro na comunicação Serial: {e}')
            print('Verifique se a porta está correta ou se o monitor serial da IDE não está aberto.')
            time.sleep(5)
            print("Tentando Reconectar...")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor de Umidade do Solo</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background-color: #f4f4f9; padding-top: 100px; }
        .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; min-width: 300px; }
        h1 { color: #333; margin-top: 0;}
        .valor { font-size: 5em; font-weight: bold; color: #0078D7; }
        .unidade { font-size: 0.3em; color: #666; }
        .status { font-size: 1.8em; font-weight: bold; margin-top: 20px; transition: color 0.3s ease; }
        .status.seco { color: #d9534f; }
        .status.umido { color: #0275d8; }
        .status.normal { color: #5cb85c; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Umidade Atual (ADC)</h1>
        <div class="valor" id="umidade-display">--</div>
        <div class="status" id="status-display">--</div>
    </div>

    <script>
        // Função que bate na API do Flask e atualiza o DOM a cada 500ms
        function buscarUmidade() {
            fetch('/api/dados')
                .then(response => response.json())
                .then(data => {
                    const umidade = data.umidade;
                    document.getElementById('umidade-display').innerHTML = umidade.toFixed(0);
                    
                    const statusDisplay = document.getElementById('status-display');
                    if (umidade >= 800) {
                        statusDisplay.innerHTML = "Solo Seco";
                        statusDisplay.className = "status seco";
                    } else if (umidade <= 400) {
                        statusDisplay.innerHTML = "Solo Muito Úmido";
                        statusDisplay.className = "status umido";
                    } else {
                        statusDisplay.innerHTML = "Solo Normal";
                        statusDisplay.className = "status normal";
                    }
                })
                .catch(error => console.error('Erro de conexão:', error));
        }

        setInterval(buscarUmidade, 500);
        buscarUmidade(); 
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dados')
def api_dados():
    return jsonify(dados_sensor)

if __name__ == '__main__':
    thread_arduino = threading.Thread(target=ler_porta_serial, daemon=True)
    thread_arduino.start()

    print("Iniciando servidor web na porta 8080...")
    app.run(host='0.0.0.0', port=8080)
