import redis
import json
import requests

# On configure Redis
redis_host = 'localhost'  # Nom du service Redis dans Docker Compose ou 'localhost' si exécuté en local
redis_port = 6379
redis_db = 0

# On configure le webhook Teams
teams_webhook_url = "urldevotrwebhookteams"

# Connexion à Redis
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# On recupere tous les incidents dans redis
for key in r.keys("incident:*"):
    incident_data = json.loads(r.get(key))

    # Si notif_send est false on envoie un message dans Teams
    if not incident_data.get("notif_send", False):
        message = {
            "title": f"Notification d'Incident: {incident_data['Incident']}",
            "text": (
                f"**Titre**: {incident_data['Titre']}\n"
                f"**Agent**: {incident_data['Agent']}\n"
                f"**Échéance TTO**: {incident_data['Échéance TTO']}\n"
                f"**Échéance TTR**: {incident_data['Échéance TTR']}\n"
            )
        }

        # Envoyer le message au webhook Teams
        response = requests.post(teams_webhook_url, headers={'Content-Type': 'application/json'}, data=json.dumps(message))
        
        if response.status_code == 200:
            print(f"Message envoyé pour {incident_data['Incident']}")
            # Mettre à jour notif_send à true dans Redis
            incident_data['notif_send'] = True
            r.set(key, json.dumps(incident_data, ensure_ascii=False))
        else:
            print(f"Échec de l'envoi pour {incident_data['Incident']}: {response.status_code}")
