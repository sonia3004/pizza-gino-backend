from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'commande_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("En attente des événements...")

for message in consumer:
    print(f"Commande reçue: {message.value}")
