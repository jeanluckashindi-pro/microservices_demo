# Référence API — Microservices Demo

Ce document décrit l'ensemble des endpoints exposés par les trois services. Tous les exemples utilisent `curl` et supposent que les services tournent localement via Docker Compose.

---

## Convention d'authentification

Les endpoints protégés requièrent un token JWT dans le header HTTP :

```
Authorization: Bearer <access_token>
```

Le token s'obtient via `POST /api/users/login/`. Sa durée de validité est configurable (par défaut SimpleJWT : 5 minutes pour `access`, 1 jour pour `refresh`).

---

## user_service — http://localhost:8000

### POST /api/users/register/

Crée un nouveau compte utilisateur.

- **Authentification** : aucune
- **Content-Type** : application/json

**Body de la requête :**

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "motdepasse123",
  "password2": "motdepasse123"
}
```

**Réponse 201 Created :**

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com"
}
```

**Codes HTTP :**

| Code | Signification                                      |
|------|----------------------------------------------------|
| 201  | Utilisateur créé avec succès                       |
| 400  | Données invalides (mots de passe non concordants, username déjà pris, etc.) |

---

### POST /api/users/login/

Authentifie un utilisateur et retourne une paire de tokens JWT.

- **Authentification** : aucune
- **Content-Type** : application/json

**Body de la requête :**

```json
{
  "username": "alice",
  "password": "motdepasse123"
}
```

**Réponse 200 OK :**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Codes HTTP :**

| Code | Signification                    |
|------|----------------------------------|
| 200  | Authentification réussie         |
| 401  | Identifiants incorrects          |

---

### POST /api/users/token/refresh/

Rafraîchit un token d'accès expiré à partir d'un token de rafraîchissement.

