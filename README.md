🍕 Pizza Ordering System

Ce projet est un système de commande de pizzas en temps réel, développé avec Django (backend), React (frontend), Kafka (messaging) et WebSockets pour une mise à jour en temps réel.

🚀 Fonctionnalités

📌 Passer une commande de pizza avec suivi en direct.

🔄 Mise à jour en temps réel des statuts de commande via WebSockets.

📊 Dashboard dynamique avec affichage des métriques (commandes, recettes, stock).

🛠️ Kafka pour la gestion des événements liés aux commandes.

📡 Intégration PostgreSQL pour stocker les données de manière fiable.

🏗️ Architecture

Frontend : React, WebSockets, Recharts (graphiques)

Backend : Django, Django REST Framework, Django Channels

Messaging : Apache Kafka

Base de données : PostgreSQL

📦 Installation & Setup

1️⃣ Prérequis

Python 3.8+

Node.js & npm

PostgreSQL

Apache Kafka

2️⃣ Installation du backend

Cloner le projet :

git clone <URL_DU_DEPOT>
cd <nom_du_dossier>

Créer un environnement virtuel et l'activer :

python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

Installer les dépendances :

pip install -r requirements.txt

Configurer la base de données :

Modifier settings.py pour inclure les infos de connexion PostgreSQL.

Appliquer les migrations :

python manage.py migrate

Lancer le serveur Django :

python manage.py runserver

3️⃣ Installation du frontend

Aller dans le dossier frontend :

cd frontend

Installer les dépendances :

npm install

Lancer le serveur React :

npm start

4️⃣ Lancer Kafka & les consommateurs

Assurez-vous que Kafka est installé et fonctionne sur votre machine.

Lancer les consommateurs Kafka pour la mise à jour des commandes.

📊 Utilisation

Commande d'une pizza depuis l'interface.

Suivi en temps réel du statut de la commande.

Visualisation des métriques sur le dashboard (nombre de commandes, recettes, stock).

🛠️ Développement & Tests

Tester les commandes via Postman ou curl.

Simuler des commandes avec des dates personnalisées si nécessaire.

Vérifier les logs Kafka pour s'assurer du bon fonctionnement du messaging.

📜 Technologies utilisées

Backend : Django, Django REST Framework, Django Channels

Frontend : React, WebSockets, Recharts

Base de données : PostgreSQL

Messaging : Apache Kafka

Serveur en temps réel : WebSockets via Django Channels

📄 Licence

Ce projet est réalisé dans un cadre éducatif.

🚀 Bon développement et bonne dégustation de pizzas ! 🍕
