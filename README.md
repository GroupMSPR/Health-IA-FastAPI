# 🧠 Health-IA-FastAPI - API d'Analyse IA Nutritionnelle

**Microservice d'Intelligence Artificielle** de la plateforme HealthAI Coach, construit avec **FastAPI** et **Ollama**. Cette API permet d'analyser des images de repas grâce au modèle multimodal **LLaVA**, d'estimer les calories, de lister les macronutriments et de fournir des recommandations nutritionnelles.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688?logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLaVA-black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

![Type](https://img.shields.io/badge/Type-Microservice_IA-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Stack technologique](#stack-technologique)
- [Installation et Déploiement](#installation-et-déploiement)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Vue d'ensemble

**Health-IA-FastAPI** est le moteur d'analyse d'images de la plateforme.  
Il expose des endpoints rapides et documentés pour interagir avec un modèle de langage local (**LLaVA via Ollama**), évitant ainsi de dépendre d'API externes payantes et garantissant la confidentialité des données de santé.

**Point d'entrée recommandé** :  
Le repository [Health-IA-Workspace](https://github.com/GroupMSPR/Health-IA-Workspace) qui orchestre l'ensemble du projet.

---

## Architecture

### Structure du projet

```text
Health-IA-FastAPI/
├── app/
│   └── main.py             # Contrôleurs et logique métier FastAPI
├── .env.example            # Exemple de variables d'environnement
├── docker-compose.yml      # Orchestration (API + Serveur Ollama)
├── Dockerfile              # Configuration de l'image de l'API Python
└── requirements.txt        # Dépendances Python (FastAPI, Uvicorn, Requests)
```

---

### Diagramme de flux

```text
Client (Frontend/Mobile)
    ↓
Requête POST avec Image (multipart/form-data)
    ↓
FastAPI (Port 4000)
    ↓ (Conversion Base64 + Prompt Expert Nutrition)
Serveur Ollama (Port 11434)
    ↓ (Analyse par le modèle LLaVA)
Retour JSON structuré
    ↓
Client
```

---

## Stack technologique

### Backend & API

- **Framework** : FastAPI
- **Serveur ASGI** : Uvicorn
- **Langage** : Python 3.11

### Intelligence Artificielle

- **Moteur LLM** : Ollama (serveur d'inférence local)
- **Modèle utilisé** : LLaVA (Large Language-and-Vision Assistant)

### DevOps

- **Containerization** : Docker
- **Orchestration** : Docker Compose
- **Accélération matérielle** : Support GPU Nvidia / WSL2 (configurable)

---

## Installation et Déploiement

### Prérequis

- Docker Desktop (fortement recommandé pour gérer Ollama)
- RAM : au moins 8 Go (16 Go recommandés pour faire tourner le modèle IA confortablement)
- *(Optionnel)* Carte graphique Nvidia avec pilotes à jour pour de meilleures performances

---

### Déploiement avec Docker (Recommandé)

Le fichier `docker-compose.yml` déploie à la fois :

- l'API FastAPI
- le serveur autonome Ollama

```bash
# 1. Cloner le repository

git clone https://github.com/GroupMSPR/Health-IA-FastAPI.git
cd Health-IA-FastAPI

# 2. Lancer les conteneurs (FastAPI + Ollama)

docker compose up -d
```

---

## ⚠️ Étape obligatoire : Télécharger le modèle IA

Une fois les conteneurs lancés, le serveur Ollama est vide.  
Vous devez télécharger le modèle `llava` à l'intérieur du conteneur Ollama pour que l'API fonctionne :

```bash
docker exec -it healthai_ollama ollama run llava
```

> Le téléchargement prendra quelques minutes selon votre connexion.  
> Vous pouvez faire `Ctrl + D` pour quitter le terminal Ollama une fois le téléchargement terminé.

L'API est maintenant accessible sur :

```txt
http://localhost:4000
```

---

## API Documentation

FastAPI génère automatiquement la documentation interactive (Swagger UI).

Une fois le projet lancé, visitez :

```txt
http://localhost:4000/docs
```

---

## Endpoints principaux

### 🔍 Vérification du statut

| Méthode | Endpoint | Description |
|----------|----------|-------------|
| `GET` | `/` | Vérifie que l'API est opérationnelle |

---

### 📸 Analyse de repas

| Méthode | Endpoint | Description |
|----------|----------|-------------|
| `POST` | `/analyze-meal` | Reçoit une image et renvoie l'analyse nutritionnelle |

---

### Exemple de requête (CURL)

```bash
curl -X 'POST' \
  'http://localhost:4000/analyze-meal' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@mon_assiette.jpg;type=image/jpeg'
```

---

### Exemple de réponse (`200 OK`)

```json
{
  "status": "success",
  "model_used": "llava",
  "analysis": "Je vois une assiette composée de poulet grillé, de brocolis et de riz... Estimation : 450 kcal. Protéines: 35g, Glucides: 45g, Lipides: 10g..."
}
```

---

## Configuration

### Variables d'environnement (`.env`)

Copiez le fichier `.env.example` en `.env` :

```bash
cp .env.example .env
```

---

### Exemple de configuration

```env
# URL du serveur Ollama

OLLAMA_URL=http://ollama:11434
# Utiliser http://localhost:11434 si lancé en local sans Docker
```

---

## ⚡ Accélération GPU (Nvidia)

Si vous possédez une carte graphique Nvidia et souhaitez accélérer drastiquement le temps de réponse de l'IA :

ouvrez le fichier `docker-compose.yml` et décommentez la section `deploy` du service `ollama` :

```yaml
# Décommente 'deploy' si tu as une GPU Nvidia et WSL2

deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

---

## Troubleshooting

### Erreur de communication avec Ollama (503)

#### Problème

```txt
Erreur de communication avec Ollama: Connection refused
```

#### Solution

- Vérifiez que le conteneur `ollama` est bien démarré :

```bash
docker ps
```

- Si vous êtes en local (sans Docker Compose), assurez-vous que :

```env
OLLAMA_URL=http://localhost:11434
```

et non :

```env
OLLAMA_URL=http://ollama:11434
```

---

### Modèle non trouvé (Erreur 500 ou 404)

#### Problème

L'image est envoyée mais l'API retourne une erreur indiquant que le modèle `llava` n'existe pas.

#### Solution

Téléchargez le modèle :

```bash
docker exec -it healthai_ollama ollama pull llava
```

---

### L'IA est extrêmement lente

#### Problème

La requête `/analyze-meal` prend plusieurs minutes.

#### Solution

Le traitement d’images par IA est lourd et s’exécute probablement sur le CPU.

Pour améliorer les performances :

- activez le support GPU dans `docker-compose.yml`
- utilisez une machine plus puissante
- augmentez la RAM disponible pour Docker

---

## 📚 Documentation supplémentaire

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.com/)
- [LLaVA Model Info](https://llava-vl.github.io/)

---

## 👥 Équipe

Développeurs MSPR :

- Ilan
- Anthony
- Diana

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🔗 Liens

- **Organization** : GroupMSPR
- **Workspace** : Health-IA-Workspace
- **Frontend** : Health-IA-Frontend
- **Backend** : Health-IA-Backend
- **ETL** : Health-IA-ETL
- **Grafana** : Health-IA-Grafana

---

Dernière mise à jour : 29 mai 2026

Pour toute question ou contribution, consultez le repository ou ouvrez une issue.
