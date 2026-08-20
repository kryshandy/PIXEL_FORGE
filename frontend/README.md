# PetroSage — Frontend

Interface web de **PetroSage**, copilote IA pour la complétion et la production de puits pétroliers conventionnels.
Projet soumis au **Pixel Forge AI Hackathon** (15 → 22 août 2026).

## Stack technique

- **React 18** + **Vite**
- **Three.js** pour la scène 3D du hero
- **Vitest** pour les tests unitaires
- **Oxlint** pour le linting

## Prérequis

- Node.js 18+ et npm
- Le backend FastAPI de PetroSage doit tourner en local pour que le formulaire retourne de vraies recommandations (voir `docs/` à la racine du dépôt pour le lancer)

## Installation

```bash
cd frontend
npm install
```

## Variables d'environnement

Copier `.env.example` vers `.env` et ajuster si besoin :

```bash
cp .env.example .env
```

| Variable | Description | Valeur par défaut |
|---|---|---|
| `VITE_API_BASE_URL` | URL de base de l'API backend | `http://127.0.0.1:8000/api/v1` |

## Commandes disponibles

| Commande | Description |
|---|---|
| `npm run dev` | Lance le serveur de développement (`http://localhost:5173`) |
| `npm run build` | Build de production dans `dist/` |
| `npm run preview` | Prévisualise le build de production en local |
| `npm run lint` | Vérifie le code avec Oxlint |
| `npm run test` | Lance les tests unitaires (Vitest) |

## Structure du projet