- **Authentification** : aucune (le refresh token fait office d'authentification)
- **Content-Type** : application/json

**Body de la requête :**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Réponse 200 OK :**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Codes HTTP :**

| Code | Signification                                        |
|------|------------------------------------------------------|
| 200  | Nouveau token d'accès émis                           |
| 401  | Refresh token expiré, invalide ou déjà utilisé       |

---

### GET /api/users/me/

Retourne le profil de l'utilisateur actuellement authentifié.

- **Authentification** : Bearer token requis
- **Headers** : `Authorization: Bearer <access_token>`

**Réponse 200 OK :**

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "profile": {
    "bio": "",
    "avatar": null
  }
}
```

**Codes HTTP :**

| Code | Signification                          |
|------|----------------------------------------|
| 200  | Profil retourné                        |
| 401  | Token absent, invalide ou expiré       |

---

### GET /api/users/list/

Retourne la liste de tous les utilisateurs enregistrés.

- **Authentification** : admin seulement (IsAdminUser)
- **Headers** : `Authorization: Bearer <access_token_admin>`

**Réponse 200 OK :**

```json
[
  {"id": 1, "username": "alice", "email": "alice@example.com"},
  {"id": 2, "username": "bob", "email": "bob@example.com"}
]
```

**Codes HTTP :**

| Code | Signification                          |
|------|----------------------------------------|
| 200  | Liste retournée                        |
| 401  | Token absent ou invalide               |
| 403  | Utilisateur non admin                  |

---

### GET /api/users/\<id\>/

Retourne le profil d'un utilisateur par son identifiant.

- **Authentification** : Bearer token requis
- **Headers** : `Authorization: Bearer <access_token>`

**Réponse 200 OK :**

```json
{
  "id": 2,
  "username": "bob",
  "email": "bob@example.com"
}
```

**Codes HTTP :**

| Code | Signification                          |
|------|----------------------------------------|
| 200  | Profil retourné                        |
| 401  | Token absent ou invalide               |
| 404  | Utilisateur introuvable                |

---

### PUT /api/users/\<id\>/

Met à jour les informations d'un utilisateur.

- **Authentification** : Bearer token requis (propriétaire du compte ou admin)
- **Headers** : `Authorization: Bearer <access_token>`, `Content-Type: application/json`

**Body de la requête :**

```json
{
  "email": "newemail@example.com"
}
```

**Réponse 200 OK :**

```json
{
  "id": 1,
  "username": "alice",
  "email": "newemail@example.com"
}
```

**Codes HTTP :**

| Code | Signification                                      |
|------|----------------------------------------------------|
| 200  | Mise à jour réussie                                |
| 400  | Données invalides                                  |
| 401  | Token absent ou invalide                           |
| 403  | L'utilisateur n'est pas propriétaire du compte     |
| 404  | Utilisateur introuvable                            |

---

## vote_service — http://localhost:8001

### GET /api/votes/topics/

Retourne la liste de tous les sujets de vote, triés par date de création décroissante.

- **Authentification** : optionnelle (IsAuthenticatedOrReadOnly)

**Réponse 200 OK :**

```json
[
  {
    "id": 1,
    "title": "Faut-il adopter Python 3.12 ?",
    "description": "Discussion sur la migration vers Python 3.12 dans nos projets.",
    "created_by_user_id": 1,
    "is_active": true,
    "vote_count": 5,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

**Codes HTTP :**

| Code | Signification   |
|------|-----------------|
| 200  | Liste retournée |

---

### POST /api/votes/topics/

Crée un nouveau sujet de vote. L'identifiant de l'admin connecté est automatiquement enregistré comme `created_by_user_id`.

- **Authentification** : admin requis (IsAdminUser)
- **Headers** : `Authorization: Bearer <access_token>`, `Content-Type: application/json`

**Body de la requête :**

```json
{
  "title": "Faut-il adopter Python 3.12 ?",
  "description": "Discussion sur la migration vers Python 3.12 dans nos projets."
}
```

**Réponse 201 Created :**

```json
{
  "id": 1,
  "title": "Faut-il adopter Python 3.12 ?",
  "description": "Discussion sur la migration vers Python 3.12 dans nos projets.",
  "created_by_user_id": 1,
  "is_active": true,
  "vote_count": 0,
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Codes HTTP :**

| Code | Signification                   |
|------|---------------------------------|
| 201  | Sujet créé avec succès          |
| 400  | Données invalides               |
| 401  | Token absent ou invalide        |
| 403  | Utilisateur non admin           |

---

### GET /api/votes/topics/\<id\>/

Retourne le détail d'un sujet de vote.

- **Authentification** : optionnelle

**Réponse 200 OK :**

```json
{
  "id": 1,
  "title": "Faut-il adopter Python 3.12 ?",
  "description": "Discussion sur la migration vers Python 3.12 dans nos projets.",
  "created_by_user_id": 1,
  "is_active": true,
  "vote_count": 5,
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Codes HTTP :**

| Code | Signification          |
|------|------------------------|
| 200  | Détail retourné        |
| 404  | Sujet introuvable      |

---

### PUT /api/votes/topics/\<id\>/

Met à jour un sujet de vote existant.

- **Authentification** : admin requis
- **Headers** : `Authorization: Bearer <access_token>`, `Content-Type: application/json`

**Body de la requête :**

```json
{
  "title": "Faut-il adopter Python 3.12 ? (mise à jour)",
  "is_active": false
}
```

**Codes HTTP :**

| Code | Signification                   |
|------|---------------------------------|
| 200  | Mise à jour réussie             |
| 400  | Données invalides               |
| 401  | Token absent ou invalide        |
| 403  | Utilisateur non admin           |
| 404  | Sujet introuvable               |

---

### DELETE /api/votes/topics/\<id\>/

Supprime un sujet de vote ainsi que tous les votes associés.

- **Authentification** : admin requis
- **Headers** : `Authorization: Bearer <access_token>`

**Codes HTTP :**

| Code | Signification                   |
|------|---------------------------------|
| 204  | Suppression réussie (no content)|
| 401  | Token absent ou invalide        |
| 403  | Utilisateur non admin           |
| 404  | Sujet introuvable               |

---

### POST /api/votes/topics/\<id\>/vote/

Enregistre ou met à jour le vote d'un utilisateur authentifié sur un sujet. Un utilisateur ne peut avoir qu'un seul vote par sujet (`unique_together` sur `(topic, user_id)`). Déclenche une notification fire-and-forget vers notification_service.

- **Authentification** : Bearer token requis (IsAuthenticated)
- **Headers** : `Authorization: Bearer <access_token>`, `Content-Type: application/json`

**Body de la requête :**

```json
{
  "choice": "for"
}
```

Les valeurs acceptées pour `choice` : `"for"` (pour), `"against"` (contre), `"abstain"` (abstention).

**Réponse 201 Created (nouveau vote) :**

```json
{
  "message": "Vote créé avec succès.",
  "vote": {
    "id": 3,
    "topic": 1,
    "user_id": 2,
    "choice": "for",
    "voted_at": "2024-01-15T11:00:00Z"
  }
}
```

**Réponse 200 OK (vote mis à jour) :**

```json
{
  "message": "Vote mis à jour avec succès.",
  "vote": {
    "id": 3,
    "topic": 1,
    "user_id": 2,
    "choice": "against",
    "voted_at": "2024-01-15T11:05:00Z"
  }
}
```

**Codes HTTP :**

| Code | Signification                                                 |
|------|---------------------------------------------------------------|
| 201  | Nouveau vote enregistré                                       |
| 200  | Vote existant mis à jour                                      |
| 400  | Topic inactif (`is_active=False`) ou valeur de `choice` invalide |
| 401  | Token absent ou invalide                                      |
| 404  | Sujet introuvable                                             |

> **Note :** La notification vers notification_service est envoyée de manière fire-and-forget (timeout 2s, erreurs ignorées). Une indisponibilité de notification_service ne fait pas échouer le vote.

---

### GET /api/votes/topics/\<id\>/results/

Retourne les résultats agrégés d'un sujet de vote, calculés directement en SQL (`COUNT` avec `GROUP BY`).

- **Authentification** : optionnelle (IsAuthenticatedOrReadOnly)

**Réponse 200 OK :**

```json
{
  "topic_id": 1,
  "topic_title": "Faut-il adopter Python 3.12 ?",
  "is_active": true,
  "total_votes": 10,
  "results": {
    "for": 6,
    "against": 2,
    "abstain": 2
  }
}
```

**Codes HTTP :**

| Code | Signification          |
|------|------------------------|
| 200  | Résultats retournés    |
| 404  | Sujet introuvable      |

---

## notification_service — http://localhost:8002

### GET /api/notifications/?user_id=\<id\>

Retourne la liste des notifications d'un utilisateur, filtrées par le paramètre de requête `user_id`.

- **Authentification** : optionnelle (IsAuthenticatedOrReadOnly)
- **Paramètre d'URL** : `user_id` (entier) — identifiant de l'utilisateur

**Exemple de requête :**

```
GET http://localhost:8002/api/notifications/?user_id=2
```

**Réponse 200 OK :**

```json
[
  {
    "id": 1,
    "user_id": 2,
    "event_type": "vote_cast",
    "message": "Vous avez voté \"Pour\" sur le topic \"Faut-il adopter Python 3.12 ?\"",
    "is_read": false,
    "created_at": "2024-01-15T11:00:01Z"
  }
]
```

**Codes HTTP :**

| Code | Signification                 |
|------|-------------------------------|
| 200  | Liste des notifications       |

---

### POST /api/notifications/create/

Crée une nouvelle notification. Cet endpoint est accessible sans authentification pour permettre les appels service-à-service (vote_service → notification_service).

- **Authentification** : aucune (AllowAny)
- **Content-Type** : application/json

**Body de la requête :**

```json
{
  "user_id": 2,
  "event_type": "vote_cast",
  "message": "Vous avez voté \"Pour\" sur le topic \"Faut-il adopter Python 3.12 ?\""
}
```

**Réponse 201 Created :**

```json
{
  "id": 1,
  "user_id": 2,
  "event_type": "vote_cast",
  "message": "Vous avez voté \"Pour\" sur le topic \"Faut-il adopter Python 3.12 ?\"",
  "is_read": false,
  "created_at": "2024-01-15T11:00:01Z"
}
```

**Codes HTTP :**

| Code | Signification                              |
|------|--------------------------------------------|
| 201  | Notification créée avec succès             |
| 400  | Données invalides (champs requis manquants)|

> **Note de sécurité :** En production, cet endpoint `AllowAny` devrait être protégé par un réseau interne (non exposé publiquement) ou par un mécanisme d'authentification inter-services (token de service, mTLS).

---

### PUT /api/notifications/\<id\>/read/

Marque une notification comme lue (`is_read = True`).

- **Authentification** : Bearer token requis (IsAuthenticated)
- **Headers** : `Authorization: Bearer <access_token>`

**Réponse 200 OK :**

```json
{
  "id": 1,
  "user_id": 2,
  "event_type": "vote_cast",
  "message": "Vous avez voté \"Pour\" sur le topic \"Faut-il adopter Python 3.12 ?\"",
  "is_read": true,
  "created_at": "2024-01-15T11:00:01Z"
}
```

**Codes HTTP :**

| Code | Signification                    |
|------|----------------------------------|
| 200  | Notification marquée comme lue   |
| 401  | Token absent ou invalide         |
| 404  | Notification introuvable         |
