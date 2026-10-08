# Architecture technique — Microservices Demo

## 1. Vue d'ensemble

Le projet adopte une **architecture microservices** : l'application est décomposée en trois services autonomes, chacun ayant une **responsabilité unique et bien définie**. Chaque service est déployé dans son propre conteneur Docker, possède sa propre base de données et communique avec les autres services exclusivement via HTTP REST.

Cette approche contraste avec une architecture monolithique dans laquelle toute la logique métier réside dans une seule application. Ici, un service peut évoluer, être déployé ou scalé indépendamment des autres.

---

## 2. Justification du découpage en services

### user_service — Identité et authentification

Ce service est responsable de tout ce qui concerne les **utilisateurs** : inscription, connexion, gestion de profil, et émission des tokens JWT. Il constitue le fournisseur d'identité du système.

Raisons du découpage :
- L'authentification est un domaine transversal utilisé par tous les autres services
- Isoler la gestion des comptes protège les données sensibles (mots de passe hashés)
- Peut évoluer vers un fournisseur OAuth2/OIDC complet sans impacter les autres services

### vote_service — Logique métier du vote

C'est le **domaine central** (core domain) de l'application. Il gère les sujets de vote, l'enregistrement des votes et le calcul des résultats.

Raisons du découpage :
- Contient la valeur métier principale de l'application
- Peut être scalé indépendamment (plus de trafic lors de votes importants)
- Les règles métier (un vote par utilisateur, choix valides) sont encapsulées ici

### notification_service — Notifications événementielles

Ce service stocke et expose les notifications destinées aux utilisateurs. Il est découplé du service de vote.

Raisons du découpage :
- Peut évoluer indépendamment (ajout de canaux : email, push, SMS) sans toucher à vote_service
- Découplage temporel via le pattern fire-and-forget
- La défaillance de ce service n'impacte pas la disponibilité du vote

---

## 3. Flux principal : un utilisateur vote

Le diagramme séquentiel ci-dessous illustre le chemin complet d'un vote, de l'authentification à la notification :

```ascii
Client                user_service          vote_service          notification_service
  │                       │                      │                        │
  │  POST /api/users/login/│                      │                        │
  │  {"username","password}│                      │                        │
  │──────────────────────▶│                      │                        │
  │                       │  Vérifie credentials  │                        │
  │                       │  Génère tokens JWT    │                        │
  │◀──────────────────────│                      │                        │
  │  {"access","refresh"} │                      │                        │
  │                       │                      │                        │
  │  POST /api/votes/topics/1/vote/               │                        │
  │  Authorization: Bearer <access_token>         │                        │
  │  {"choice": "for"}    │                      │                        │
  │──────────────────────────────────────────────▶│                        │
  │                       │    vote_service valide le JWT localement       │
  │                       │    (SimpleJWT + SECRET_KEY partagée)           │
  │                       │    → pas d'appel réseau vers user_service      │
  │                       │                      │                        │
  │                       │              Crée/met à jour Vote              │
  │                       │              dans votes_db                     │
  │                       │                      │                        │
  │                       │              POST /api/notifications/create/   │
  │                       │              (fire-and-forget, timeout=2s)     │
  │                       │              ───────────────────────────────▶  │
  │                       │                      │   Stocke Notification   │
  │                       │                      │   dans notifications_db │
  │                       │                      │◀─────────────────────── │
  │                       │                      │   201 (ou erreur        │
  │                       │                      │   ignorée)              │
  │                       │                      │                        │
  │◀──────────────────────────────────────────────│                        │
  │  201 Created (ou 200 Updated)                 │                        │
  │  {"message": "Vote créé/mis à jour avec succès.", "vote": {...}}       │
  │                       │                      │                        │
```

