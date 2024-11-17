# Check_itop

  
  
  

## Presentation du projet

  

Ce projet a pour but de réduire les erreurs humaines en automatisant la vérification de la liste des incidents ITOP et de notifier les membres d’une équipe directement dans un canal Teams lorsqu’une P1 arrive ou lorsqu’un TTR/TTO va expirer.

  

## Structure

  

Pour ce projet d’automatisation, la stack se décompose en trois conteneurs docker :

-  Un conteneur docker hébergeant un script python permettant de récupérer les données sur ITOP

-  Un conteneur docker Redis servant de base de données légères pour stocker les données

-  Un conteneur docker hébergeant un script python pour envoyer des messages sur le canal Teams via un webhook entrant.

  

## Scripts

  

### Script Python Selenium
  

Objectif : Synchroniser les incidents entre iTop et Redis.

Étapes principales :

- Connexion à Redis : Le script initialise une connexion pour accéder aux incidents stockés dans Redis.

- Extraction des incidents depuis Redis : Récupère les incidents existants pour pouvoir les comparer à ceux extraits de l'interface iTop.

- Accès à iTop avec Selenium : Utilise Selenium pour simuler une connexion et naviguer dans iTop afin de récupérer les données des incidents.

- Traitement des données des incidents : Les incidents extraits d’iTop sont structurés sous forme de dictionnaire, comprenant des informations telles que le numéro d'incident, le titre, l'agent, les échéances TTO et TTR.

- Synchronisation avec Redis : Compare les incidents de Redis avec ceux récupérés d’iTop. Les incidents sont ajoutés, mis à jour ou supprimés en fonction de leur état dans iTop.

Technologies utilisées : Redis, Selenium, JSON.

  

###  Script Python Notifier

  

Objectif : Notifier les équipes des nouveaux incidents ou de leur mise à jour via un message Teams.

Étapes principales :

- Connexion à Redis : Se connecte à Redis pour récupérer les incidents dont le champ notif_send est à False.

- Vérification des critères et de l'état de notification : Parcourt chaque incident pour vérifier les critères TTO/TTR, la priorité et si une notification a déjà été envoyée.

- Envoi de la notification : Formate et envoie une notification via un webhook Teams. Si l’envoi est réussi, le champ notif_send est mis à True dans Redis.

- Gestion des erreurs d’envoi : En cas d’échec, le script capture le code de statut HTTP pour faciliter le diagnostic.

Technologies utilisées : Redis, Requests, JSON, Webhook Teams.

  

## Auteur

Guillaume Desoutter
