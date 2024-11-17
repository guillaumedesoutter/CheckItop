import redis
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

#Mise en forme de l'horodatage pour les messages de log
def log(message):
    # Horodatage (HH:MM:SS)
    print(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

log("Démarrage du script")

# Connexion à Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    log("Connexion à Redis réussie.")
except Exception as e:
    log(f"Erreur de connexion à Redis : {e}")

# Étape 1 : Récupérer tous les incidents stockés dans Redis
log("Récupération des incidents dans Redis")
incidents_redis = {}
keys = r.keys("incident:*")
log(f"{len(keys)} incidents trouvés dans Redis.")
for key in keys:
    incident_data = r.get(key)
    if incident_data:
        incident = json.loads(incident_data)
        incident_id = incident["Incident"]
        incidents_redis[incident_id] = incident
log(f"Incidents chargés depuis Redis : {incidents_redis}")

# Étape 2 : Initialiser le navigateur Selenium et récupérer les incidents depuis iTop
log("Initialisation de Selenium et chargement de la page iTop")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_argument("--disable-extensions")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
driver = webdriver.Chrome(options=options)

try:
    driver.get("ipduserveuritopàcompleter")
    log("Page iTop chargée.")
    champ_username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user")))
    champ_username.send_keys("admin")
    log("Nom d'utilisateur saisi.")
    
    champ_password = driver.find_element(By.ID, "pwd")
    champ_password.send_keys("admin")
    log("Mot de passe saisi.")
    
    bouton_login = driver.find_element(By.CSS_SELECTOR, "input[value='Entrer dans iTop']")
    bouton_login.click()
    log("Connexion en cours...")

    vue_incident = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "li[id='AccordionMenu_MyShortcuts_1'] a"))
    )
    vue_incident.click()
    log("Vue des incidents sélectionnée.")

    lignes_tableau_incident = driver.find_elements(By.XPATH, "//table//tr")

except Exception as e:
    log(f"Erreur lors de la connexion à iTop ou de la navigation : {e}")

# On prépare une liste pour les incidents récupérés depuis iTop
log("Récupération des incidents depuis iTop")
incidents_itop = {}
for ligne_incident in lignes_tableau_incident:
    driver.execute_script("arguments[0].scrollIntoView();", ligne_incident)
    time.sleep(0.5)

    colonne = ligne_incident.find_elements(By.TAG_NAME, "td")
    if colonne and colonne[0].text.startswith("I-"):
        if len(colonne) >= 5:
            incident_numero = colonne[0].text.strip()
            titre = colonne[1].text.strip()
            agent = colonne[2].text.strip()
            echeance_tto = colonne[3].text.strip()
            echeance_ttr = colonne[4].text.strip()

            incident = {
                "Incident": incident_numero,
                "Titre": titre,
                "Agent": agent,
                "Échéance TTO": echeance_tto,
                "Échéance TTR": echeance_ttr
            }
            incidents_itop[incident_numero] = incident
log(f"Incidents récupérés depuis iTop : {incidents_itop}")

# Étape 3 : Comparaison et mise à jour de Redis
log("Comparaison et mise à jour des incidents dans Redis")
for incident_id, incident_data in incidents_redis.items():
    if incident_id not in incidents_itop:
        log(f"Suppression de l'incident {incident_id} de Redis.")
        r.delete(f"incident:{incident_id}")

for incident_id, incident_data in incidents_itop.items():
    if incident_id not in incidents_redis:
        log(f"Ajout de l'incident {incident_id} dans Redis.")
        incident_data["notif_send"] = False
        r.set(f"incident:{incident_id}", json.dumps(incident_data, ensure_ascii=False))
    else:
        log(f"Mise à jour de l'incident {incident_id} dans Redis.")
        incident_data["notif_send"] = incidents_redis[incident_id]["notif_send"]
        r.set(f"incident:{incident_id}", json.dumps(incident_data, ensure_ascii=False))

# Fermer le navigateur
log("Fermeture de Selenium")
driver.quit()
log("Script terminé.")
