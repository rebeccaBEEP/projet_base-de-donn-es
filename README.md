# projet_base-de-donn-es
======================================================================
  PROJET — Base de Données : Plateforme de Streaming Musical
  EFREI Paris — INGE-1-APP-BDML
  AUTEUR : REBECCA KOUADIO & FATOU KA
======================================================================

DOMAINE CHOISI
──────────────
Gestion d'une plateforme de streaming musical (inspirée de Spotify /
Deezer). La base modélise les artistes, albums, morceaux, utilisateurs,
abonnements, playlists, écoutes et genres musicaux.

RÈGLES MÉTIER PRINCIPALES
─────────────────────────
- Un utilisateur possède une adresse email unique (RM-U1).
- Un utilisateur est rattaché à exactement un plan actif (RM-U2).
- Un utilisateur doit avoir au moins 13 ans (RM-U3).
- Un artiste est identifié par un nom de scène unique (RM-A1).
- Un album appartient à un seul artiste principal (RM-A2).
- La durée d'un morceau doit être > 0 secondes (RM-AM2).
- Le numéro de piste est unique au sein d'un album (RM-AM3).
- Un morceau peut appartenir à plusieurs genres (RM-AM5).
- Une playlist appartient à un seul utilisateur (RM-P1).
- Un même morceau n'apparaît qu'une seule fois dans une playlist (RM-P2).
- Une écoute est comptabilisée si durée >= 30 secondes (RM-E3).

PRÉREQUIS
─────────
- Python 3.8 ou supérieur
- MySQL 8.0 ou supérieur
- Bibliothèque : mysql-connector-python

INSTALLATION DES DÉPENDANCES
─────────────────────────────
    pip install mysql-connector-python

INITIALISATION DE LA BASE DE DONNÉES
──────────────────────────────────────
1. Ouvrez MySQL Workbench (ou la ligne de commande mysql).
2. Exécutez le script de création :
       source chemin/vers/script_creation.sql
3. Vérifiez que la base "streaming_musical" est bien créée avec des données.

LANCEMENT DE L'APPLICATION
────────────────────────────
Option 1 — Variables d'environnement (recommandé) :

    Windows (PowerShell) :
        $env:DB_HOST="localhost"
        $env:DB_PORT="3306"
        $env:DB_USER="root"
        $env:DB_PASSWORD="votre_mot_de_passe"
        $env:DB_NAME="streaming_musical"
        python src/app.py

    Linux / macOS :
        DB_HOST=localhost DB_USER=root DB_PASSWORD=xxx \
        DB_NAME=streaming_musical python src/app.py

Option 2 — Modifier directement DB_CONFIG dans src/app.py :

    DB_CONFIG = {
        "host":     "localhost",
        "port":     3306,
        "user":     "root",
        "password": "votre_mot_de_passe",
        "database": "streaming_musical",
    }

FONCTIONNALITÉS DE L'APPLICATION
──────────────────────────────────
Module ARTISTES :
  - Lister tous les artistes (tri alphabétique)          → R1
  - Rechercher par mot-clé                               → recherche libre
  - Afficher le détail avec albums associés              → jointure multi-tables
  - Ajouter / Modifier / Supprimer un artiste            → CRUD complet
  - Classement top auditeurs mensuels (RANK())           → statistique globale

Module MORCEAUX :
  - Lister les morceaux d'un album (tri par piste)
  - Rechercher par mot-clé (titre)
  - Afficher le détail avec genres associés
  - Ajouter un morceau (avec association de genres)
  - Modifier / Supprimer un morceau
  - Top 10 morceaux les plus écoutés (RANK())

Module UTILISATEURS :
  - Lister avec plan d'abonnement actif (LEFT JOIN)
  - Rechercher par nom ou email
  - Détail avec compteurs (playlists, écoutes, artistes suivis)
  - Ajouter avec souscription initiale
  - Modifier / Supprimer
  - Statistiques : abonnés et revenu par plan

Module PLAYLISTS :
  - Lister les playlists publiques
  - Rechercher par mot-clé
  - Afficher le contenu (morceaux ordonnés)
  - Créer une playlist
  - Ajouter un morceau (position automatique)
  - Supprimer une playlist



DICTIONNAIRE DES DONNÉES (résumé)
───────────────────────────────────
Tables principales : Utilisateur, Artiste, Album, Morceau, Genre,
                     Playlist, Abonnement, Souscription, Ecoute
Tables de relation : Contient (Playlist×Morceau), Categorise (Morceau×Genre),
                     Suit (Utilisateur×Artiste)

Voir le rapport PDF (Livrable/) pour le dictionnaire complet avec
types SQL et contraintes.

======================================================================
