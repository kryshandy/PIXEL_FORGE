# Corpus documentaire — Sources

Tâche Jour 1 (Azra) : lister 5 à 10 documents techniques en accès libre sur la
complétion et la production de puits pétroliers **conventionnels**
(pétrophysique, indice de productivité, pression de fracturation, méthodes de
complétion). Une ligne par document ci-dessous, puis déposer le PDF/texte
correspondant dans `docs/corpus/raw/`.

Un exemple confirmé pour démarrer (accès libre, SPE) :

| # | Titre | Auteur / Organisation | URL | Type | Sujets couverts | Accès |
|---|---|---|---|---|---|---|
| 1 | Glossary: Productivity Index | PetroWiki (SPE) | https://petrowiki.spe.org/Glossary:Productivity_index | Wiki technique | Indice de productivité, IPR | Libre |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

## Où chercher (pistes)

- **PetroWiki** (petrowiki.spe.org) — wiki technique de la SPE, en accès libre, très bien structuré par sujet.
- **OnePetro** (onepetro.org) — publications SPE ; certains articles anciens ou résumés sont en accès libre.
- **ScienceDirect Topics** (sciencedirect.com/topics) — pages de synthèse en accès libre sur des notions comme l'indice de productivité, l'IPR, la complétion.
- Cours universitaires publics de pétrophysique / ingénierie de réservoir (chercher `filetype:pdf` + nom de l'université).
- Manuels historiques de l'API (American Petroleum Institute) tombés dans le domaine public.

## Colonne "Accès" — à vérifier avant d'indexer

Préciser pour chaque source : `Libre` (aucune restriction), `Libre avec attribution`,
ou `À vérifier`. Ne pas indexer un document dont le statut n'est pas clair —
en cas de doute, en discuter avec l'équipe avant le Jour 2.

## Format de dépôt

- Un fichier par source dans `docs/corpus/raw/` (PDF ou `.txt`/`.md`).
- Nom de fichier : `NN_slug-du-titre.pdf` (ex. `01_petrowiki-productivity-index.pdf`), `NN` correspondant au numéro de la ligne ci-dessus.
- Le dossier `docs/corpus/processed/` est réservé aux chunks générés au Jour 2 (indexation RAG) — ne pas y déposer de fichiers manuellement.
