# Guide d'installation — Microservices Demo

Ce guide vous accompagne pas à pas pour installer, démarrer et tester le projet en local, puis le déployer sur Kubernetes.

---

## 1. Prérequis

Assurez-vous que les outils suivants sont installés sur votre machine avant de commencer.

| Outil           | Version minimale | Vérification                    |
|-----------------|------------------|---------------------------------|
| Docker          | ≥ 20.10          | `docker --version`              |
| Docker Compose  | ≥ 2.x            | `docker compose version`        |
| Git             | toute version    | `git --version`                 |
| RAM disponible  | 4 Go recommandés | — (3 services + PostgreSQL)     |

*(optionnel — pour Kubernetes)* :

| Outil      | Vérification            |
|------------|-------------------------|
| kubectl    | `kubectl version`       |
| minikube   | `minikube version`      |

---

## 2. Installation et démarrage avec Docker Compose

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd microservices_demo

# 2. Construire les images Docker et démarrer tous les services
#    (db, user-service, vote-service, notification-service)
docker compose up --build
```

Attendez que les logs indiquent que chaque service est démarré. Le service `db` (PostgreSQL) effectue un healthcheck avec `pg_isready` avant que les services applicatifs ne démarrent.

```bash
# 3. Dans un autre terminal : exécuter les migrations de base de données
docker compose exec user-service python manage.py migrate
docker compose exec vote-service python manage.py migrate
docker compose exec notification-service python manage.py migrate

# 4. Créer un superutilisateur (nécessaire pour créer des topics de vote)
docker compose exec user-service python manage.py createsuperuser

# 5. Vérifier que les services répondent
curl http://localhost:8000/admin/
curl http://localhost:8001/admin/
curl http://localhost:8002/admin/
```

Les services sont maintenant accessibles :

| Service              | URL locale              |
|----------------------|-------------------------|
| user-service         | http://localhost:8000   |
| vote-service         | http://localhost:8001   |
| notification-service | http://localhost:8002   |
| Django Admin (user)  | http://localhost:8000/admin/ |

---

## 3. Tester avec curl — séquence complète

La séquence suivante illustre un cycle complet : inscription → login → vote → consultation des résultats → notification.

```bash
# ── Étape 1 : Enregistrer un utilisateur ──────────────────────────────────────
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"Pass1234!","password2":"Pass1234!"}'

# Réponse attendue :
# {"id": 1, "username": "alice", "email": "alice@example.com"}


# ── Étape 2 : Obtenir un token JWT ────────────────────────────────────────────
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass1234!"}'

# Réponse attendue :
# {"access": "eyJ...", "refresh": "eyJ..."}
# → Copier la valeur du champ "access" pour les étapes suivantes


# ── Étape 3 : Lister les topics de vote ───────────────────────────────────────
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8001/api/votes/topics/

# Si la liste est vide, créez d'abord un topic avec le superuser (étape 3b)


# ── Étape 3b (optionnel) : Créer un topic avec le superuser ───────────────────
# D'abord, obtenir un token pour le superuser :
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<superuser>","password":"<password>"}'

# Puis créer un topic :
curl -X POST http://localhost:8001/api/votes/topics/ \
  -H "Authorization: Bearer <superuser_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Faut-il adopter Python 3.12 ?","description":"Discussion sur la migration."}'


# ── Étape 4 : Voter sur le topic 1 ────────────────────────────────────────────
curl -X POST http://localhost:8001/api/votes/topics/1/vote/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"choice":"for"}'

# Réponse 201 si nouveau vote, 200 si mise à jour d'un vote existant


# ── Étape 5 : Voir les résultats ──────────────────────────────────────────────
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8001/api/votes/topics/1/results/

# Réponse attendue :
# {"topic_id": 1, "topic_title": "...", "is_active": true, "total_votes": 1,
#  "results": {"for": 1, "against": 0, "abstain": 0}}


# ── Étape 6 : Voir les notifications ──────────────────────────────────────────
curl -H "Authorization: Bearer <access_token>" \
  "http://localhost:8002/api/notifications/?user_id=1"

# Réponse attendue :
# [{"id": 1, "user_id": 1, "event_type": "vote_cast", "message": "...",
#   "is_read": false, "created_at": "..."}]


# ── Étape 7 (optionnel) : Marquer la notification comme lue ───────────────────
curl -X PUT http://localhost:8002/api/notifications/1/read/ \
  -H "Authorization: Bearer <access_token>"


# ── Étape 8 (optionnel) : Rafraîchir le token d'accès ─────────────────────────
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

## 4. pgAdmin (optionnel)

