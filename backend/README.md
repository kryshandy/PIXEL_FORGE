# Backend Pixel Forge

API FastAPI et bibliothèque de calculs d'ingénierie du copilote Pixel Forge.

## Prérequis

- Python 3.10 ou supérieur
- Git

## Installation locale

Depuis le dossier `backend` :

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

À la racine du dépôt, copier `.env.example` vers `.env`, puis lancer :

```bash
uvicorn app.main:app --reload --env-file ../.env
```

- API : <http://127.0.0.1:8000>
- Documentation Swagger : <http://127.0.0.1:8000/docs>
- Santé : <http://127.0.0.1:8000/api/v1/health>

## Qualité et tests

```bash
ruff check .
mypy app
pytest --cov=app --cov-report=term-missing
```

## Indice de productivité

Le module `app.engineering.productivity_index` propose deux calculs purs et testables :

1. À partir d'un essai de puits : `J = qₒ / (pᵣ - pᵥf)`.
2. À partir du modèle radial de Darcy en unités de champ :
   `J = 0.00708 kh / [μₒ Bₒ (ln(rₑ/rᵥ) + correction + s)]`.

La correction vaut `0` en régime permanent et `-0.75` en régime pseudo-permanent.
Le résultat est exprimé en `STB/jour/psi` lorsque les entrées utilisent `md`, `ft`, `cP`
et `rb/STB`. Les hypothèses et unités sont explicites dans le résultat retourné.

> Ce module est un outil d'aide au calcul pour le prototype du hackathon. Toute décision
> opérationnelle doit être vérifiée par un ingénieur qualifié avec des données de terrain validées.

## Base vectorielle (Chroma)

Le module `app.rag` gère la base vectorielle utilisée par le pipeline RAG.

- `app.rag.config` : réglages via variables d'environnement (`CHROMA_PERSIST_DIR`,
  `CHROMA_COLLECTION_NAME`, `EMBEDDING_MODEL`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`,
  `RAG_TOP_K`), voir `.env.example` à la racine du dépôt.
- `app.rag.chroma_client` : client Chroma persistant local (`get_chroma_client`)
  et création/récupération de la collection du corpus (`get_or_create_corpus_collection`).
- Embeddings : `all-MiniLM-L6-v2` exécuté localement en ONNX via
  `chromadb.utils.embedding_functions.DefaultEmbeddingFunction` — gratuit, aucune
  clé API requise. Au premier appel réel, chromadb télécharge le modèle (~90 Mo) ;
  prévoir une connexion internet une seule fois.
- La base est persistée sur disque dans `CHROMA_PERSIST_DIR` (`.chroma/` par défaut,
  déjà ignoré par git). Elle survit aux redémarrages du backend.

Le découpage du corpus en chunks et l'indexation effective (Jour 2) vivront dans
`app.rag.ingest`, consommé par `docs/corpus/` (voir `docs/corpus/SOURCES.md` pour
la collecte des sources par Azra).

### Vérifier le setup localement

```bash
cd backend
python -c "
from app.rag.chroma_client import get_or_create_corpus_collection
collection = get_or_create_corpus_collection()
print('Collection prête :', collection.name, '| documents :', collection.count())
"
```

> Premier appel : peut prendre quelques secondes le temps de télécharger le modèle
> d'embedding. Les appels suivants sont instantanés (modèle mis en cache localement).