**Points clés du flux :**
1. Le token JWT est émis une seule fois par user_service lors du login
2. Toutes les validations suivantes sont locales à chaque service (pas d'appel vers user_service)
3. La notification est envoyée après l'enregistrement du vote — le résultat du vote n'en dépend pas

---

## 4. Pattern d'authentification JWT

### Deux approches possibles

**Validation distante (non utilisée ici) :**
À chaque requête authentifiée, le service appelant ferait une requête HTTP vers user_service (sur l'endpoint `/api/users/me/` par exemple) pour vérifier la validité du token. Cela crée une dépendance réseau synchrone : si user_service est lent ou indisponible, toutes les requêtes vers vote_service échouent.

**Validation locale (approche du projet) :**
Chaque service possède la même `SECRET_KEY` que user_service. La bibliothèque **SimpleJWT** peut décoder et vérifier la signature du JWT entièrement en mémoire, sans aucun appel réseau. La validation vérifie :
- La signature cryptographique du token (avec la SECRET_KEY)
- La date d'expiration (`exp` claim)
- Le type du token (`access` vs `refresh`)

```ascii
Vote-service reçoit une requête avec JWT
       │
       ▼
SimpleJWT.decode(token, SECRET_KEY)
       │
       ├─ Signature valide ? ──Non──▶ 401 Unauthorized
       │
       ├─ Token expiré ?      ──Oui──▶ 401 Unauthorized
       │
       └─ OK ──▶ request.user est populé ──▶ traitement de la requête
```

**Conséquence en production :** tous les services **doivent partager exactement la même `SECRET_KEY`**. En environnement de production, cette clé doit être stockée dans un secret Kubernetes (`secrets.yaml`) et non en clair dans `docker-compose.yml`.

---

## 5. Isolation des bases de données

Chaque service dispose de **sa propre base de données logique** dans l'instance PostgreSQL :

| Service              | Base de données  | Tables principales              |
|----------------------|------------------|---------------------------------|
| user_service         | users_db         | users, auth_token, ...          |
| vote_service         | votes_db         | votes_topic, votes_vote         |
| notification_service | notifications_db | notifications_notification      |

### Pas de jointures cross-service

Il n'existe **aucune Foreign Key entre les bases de données**. Les références cross-service utilisent des **champs Integer** :

```python
# Dans vote_service/votes/models.py
class Topic(models.Model):
    # Pas de: created_by = models.ForeignKey(User, ...)
    created_by_user_id = models.IntegerField()  # Simple entier — référence "logique"

class Vote(models.Model):
    topic = models.ForeignKey(Topic, ...)  # FK intra-service : OK
    user_id = models.IntegerField()        # FK cross-service : Integer seulement
```

**Pourquoi ?** Une Foreign Key impose une contrainte d'intégrité référentielle que la base de données ne peut pas garantir entre deux instances DB distinctes. En utilisant de simples entiers, les services restent véritablement indépendants au niveau des données.

---

## 6. Communication synchrone vs asynchrone

### Communication synchrone (client → services)

Le client communique avec les services via des appels HTTP REST synchrones. La réponse est attendue avant de continuer.

### Communication asynchrone — fire-and-forget (vote_service → notification_service)

```python
# Extrait de vote_service/votes/views.py
def _notify_vote_cast(user_id, topic_title, choice):
    try:
        requests.post(
            settings.NOTIFICATION_SERVICE_URL + "/api/notifications/create/",
            json={...},
            timeout=2  # Maximum 2 secondes d'attente
        )
    except Exception:
        pass  # Toute erreur (timeout, connexion refusée, 500) est ignorée
```

Ce pattern garantit que **la défaillance de notification_service ne dégrade pas vote_service**. L'utilisateur reçoit sa réponse de vote dans tous les cas.

### Évolution possible vers une queue de messages

Le fire-and-forget HTTP présente une limitation : si notification_service est arrêté, les notifications sont **perdues définitivement**. Une architecture plus robuste utiliserait une queue de messages :

```ascii
Actuel :   vote_service ──HTTP──▶ notification_service (perte possible si down)

Futur :    vote_service ──▶ [RabbitMQ / Redis Streams] ──▶ notification_service
                             (messages persistés, replay possible)
```

Technologies envisageables : **RabbitMQ**, **Redis Streams**, **Apache Kafka**, **Celery**.

---

## 7. Scalabilité avec Kubernetes

### Déploiements indépendants

Les manifestes Kubernetes (`k8s/`) définissent un `Deployment` par service. Chaque Deployment peut être scalé indépendamment selon la charge :

```bash
# Scaler vote-service lors d'un pic de votes
kubectl scale deployment vote-service --replicas=5

# Scaler notification-service indépendamment
kubectl scale deployment notification-service --replicas=2

# user-service reçoit moins de trafic (seulement les logins/inscriptions)
kubectl scale deployment user-service --replicas=2
```

### PostgreSQL

En production, PostgreSQL est déployé en tant que **StatefulSet** (et non un Deployment) pour garantir la persistance des données avec des volumes persistants (`PersistentVolumeClaim`). Un StatefulSet maintient une identité réseau stable et des volumes persistants même en cas de redémarrage.

### Ingress

L'Ingress Kubernetes (`k8s/ingress.yaml`) expose les trois services sous un seul point d'entrée HTTP, en routant les requêtes selon le préfixe de l'URL :

```ascii
                    ┌─────────────────────────┐
  Internet          │   Ingress Controller     │
  ──────────────▶   │   microservices.local    │
                    │                         │
                    │  /api/users/    ────────▶│──▶ user-service:8000
                    │  /api/votes/    ────────▶│──▶ vote-service:8001
                    │  /api/notifications/ ───▶│──▶ notification-service:8002
                    └─────────────────────────┘
```

Activer l'Ingress dans minikube :

```bash
minikube addons enable ingress
kubectl apply -f k8s/ingress.yaml
```
