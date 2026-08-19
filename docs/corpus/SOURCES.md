# Corpus documentaire — Sources

Tâche Jour 1 (Azra) : lister 5 à 10 documents techniques en accès libre sur la
complétion et la production de puits pétroliers **conventionnels**
(pétrophysique, indice de productivité, pression de fracturation, méthodes de
complétion). Une ligne par document ci-dessous, puis déposer le PDF/texte
correspondant dans `docs/corpus/raw/`.

| # | Titre | Auteur / Organisation | URL | Type | Sujets couverts | Accès |
|---|---|---|---|---|---|---|
| 1 | Reservoir Technologies of the 21st Century | SPE | https://www.spe.org/media/filer_public/58/b7/58b77816-5ec4-49b6-adbe-ba03f3247ef7/reservoir_technologies_of_the_21st_century.pdf | PDF | Vue d'ensemble des technologies de réservoir | Libre |
| 2 | Basic Petrophysics | Slideshare | https://fr.slideshare.net/slideshow/basic-petrophysics/10273848 | HTML (viewer) | Notions de pétrophysique | À vérifier — mis de côté, format non exploitable en l'état |
| 3 | Chap 2 - Productivity Index | Scribd | https://fr.scribd.com/document/961147995/Chap-2-Productivity-Index | HTML (viewer) | Indice de productivité | À vérifier — mis de côté, accès Scribd restreint |
| 4 | Advanced Well Completion Design | Scribd | https://fr.scribd.com/document/640760610/Advanced-Well-Completion-Design | — | Conception de complétion de puits | À vérifier — non téléchargé, accès Scribd restreint |
| 5 | Economides — Stanford Geothermal Workshop (1979) | Stanford University | https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/1979/Economides2.pdf | PDF | Ingénierie de réservoir | Libre |
| 6 | Introduction to Petroleum Engineering | irmat-ucan.com | https://irmat-ucan.com/library/admin/books_pdf/pdf_67b37378e7a242.27494055.pdf | PDF | Cours d'introduction | Libre |
| 7 | Advanced Petroleum Reservoir Engineering (syllabus) | Khazar University | https://khazar.org/uploads/schools/Engineering/Petroleum_Engineering/syllabus/2020/spring/Advanced_Petroleum_Reservoir_Engineering.pdf | PDF | Cours universitaire | Libre |
| 8 | PETE Course Descriptions | Scribd | https://fr.scribd.com/document/179053139/PETE-Course-Descriptions-131-undergrad-pdf | — | Catalogue de cours (contexte) | À vérifier — non téléchargé, faible priorité |
| 9 | Fracturing Pressure (2024, Lei et al.) | Penn State University | https://personal.ems.psu.edu/~fkd/publications/journals/2024_j_rmre_fracturing_pressure_lei.pdf | PDF | Pression de fracturation | Libre |
| 10 | NETL Final Report FE0024311 | NETL / DOE | https://www.netl.doe.gov/sites/default/files/2020-06/FE0024311-Final-Report.pdf | PDF | Rapport technique DOE | Libre |

## État de l'indexation (Jour 1 → 2)

**6 documents indexables déposés dans `docs/corpus/raw/`** : 1, 5, 6, 7, 9, 10.

**4 documents mis de côté** : 2, 3, 4, 8 — sources Scribd/Slideshare dont le
contenu réel n'est pas récupérable par téléchargement direct (page HTML du
viewer, pas le document). Les tentatives HTML brutes (2 et 3) sont conservées
dans `docs/corpus/raw/_a_traiter_plus_tard/` pour un traitement futur
(extraction manuelle si nécessaire). Couverture jugée suffisante sans ces
4 documents : pétrophysique, indice de productivité, pression de
fracturation, et contexte général sont tous couverts par les 6 documents
retenus.

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
- Nom de fichier : `NN_slug-du-titre.pdf` (ex. `01_reservoir_technologies_21st_century.pdf`), `NN` correspondant au numéro de la ligne ci-dessus.
- Le dossier `docs/corpus/processed/` est réservé aux chunks générés au Jour 2 (indexation RAG) — ne pas y déposer de fichiers manuellement.