# Pixel Forge — Copilote IA pour la complétion & production de puits pétroliers conventionnels

Projet soumis au **Pixel Forge AI Hackathon** (15 → 22 août 2026) · Catégorie **AI Agents** · Axe **Conception & Exploration — IA Oil & Gas**.

> Un copilote IA (RAG + LLM + calculs d'ingénierie) qui recommande une stratégie de complétion et de production adaptée à un puits pétrolier conventionnel, à partir des caractéristiques de son réservoir.

## Équipe

| Membre | Rôle principal | Domaine |
|---|---|---|
| Flo (Florent) | RAG, intégration LLM, prompt engineering, infra & déploiement | IA / Infra |
| **Krys** | **Module de calcul d'ingénierie, API backend, dépôt GitHub, soumission Devpost** | **Backend** |
| Henri-Michel | Formulaire & interface (frontend), vidéo de démo | Frontend |
| Azra | Recherche corpus, documentation, tests utilisateur, conformité règlement | Contenu / QA |

## Stack technique

| Composant | Choix |
|---|---|
| Backend | Python **FastAPI** |
| Calcul d'ingénierie | Python (`numpy`) — indice de productivité, pression de fracturation |
| Base vectorielle | Chroma (locale) |
| LLM | API Claude (version fonctionnelle) |
| Frontend | React (Henri-Michel) |
| Hébergement | Vercel / Render (URL live) |

## Structure du dépôt

```
PIXEL_FORGE/
├── backend/          # API FastAPI + module de calcul d'ingénierie (Krys)
├── frontend/         # Interface utilisateur React (Henri-Michel)
├── docs/             # Documentation du projet
├── LICENSE           # MIT
└── README.md
```

## Démarrage rapide (backend)

Prérequis : Python ≥ 3.10.

```bash
cd backend
python -m venv .venv
# Windows : .venv\Scripts\activate   |  Linux/macOS : source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Documentation interactive de l'API (Swagger) : http://127.0.0.1:8000/docs

## Exécution des tests

```bash
cd backend
pytest
```

Contrôles qualité complets :

```bash
cd backend
ruff check .
mypy app
pytest --cov=app --cov-report=term-missing
```

Le Jour 2 ajoute un module de calcul pur et testé pour l'indice de productivité,
avec méthode par essai de puits et estimation radiale de Darcy. Les hypothèses et
unités sont documentées dans [`backend/README.md`](backend/README.md).

## Documentation complète

La documentation métier et réglementaire du projet est maintenue dans [`docs/`](docs/).
