import json
import time
import paho.mqtt.client as paho
from paho import mqtt

# Dados HiveMQ Cloud
broker = "1513bd8554204d70ace5ca47bae8225b.s1.eu.hivemq.cloud"
port = 8883
username = "hydrosmartapp"
password = "Hydrosmartapp01"
topic = "topico-esp23-app-comunicacao-nivel"
statusAtualSolenoide = 0
centimetros_mock = [31.9,30.1,28.3,26.5,24.7,22.9,21.1,19.3,17.5,15.7,13.9,12.1,10.3,8.5,6.7,4.9,3.1,1.3,0.9,0.5]

# Callback de conexão
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado ao broker MQTT!")
        client.subscribe(topic, qos=1)
    else:
        print("Falha na conexão, código:", rc)

# Callback de mensagem recebida
def on_message(client, userdata, msg):
    global statusAtualSolenoide
    print("Mensagem recebida:", msg.payload.decode())
    try:
        body = json.loads(msg.payload.decode())
        print("JSON parseado:", body)
        if body.get("origem") == "APP":
            if body.get("comando") == 1:
                statusAtualSolenoide = 1
                print("Comando para LIGAR solenoide recebido.")
            else:
                statusAtualSolenoide = 0
                print("Comando para DESLIGAR solenoide recebido.")
    except json.JSONDecodeError:
        print("Mensagem não é JSON válido.")

# Criação do cliente MQTT com protocolo v5
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)

client.on_connect = on_connect
client.on_message = on_message

# Configuração TLS
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(username, password)

# Conectar ao broker
client.connect(broker, port)

# Iniciar o loop de processamento
client.loop_start()

# Simular envio periódico de dados
try:
    index = 0
    while True:
        if statusAtualSolenoide == 1:
            centimetros = centimetros_mock[index]
            body = {
                "centimetros": centimetros,
                "origem": "ESP",
                "statusSolenoide": statusAtualSolenoide,
                "comando": -1
            }
            payload = json.dumps(body)
            client.publish(topic, payload=payload, qos=1)
            print("Mensagem enviada:", payload)
            if (index + 1) < len(centimetros_mock):
                index += 1
        else:
            centimetros = centimetros_mock[index]
            body = {
                "centimetros": centimetros,
                "origem": "ESP",
                "statusSolenoide": statusAtualSolenoide,
                "comando": -1
            }

            payload = json.dumps(body)
            client.publish(topic, payload=payload, qos=1)
            print("Mensagem enviada:", payload)

        print("Domindo ...")
        time.sleep(3)

except KeyboardInterrupt:
    print("Finalizando...")
    client.loop_stop()
    client.disconnect()