pgAdmin est inclus dans la configuration Docker mais activé uniquement avec le profil `debug` pour ne pas consommer de ressources inutilement en développement normal.

```bash
# Démarrer avec le profil debug pour inclure pgAdmin
docker compose --profile debug up
```

- **URL** : http://localhost:5050
- **Email** : `admin@admin.com`
- **Mot de passe** : `admin`

### Ajouter le serveur PostgreSQL dans pgAdmin

Avec pgAdmin inclus dans Docker, le serveur **Microservices PostgreSQL** est
ajouté automatiquement. Il suffit d'ouvrir http://localhost:5050 et de se
connecter avec `admin@admin.com` / `admin`.

Si vous utilisez **pgAdmin Desktop** installé sur Windows, ajoutez le serveur
avec `localhost` comme hôte (et non `db`) : le port PostgreSQL `5432` est
maintenant publié par Docker.

1. Cliquer sur **Add New Server**
2. Onglet **General** → Name : `microservices_db`
3. Onglet **Connection** :
   - **Host** : `db` (pgAdmin Web Docker) ou `localhost` (pgAdmin Desktop)
   - **Port** : `5432`
   - **Maintenance database** : `postgres`
   - **Username** : `postgres`
   - **Password** : `postgres`

Vous pourrez alors explorer les trois bases de données : `users_db`, `votes_db`, `notifications_db`.

---

## 5. Déploiement Kubernetes

### Prérequis

- minikube installé et en cours d'exécution, **ou** accès à un cluster Kubernetes
- `kubectl` configuré et pointant vers le bon contexte

```bash
# Démarrer minikube (si pas encore démarré)
minikube start

# Appliquer toutes les ressources Kubernetes
# (ConfigMap, Secrets, PostgreSQL StatefulSet, Deployments, Services, Ingress)
kubectl apply -f k8s/

# Vérifier l'état des pods (attendre que tous soient "Running")
kubectl get pods

# Vérifier les services exposés
kubectl get services

# Vérifier la configuration de l'Ingress
kubectl get ingress

# Activer le contrôleur Ingress dans minikube
minikube addons enable ingress

# Obtenir l'adresse IP de minikube
minikube ip
```

### Configurer le fichier hosts

Ajoutez l'entrée suivante dans votre fichier hosts en remplaçant `<minikube-ip>` par l'IP retournée par `minikube ip` :

- **Linux / macOS** : `/etc/hosts`
- **Windows** : `C:\Windows\System32\drivers\etc\hosts`

```
<minikube-ip>  microservices.local
```

### Accéder aux services

Après configuration du fichier hosts, les services sont accessibles via :

| Service              | URL Kubernetes                                    |
|----------------------|---------------------------------------------------|
| user-service         | http://microservices.local/api/users/             |
| vote-service         | http://microservices.local/api/votes/             |
| notification-service | http://microservices.local/api/notifications/     |

### Scaler un service

```bash
# Exemple : augmenter le nombre de répliques de vote-service
kubectl scale deployment vote-service --replicas=3

# Vérifier
kubectl get pods
```

---

## 6. Troubleshooting

| Problème | Cause probable | Solution |
|---|---|---|
| `django.db.OperationalError: could not connect to server` | PostgreSQL pas encore prêt au démarrage | Attendre que le healthcheck `pg_isready` passe, puis relancer `docker compose up` |
| `401 Unauthorized` sur un endpoint protégé | Token d'accès expiré ou header manquant | Rafraîchir avec `POST /api/users/token/refresh/` ou se reconnecter |
| `403 Forbidden` sur `POST /api/votes/topics/` | L'utilisateur connecté n'est pas admin (`is_staff=False`) | Utiliser le superuser créé avec `createsuperuser`, ou promouvoir l'utilisateur dans l'admin Django |
| Les notifications n'apparaissent pas | notification-service arrêté ou en erreur | `docker compose ps` pour vérifier l'état, puis `docker compose restart notification-service` |
| Port déjà utilisé (8000, 8001, 8002, 5432) | Un autre processus occupe le port | **Linux/macOS** : `lsof -i :8000` — **Windows** : `netstat -ano | findstr :8000`, puis arrêter le processus concerné |
| `ModuleNotFoundError` au démarrage d'un service | Dépendances non installées dans l'image | Reconstruire l'image : `docker compose build <service-name>` |
| Migration échoue avec `relation does not exist` | Les migrations n'ont pas encore été exécutées | Relancer `docker compose exec <service> python manage.py migrate` |
| `502 Bad Gateway` sur l'Ingress Kubernetes | Pod pas encore prêt ou service mal configuré | `kubectl describe ingress`, `kubectl logs <pod-name>` pour diagnostiquer |
