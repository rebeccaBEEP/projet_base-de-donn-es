
"""
Application console — Gestion de la Plateforme de Streaming Musical
Auteur : REBECCA KOUADIO & FATOU KA
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME",     "streaming_musical"),
    "charset":  "utf8mb4",
}

# ─────────────────────────────────────────────
#  CONNEXION RESILIENTE
# ─────────────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"\n  X  Connexion impossible : {e}")
        print("  Verifiez que MySQL est demarre et que DB_CONFIG est correct.")
        return None

def connexion_active(conn):
    try:
        if conn is None or not conn.is_connected():
            print("  !  Connexion perdue - tentative de reconnexion...")
            conn = get_connection()
            if conn:
                print("  OK  Reconnexion reussie.")
        return conn
    except Error:
        return None

def executer_lecture(conn, sql, params=None):
    conn = connexion_active(conn)
    if conn is None:
        print("  X  Pas de connexion disponible.")
        return conn, []
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return conn, rows
    except Error as e:
        print(f"  X  Erreur de lecture : {e}")
        return conn, []

def executer_ecriture(conn, sql, params=None):
    conn = connexion_active(conn)
    if conn is None:
        print("  X  Pas de connexion disponible.")
        return conn, None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return conn, last_id
    except Error as e:
        try:
            conn.rollback()
        except Error:
            pass
        print(f"  X  Erreur : {e}")
        return conn, None

# ─────────────────────────────────────────────
#  AFFICHAGE
# ─────────────────────────────────────────────
SEP  = "-" * 68
DSEP = "=" * 68

def print_header(title):
    print(f"\n{DSEP}\n  {title}\n{DSEP}")

def print_section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def print_table(rows, headers):
    if not rows:
        print("  (Aucun resultat)")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell) if cell is not None else "NULL"))
    sep  = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    hdr  = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep); print(hdr); print(sep)
    for row in rows:
        cells = [str(c).ljust(widths[i]) if c is not None else "NULL".ljust(widths[i]) for i, c in enumerate(row)]
        print("| " + " | ".join(cells) + " |")
    print(sep)
    print(f"  {len(rows)} enregistrement(s).")

def pause():
    input("\n  Appuyez sur [Entree] pour continuer...")

def saisir(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("  !  Champ obligatoire.")

def saisir_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            v = int(input(prompt).strip())
            if min_val is not None and v < min_val:
                print(f"  !  Minimum : {min_val}")
                continue
            if max_val is not None and v > max_val:
                print(f"  !  Maximum : {max_val}")
                continue
            return v
        except ValueError:
            print("  !  Entier attendu.")


# =============================================================
#  MODULE ARTISTES
# =============================================================

def menu_artistes(conn):
    while True:
        print_header("GESTION DES ARTISTES")
        print("  1. Lister tous les artistes")
        print("  2. Rechercher par nom (mot-cle)")
        print("  3. Detail d'un artiste + ses albums")
        print("  4. Ajouter un artiste")
        print("  5. Modifier un artiste")
        print("  6. Supprimer un artiste")
        print("  7. Classement top auditeurs mensuels")
        print("  8. Certifier / decertifier un artiste")
        print("  0. Retour")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = lister_artistes(conn)
        elif c == "2": conn = rechercher_artiste(conn)
        elif c == "3": conn = detail_artiste(conn)
        elif c == "4": conn = ajouter_artiste(conn)
        elif c == "5": conn = modifier_artiste(conn)
        elif c == "6": conn = supprimer_artiste(conn)
        elif c == "7": conn = classement_artistes(conn)
        elif c == "8": conn = certifier_artiste(conn)
        elif c == "0": break
        else: print("  !  Option invalide.")
    return conn

def lister_artistes(conn):
    print_section("Liste de tous les artistes (ordre alphabetique)")
    conn, rows = executer_lecture(conn, """
        SELECT id_Artiste, nom_Artiste, paysOrigine_Artiste,
               nb_auditeurs_mensuels,
               IF(est_verifie, 'Oui', 'Non') AS verifie
        FROM Artiste ORDER BY nom_Artiste ASC
    """)
    print_table(rows, ["ID", "Nom", "Pays", "Auditeurs/mois", "Verifie"])
    pause()
    return conn

def rechercher_artiste(conn):
    print_section("Recherche d'un artiste par mot-cle")
    mot = saisir("  Mot-cle : ")
    conn, rows = executer_lecture(conn, """
        SELECT id_Artiste, nom_Artiste, paysOrigine_Artiste, nb_auditeurs_mensuels
        FROM Artiste WHERE nom_Artiste LIKE %s ORDER BY nom_Artiste
    """, (f"%{mot}%",))
    print_table(rows, ["ID", "Nom", "Pays", "Auditeurs/mois"])
    pause()
    return conn

def detail_artiste(conn):
    print_section("Detail d'un artiste et ses albums")
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, rows = executer_lecture(conn, """
        SELECT id_Artiste, nom_Artiste, biographie_artiste,
               paysOrigine_Artiste, Date_debut_Artiste,
               nb_auditeurs_mensuels, IF(est_verifie, 'Oui', 'Non') AS verifie
        FROM Artiste WHERE id_Artiste = %s
    """, (id_art,))
    if not rows:
        print(f"  !  Artiste #{id_art} introuvable.")
        pause(); return conn
    r = rows[0]
    print(f"\n  Artiste #{r[0]}")
    print(f"  Nom       : {r[1]}")
    print(f"  Bio       : {str(r[2] or 'N/A')[:70]}")
    print(f"  Pays      : {r[3] or 'N/A'}")
    print(f"  Debut     : {r[4] or 'N/A'}")
    print(f"  Auditeurs : {r[5]:,}")
    print(f"  Verifie   : {r[6]}")
    conn, albums = executer_lecture(conn, """
        SELECT al.id_album, al.titre, al.type_album, al.DateSortie_album,
               COUNT(m.id_morceau) AS nb_morceaux
        FROM Album al LEFT JOIN Morceau m ON al.id_album = m.id_album
        WHERE al.id_Artiste = %s
        GROUP BY al.id_album, al.titre, al.type_album, al.DateSortie_album
        ORDER BY al.DateSortie_album DESC
    """, (id_art,))
    print(f"\n  Albums ({len(albums)}) :")
    if albums:
        print_table(albums, ["ID", "Titre", "Type", "Date sortie", "Morceaux"])
    else:
        print("  (Aucun album)")
    pause()
    return conn

def ajouter_artiste(conn):
    print_section("Ajouter un artiste")
    nom   = saisir("  Nom de scene      : ")
    pays  = saisir("  Pays d'origine    : ")
    bio   = input("  Biographie (opt.) : ").strip() or None
    date_ = input("  Date debut carriere (AAAA-MM-JJ, opt.) : ").strip() or None
    if date_:
        try: datetime.strptime(date_, "%Y-%m-%d")
        except ValueError: print("  !  Date invalide, ignoree."); date_ = None
    conn, id_ = executer_ecriture(conn, """
        INSERT INTO Artiste (nom_Artiste, biographie_artiste, paysOrigine_Artiste,
                             Date_debut_Artiste, nb_auditeurs_mensuels, est_verifie)
        VALUES (%s, %s, %s, %s, 0, 0)
    """, (nom, bio, pays, date_))
    if id_ is not None:
        print(f"\n  OK  Artiste '{nom}' ajoute (ID : {id_}).")
    pause()
    return conn

def modifier_artiste(conn):
    print_section("Modifier un artiste")
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT nom_Artiste, paysOrigine_Artiste, biographie_artiste FROM Artiste WHERE id_Artiste = %s",
        (id_art,))
    if not rows:
        print(f"  !  Artiste #{id_art} introuvable.")
        pause(); return conn
    r = rows[0]
    nv_nom  = input(f"  Nom   (Entree = garder '{r[0]}') : ").strip() or r[0]
    nv_pays = input(f"  Pays  (Entree = garder '{r[1] or ''}') : ").strip() or r[1]
    nv_bio  = input(f"  Bio   (Entree = garder) : ").strip() or r[2]
    conn, _ = executer_ecriture(conn, """
        UPDATE Artiste SET nom_Artiste=%s, paysOrigine_Artiste=%s, biographie_artiste=%s
        WHERE id_Artiste=%s
    """, (nv_nom, nv_pays, nv_bio, id_art))
    if _ is not None:
        print(f"\n  OK  Artiste #{id_art} mis a jour.")
    pause()
    return conn

def supprimer_artiste(conn):
    print_section("Supprimer un artiste")
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT nom_Artiste FROM Artiste WHERE id_Artiste = %s", (id_art,))
    if not rows:
        print(f"  !  Artiste #{id_art} introuvable.")
        pause(); return conn
    if input(f"  Supprimer '{rows[0][0]}' ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "DELETE FROM Artiste WHERE id_Artiste = %s", (id_art,))
    if _ is not None:
        print(f"\n  OK  Artiste #{id_art} supprime.")
    pause()
    return conn

def classement_artistes(conn):
    print_section("Top artistes - auditeurs mensuels")
    conn, rows = executer_lecture(conn, """
        SELECT RANK() OVER (ORDER BY nb_auditeurs_mensuels DESC) AS rang,
               nom_Artiste, paysOrigine_Artiste, nb_auditeurs_mensuels,
               IF(est_verifie, 'OUI', '') AS verifie,
               (SELECT COUNT(*) FROM Album al WHERE al.id_Artiste = a.id_Artiste) AS nb_albums
        FROM Artiste a
        ORDER BY nb_auditeurs_mensuels DESC LIMIT 20
    """)
    print_table(rows, ["#", "Artiste", "Pays", "Auditeurs/mois", "Verifie", "Albums"])
    pause()
    return conn

def certifier_artiste(conn):
    print_section("Certifier / Decertifier un artiste")
    conn, artistes = executer_lecture(conn, """
        SELECT id_Artiste, nom_Artiste,
               IF(est_verifie, 'Certifie', 'Non certifie') AS statut
        FROM Artiste ORDER BY nom_Artiste
    """)
    print_table(artistes, ["ID", "Artiste", "Statut actuel"])
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT nom_Artiste, est_verifie FROM Artiste WHERE id_Artiste = %s", (id_art,))
    if not rows:
        print(f"  !  Artiste #{id_art} introuvable.")
        pause(); return conn
    nom, statut_actuel = rows[0]
    nouveau_statut = 0 if statut_actuel else 1
    action = "certifier" if nouveau_statut else "retirer la certification de"
    if input(f"  Voulez-vous {action} '{nom}' ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "UPDATE Artiste SET est_verifie = %s WHERE id_Artiste = %s",
        (nouveau_statut, id_art))
    if _ is not None:
        label = "Certifie" if nouveau_statut else "Certification retiree"
        print(f"  OK  {nom} - {label}.")
    pause()
    return conn


# =============================================================
#  MODULE ALBUMS
# =============================================================

def menu_albums(conn):
    while True:
        print_header("GESTION DES ALBUMS")
        print("  1. Lister tous les albums")
        print("  2. Albums d'un artiste")
        print("  3. Detail d'un album (morceaux inclus)")
        print("  4. Ajouter un album a un artiste")
        print("  5. Modifier un album")
        print("  6. Supprimer un album")
        print("  0. Retour")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = lister_albums(conn)
        elif c == "2": conn = albums_par_artiste(conn)
        elif c == "3": conn = detail_album(conn)
        elif c == "4": conn = ajouter_album(conn)
        elif c == "5": conn = modifier_album(conn)
        elif c == "6": conn = supprimer_album(conn)
        elif c == "0": break
        else: print("  !  Option invalide.")
    return conn

def lister_albums(conn):
    print_section("Liste de tous les albums")
    conn, rows = executer_lecture(conn, """
        SELECT al.id_album, al.titre, ar.nom_Artiste,
               al.type_album, al.DateSortie_album,
               COUNT(m.id_morceau) AS nb_morceaux
        FROM Album al
        JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        LEFT JOIN Morceau m ON al.id_album = m.id_album
        GROUP BY al.id_album, al.titre, ar.nom_Artiste, al.type_album, al.DateSortie_album
        ORDER BY al.DateSortie_album DESC
    """)
    print_table(rows, ["ID", "Titre", "Artiste", "Type", "Date sortie", "Morceaux"])
    pause()
    return conn

def albums_par_artiste(conn):
    print_section("Albums d'un artiste")
    conn, artistes = executer_lecture(conn,
        "SELECT id_Artiste, nom_Artiste FROM Artiste ORDER BY nom_Artiste")
    print_table(artistes, ["ID", "Artiste"])
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, rows = executer_lecture(conn, """
        SELECT al.id_album, al.titre, al.type_album, al.DateSortie_album,
               COUNT(m.id_morceau) AS nb_morceaux
        FROM Album al LEFT JOIN Morceau m ON al.id_album = m.id_album
        WHERE al.id_Artiste = %s
        GROUP BY al.id_album, al.titre, al.type_album, al.DateSortie_album
        ORDER BY al.DateSortie_album DESC
    """, (id_art,))
    if not rows:
        print("  (Aucun album pour cet artiste)")
    else:
        print_table(rows, ["ID Album", "Titre", "Type", "Date sortie", "Morceaux"])
    pause()
    return conn

def detail_album(conn):
    print_section("Detail d'un album")
    id_album = saisir_int("  ID de l'album : ", min_val=1)
    conn, infos = executer_lecture(conn, """
        SELECT al.id_album, al.titre, al.type_album, al.DateSortie_album,
               ar.nom_Artiste, COUNT(m.id_morceau) AS nb_morceaux
        FROM Album al
        JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        LEFT JOIN Morceau m ON al.id_album = m.id_album
        WHERE al.id_album = %s
        GROUP BY al.id_album, al.titre, al.type_album, al.DateSortie_album, ar.nom_Artiste
    """, (id_album,))
    if not infos:
        print(f"  !  Album #{id_album} introuvable.")
        pause(); return conn
    i = infos[0]
    print(f"\n  Album #{i[0]}")
    print(f"  Titre    : {i[1]}")
    print(f"  Type     : {i[2]}")
    print(f"  Sortie   : {i[3]}")
    print(f"  Artiste  : {i[4]}")
    print(f"  Morceaux : {i[5]}")
    conn, morceaux = executer_lecture(conn, """
        SELECT numero_piste, titre_morceau,
               CONCAT(dureeSeconde_morceau DIV 60,'min ',
                      dureeSeconde_morceau MOD 60,'s') AS duree,
               IF(explicit_morceau,'E','') AS expl,
               nbEcouteTotal_morceau
        FROM Morceau WHERE id_album = %s ORDER BY numero_piste
    """, (id_album,))
    if morceaux:
        print()
        print_table(morceaux, ["Piste", "Titre", "Duree", "Expl.", "Ecoutes"])
    else:
        print("\n  (Aucun morceau dans cet album)")
    pause()
    return conn

def ajouter_album(conn):
    print_section("Ajouter un album a un artiste")
    conn, artistes = executer_lecture(conn,
        "SELECT id_Artiste, nom_Artiste, paysOrigine_Artiste FROM Artiste ORDER BY nom_Artiste")
    print_table(artistes, ["ID", "Artiste", "Pays"])
    id_art = saisir_int("  ID de l'artiste : ", min_val=1)
    conn, check = executer_lecture(conn,
        "SELECT nom_Artiste FROM Artiste WHERE id_Artiste = %s", (id_art,))
    if not check:
        print(f"  !  Artiste #{id_art} introuvable.")
        pause(); return conn
    print(f"  Artiste selectionne : {check[0][0]}")
    titre = saisir("  Titre de l'album  : ")
    print("  Type : 1=Album  2=EP  3=Single  4=Compilation")
    type_choix = saisir_int("  Choix : ", min_val=1, max_val=4)
    types = {1:'Album', 2:'EP', 3:'Single', 4:'Compilation'}
    type_album = types[type_choix]
    date_sortie = saisir("  Date de sortie (AAAA-MM-JJ) : ")
    try:
        datetime.strptime(date_sortie, "%Y-%m-%d")
    except ValueError:
        print("  !  Date invalide."); pause(); return conn
    couverture = input("  URL couverture (opt.) : ").strip() or None
    conn, id_al = executer_ecriture(conn, """
        INSERT INTO Album (titre, DateSortie_album, type_album,
                           imagesCouverture_album, id_Artiste)
        VALUES (%s, %s, %s, %s, %s)
    """, (titre, date_sortie, type_album, couverture, id_art))
    if id_al is not None:
        print(f"\n  OK  Album '{titre}' ({type_album}) ajoute (ID : {id_al}).")
    pause()
    return conn

def modifier_album(conn):
    print_section("Modifier un album")
    id_album = saisir_int("  ID de l'album : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT titre, type_album, DateSortie_album FROM Album WHERE id_album = %s", (id_album,))
    if not rows:
        print(f"  !  Album #{id_album} introuvable.")
        pause(); return conn
    r = rows[0]
    nv_titre = input(f"  Titre (Entree = garder '{r[0]}') : ").strip() or r[0]
    print(f"  Type actuel : {r[1]}")
    print("  1=Album  2=EP  3=Single  4=Compilation  (Entree = garder)")
    type_s = input("  Nouveau type : ").strip()
    types = {'1':'Album','2':'EP','3':'Single','4':'Compilation'}
    nv_type = types.get(type_s, r[1])
    nv_date = input(f"  Date sortie (Entree = garder {r[2]}) : ").strip() or str(r[2])
    conn, _ = executer_ecriture(conn, """
        UPDATE Album SET titre=%s, type_album=%s, DateSortie_album=%s WHERE id_album=%s
    """, (nv_titre, nv_type, nv_date, id_album))
    if _ is not None:
        print(f"\n  OK  Album #{id_album} mis a jour.")
    pause()
    return conn

def supprimer_album(conn):
    print_section("Supprimer un album")
    id_album = saisir_int("  ID de l'album : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT titre FROM Album WHERE id_album = %s", (id_album,))
    if not rows:
        print(f"  !  Album #{id_album} introuvable.")
        pause(); return conn
    print("  !  Attention : les morceaux de cet album seront mis a NULL.")
    if input(f"  Supprimer '{rows[0][0]}' ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "DELETE FROM Album WHERE id_album = %s", (id_album,))
    if _ is not None:
        print(f"\n  OK  Album #{id_album} supprime.")
    pause()
    return conn


# =============================================================
#  MODULE MORCEAUX
# =============================================================

def menu_morceaux(conn):
    while True:
        print_header("GESTION DES MORCEAUX")
        print("  1. Lister les morceaux d'un album")
        print("  2. Rechercher un morceau par titre")
        print("  3. Detail d'un morceau (genres inclus)")
        print("  4. Ajouter un morceau")
        print("  5. Modifier un morceau")
        print("  6. Supprimer un morceau")
        print("  7. Top 10 morceaux les plus ecoutes")
        print("  8. Morceaux > duree moyenne (R11)")
        print("  0. Retour")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = morceaux_par_album(conn)
        elif c == "2": conn = rechercher_morceau(conn)
        elif c == "3": conn = detail_morceau(conn)
        elif c == "4": conn = ajouter_morceau(conn)
        elif c == "5": conn = modifier_morceau(conn)
        elif c == "6": conn = supprimer_morceau(conn)
        elif c == "7": conn = top_morceaux(conn)
        elif c == "8": conn = morceaux_dessus_moyenne(conn)
        elif c == "0": break
        else: print("  !  Option invalide.")
    return conn

def morceaux_par_album(conn):
    print_section("Morceaux d'un album")
    id_album = saisir_int("  ID de l'album : ", min_val=1)
    conn, rows = executer_lecture(conn, """
        SELECT m.id_morceau, m.numero_piste, m.titre_morceau,
               CONCAT(m.dureeSeconde_morceau DIV 60,'min ',
                      m.dureeSeconde_morceau MOD 60,'s') AS duree,
               IF(m.explicit_morceau, 'E', '') AS expl,
               m.nbEcouteTotal_morceau
        FROM Morceau m WHERE m.id_album = %s ORDER BY m.numero_piste ASC
    """, (id_album,))
    print_table(rows, ["ID", "Piste", "Titre", "Duree", "Expl.", "Ecoutes"])
    pause()
    return conn

def rechercher_morceau(conn):
    print_section("Recherche de morceau par titre")
    mot = saisir("  Mot-cle : ")
    conn, rows = executer_lecture(conn, """
        SELECT m.id_morceau, m.titre_morceau, ar.nom_Artiste, al.titre AS album,
               CONCAT(m.dureeSeconde_morceau DIV 60,'min ',
                      m.dureeSeconde_morceau MOD 60,'s') AS duree,
               m.nbEcouteTotal_morceau
        FROM Morceau m
        JOIN Album al   ON m.id_album    = al.id_album
        JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        WHERE m.titre_morceau LIKE %s ORDER BY m.nbEcouteTotal_morceau DESC
    """, (f"%{mot}%",))
    print_table(rows, ["ID", "Titre", "Artiste", "Album", "Duree", "Ecoutes"])
    pause()
    return conn

def detail_morceau(conn):
    print_section("Detail d'un morceau")
    id_m = saisir_int("  ID du morceau : ", min_val=1)
    conn, rows = executer_lecture(conn, """
        SELECT m.id_morceau, m.titre_morceau, m.dureeSeconde_morceau,
               m.numero_piste, IF(m.explicit_morceau,'Oui','Non'),
               m.nbEcouteTotal_morceau, al.titre, al.type_album, ar.nom_Artiste
        FROM Morceau m
        JOIN Album al   ON m.id_album    = al.id_album
        JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        WHERE m.id_morceau = %s
    """, (id_m,))
    if not rows:
        print(f"  !  Morceau #{id_m} introuvable.")
        pause(); return conn
    r = rows[0]
    print(f"\n  Morceau #{r[0]}")
    print(f"  Titre   : {r[1]}")
    print(f"  Duree   : {r[2]//60}min {r[2]%60}s")
    print(f"  Piste   : #{r[3]}")
    print(f"  Explicit: {r[4]}")
    print(f"  Ecoutes : {r[5]:,}")
    print(f"  Album   : {r[6]} ({r[7]})")
    print(f"  Artiste : {r[8]}")
    conn, genres = executer_lecture(conn, """
        SELECT g.nom_genre FROM Genre g
        JOIN categorise c ON g.id_genre = c.id_genre
        WHERE c.id_morceau = %s
    """, (id_m,))
    print(f"\n  Genres : {', '.join(g[0] for g in genres) if genres else 'Non classifie'}")
    pause()
    return conn

def ajouter_morceau(conn):
    print_section("Ajouter un morceau")
    conn, albums = executer_lecture(conn, """
        SELECT al.id_album, al.titre, ar.nom_Artiste
        FROM Album al JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        ORDER BY ar.nom_Artiste, al.titre
    """)
    print_table(albums, ["ID Album", "Titre", "Artiste"])
    id_album = saisir_int("  ID de l'album : ", min_val=1)
    titre    = saisir("  Titre du morceau  : ")
    duree    = saisir_int("  Duree (secondes)  : ", min_val=1)
    piste    = saisir_int("  N de piste        : ", min_val=1)
    explicit = input("  Explicit ? (o/n)   : ").strip().lower() == "o"
    url      = saisir("  URL fichier audio  : ")
    conn, id_m = executer_ecriture(conn, """
        INSERT INTO Morceau (titre_morceau, dureeSeconde_morceau, numero_piste,
             explicit_morceau, nbEcouteTotal_morceau, url_fichiers_morceau, id_album)
        VALUES (%s, %s, %s, %s, 0, %s, %s)
    """, (titre, duree, piste, explicit, url, id_album))
    if id_m is None:
        pause(); return conn
    print(f"\n  OK  Morceau '{titre}' ajoute (ID : {id_m}).")
    if input("  Associer des genres ? (o/n) : ").strip().lower() == "o":
        conn, genres = executer_lecture(conn,
            "SELECT id_genre, nom_genre FROM Genre ORDER BY nom_genre")
        print_table(genres, ["ID", "Genre"])
        while True:
            gid = input("  ID genre (0 = terminer) : ").strip()
            if gid == "0": break
            if gid.isdigit():
                conn, _ = executer_ecriture(conn,
                    "INSERT INTO categorise (id_morceau, id_genre) VALUES (%s, %s)",
                    (id_m, int(gid)))
                if _ is not None: print("  OK  Genre associe.")
    pause()
    return conn

def modifier_morceau(conn):
    print_section("Modifier un morceau")
    id_m = saisir_int("  ID du morceau : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT titre_morceau, dureeSeconde_morceau, explicit_morceau FROM Morceau WHERE id_morceau = %s",
        (id_m,))
    if not rows:
        print(f"  !  Morceau #{id_m} introuvable.")
        pause(); return conn
    r = rows[0]
    nv_titre = input(f"  Titre  (Entree = garder '{r[0]}') : ").strip() or r[0]
    nv_duree_s = input(f"  Duree  (Entree = garder {r[1]}s) : ").strip()
    nv_duree = int(nv_duree_s) if nv_duree_s.isdigit() and int(nv_duree_s) > 0 else r[1]
    expl_s = input("  Explicit ? o/n (Entree = garder) : ").strip().lower()
    nv_expl = (expl_s == "o") if expl_s in ("o", "n") else r[2]
    conn, _ = executer_ecriture(conn, """
        UPDATE Morceau SET titre_morceau=%s, dureeSeconde_morceau=%s, explicit_morceau=%s
        WHERE id_morceau=%s
    """, (nv_titre, nv_duree, nv_expl, id_m))
    if _ is not None:
        print(f"\n  OK  Morceau #{id_m} mis a jour.")
    pause()
    return conn

def supprimer_morceau(conn):
    print_section("Supprimer un morceau")
    id_m = saisir_int("  ID du morceau : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT titre_morceau FROM Morceau WHERE id_morceau = %s", (id_m,))
    if not rows:
        print(f"  !  Morceau #{id_m} introuvable.")
        pause(); return conn
    if input(f"  Supprimer '{rows[0][0]}' ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "DELETE FROM Morceau WHERE id_morceau = %s", (id_m,))
    if _ is not None:
        print(f"\n  OK  Morceau #{id_m} supprime.")
    pause()
    return conn

def top_morceaux(conn):
    print_section("Top 10 morceaux les plus ecoutes")
    conn, rows = executer_lecture(conn, """
        SELECT RANK() OVER (ORDER BY m.nbEcouteTotal_morceau DESC) AS rang,
               m.titre_morceau, ar.nom_Artiste, al.titre AS album,
               m.nbEcouteTotal_morceau
        FROM Morceau m
        JOIN Album al   ON m.id_album    = al.id_album
        JOIN Artiste ar ON al.id_Artiste = ar.id_Artiste
        ORDER BY m.nbEcouteTotal_morceau DESC LIMIT 10
    """)
    print_table(rows, ["#", "Titre", "Artiste", "Album", "Ecoutes"])
    pause()
    return conn

def morceaux_dessus_moyenne(conn):
    print_section("Morceaux dont la duree > duree moyenne globale (R11)")
    conn, rows = executer_lecture(conn, """
        SELECT id_morceau, titre_morceau, dureeSeconde_morceau,
               ROUND((SELECT AVG(dureeSeconde_morceau) FROM Morceau), 1) AS moy_globale
        FROM Morceau
        WHERE dureeSeconde_morceau > (SELECT AVG(dureeSeconde_morceau) FROM Morceau)
        ORDER BY dureeSeconde_morceau DESC
    """)
    print_table(rows, ["ID", "Titre", "Duree (s)", "Moy. globale (s)"])
    pause()
    return conn


# =============================================================
#  MODULE UTILISATEURS
# =============================================================

def menu_utilisateurs(conn):
    while True:
        print_header("GESTION DES UTILISATEURS")
        print("  1. Lister tous les utilisateurs")
        print("  2. Rechercher par nom / email")
        print("  3. Detail d'un utilisateur")
        print("  4. Ajouter un utilisateur")
        print("  5. Modifier un utilisateur")
        print("  6. Supprimer un utilisateur")
        print("  7. Statistiques abonnements / revenus")
        print("  8. Classement utilisateurs par ecoutes (R13)")
        print("  0. Retour")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = lister_utilisateurs(conn)
        elif c == "2": conn = rechercher_utilisateur(conn)
        elif c == "3": conn = detail_utilisateur(conn)
        elif c == "4": conn = ajouter_utilisateur(conn)
        elif c == "5": conn = modifier_utilisateur(conn)
        elif c == "6": conn = supprimer_utilisateur(conn)
        elif c == "7": conn = stats_abonnements(conn)
        elif c == "8": conn = classement_utilisateurs(conn)
        elif c == "0": break
        else: print("  !  Option invalide.")
    return conn

def lister_utilisateurs(conn):
    print_section("Liste de tous les utilisateurs")
    conn, rows = executer_lecture(conn, """
        SELECT u.id_utilisateur,
               CONCAT(u.prenom_utilisateur, ' ', u.nom_utilisateur) AS nom_complet,
               u.email_utilisateur, u.pays, u.dateInscription_utilisateur,
               COALESCE(ab.nomPlan_abonmt, 'N/A') AS plan
        FROM Utilisateur u
        LEFT JOIN Souscription s ON u.id_utilisateur = s.id_utilisateur AND s.est_actif = 1
        LEFT JOIN Abonnement ab  ON s.id_abonmt = ab.id_abonmt
        ORDER BY u.nom_utilisateur, u.prenom_utilisateur
    """)
    print_table(rows, ["ID", "Nom complet", "Email", "Pays", "Inscription", "Plan"])
    pause()
    return conn

def rechercher_utilisateur(conn):
    print_section("Recherche d'un utilisateur")
    mot = saisir("  Mot-cle (nom ou email) : ")
    conn, rows = executer_lecture(conn, """
        SELECT id_utilisateur,
               CONCAT(prenom_utilisateur, ' ', nom_utilisateur) AS nom_complet,
               email_utilisateur, pays
        FROM Utilisateur
        WHERE nom_utilisateur LIKE %s OR prenom_utilisateur LIKE %s OR email_utilisateur LIKE %s
        ORDER BY nom_utilisateur, prenom_utilisateur
    """, (f"%{mot}%",)*3)
    print_table(rows, ["ID", "Nom complet", "Email", "Pays"])
    pause()
    return conn

def detail_utilisateur(conn):
    print_section("Detail d'un utilisateur")
    id_u = saisir_int("  ID de l'utilisateur : ", min_val=1)
    conn, rows = executer_lecture(conn, """
        SELECT u.id_utilisateur, u.prenom_utilisateur, u.nom_utilisateur,
               u.email_utilisateur, u.pays,
               u.dateInscription_utilisateur, u.dateNaissance_utilisateur,
               COALESCE(ab.nomPlan_abonmt, 'Aucun') AS plan_actif,
               (SELECT COUNT(*) FROM Playlist p WHERE p.id_utilisateur = u.id_utilisateur),
               (SELECT COUNT(*) FROM Ecoute e   WHERE e.id_utilisateur = u.id_utilisateur),
               (SELECT COUNT(*) FROM suivre sv  WHERE sv.id_utilisateur = u.id_utilisateur)
        FROM Utilisateur u
        LEFT JOIN Souscription s ON u.id_utilisateur = s.id_utilisateur AND s.est_actif = 1
        LEFT JOIN Abonnement ab  ON s.id_abonmt = ab.id_abonmt
        WHERE u.id_utilisateur = %s
    """, (id_u,))
    if not rows:
        print(f"  !  Utilisateur #{id_u} introuvable.")
        pause(); return conn
    r = rows[0]
    print(f"\n  Utilisateur #{r[0]}")
    print(f"  Nom         : {r[1]} {r[2]}")
    print(f"  Email       : {r[3]}")
    print(f"  Pays        : {r[4] or 'N/A'}")
    print(f"  Inscription : {r[5]}")
    print(f"  Naissance   : {r[6] or 'N/A'}")
    print(f"  Plan actif  : {r[7]}")
    print(f"  Playlists   : {r[8]}")
    print(f"  Ecoutes     : {r[9]:,}")
    print(f"  Artistes suivis : {r[10]}")
    pause()
    return conn

def ajouter_utilisateur(conn):
    print_section("Ajouter un utilisateur")
    prenom = saisir("  Prenom        : ")
    nom    = saisir("  Nom           : ")
    email  = saisir("  Email         : ")
    mdp    = saisir("  Mot de passe  : ")
    pays   = input("  Pays (opt.)   : ").strip() or None
    ddn    = saisir("  Date naissance (AAAA-MM-JJ) : ")
    try: datetime.strptime(ddn, "%Y-%m-%d")
    except ValueError: print("  !  Date invalide."); pause(); return conn
    conn, id_u = executer_ecriture(conn, """
        INSERT INTO Utilisateur (nom_utilisateur, prenom_utilisateur, email_utilisateur,
             mdp_utilisateur, dateNaissance_utilisateur, dateInscription_utilisateur, pays)
        VALUES (%s, %s, %s, %s, %s, CURDATE(), %s)
    """, (nom, prenom, email, mdp, ddn, pays))
    if id_u is None:
        pause(); return conn
    print(f"\n  OK  Utilisateur '{prenom} {nom}' cree (ID : {id_u}).")
    conn, plans = executer_lecture(conn,
        "SELECT id_abonmt, nomPlan_abonmt, prix_mensuel_abonmt FROM Abonnement ORDER BY prix_mensuel_abonmt")
    print_table(plans, ["ID", "Plan", "Prix euro/mois"])
    id_ab = saisir_int("  ID plan d'abonnement : ", min_val=1)
    conn, _ = executer_ecriture(conn, """
        INSERT INTO Souscription (date_debut, est_actif, id_abonmt, id_utilisateur)
        VALUES (CURDATE(), 1, %s, %s)
    """, (id_ab, id_u))
    if _ is not None:
        print("  OK  Abonnement active.")
    pause()
    return conn

def modifier_utilisateur(conn):
    print_section("Modifier un utilisateur")
    id_u = saisir_int("  ID de l'utilisateur : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT prenom_utilisateur, nom_utilisateur, pays FROM Utilisateur WHERE id_utilisateur = %s",
        (id_u,))
    if not rows:
        print(f"  !  Utilisateur #{id_u} introuvable.")
        pause(); return conn
    r = rows[0]
    nv_prenom = input(f"  Prenom (Entree = garder '{r[0]}') : ").strip() or r[0]
    nv_nom    = input(f"  Nom    (Entree = garder '{r[1]}') : ").strip() or r[1]
    nv_pays   = input(f"  Pays   (Entree = garder '{r[2] or ''}') : ").strip() or r[2]
    conn, _ = executer_ecriture(conn, """
        UPDATE Utilisateur SET prenom_utilisateur=%s, nom_utilisateur=%s, pays=%s
        WHERE id_utilisateur=%s
    """, (nv_prenom, nv_nom, nv_pays, id_u))
    if _ is not None:
        print(f"\n  OK  Utilisateur #{id_u} mis a jour.")
    pause()
    return conn

def supprimer_utilisateur(conn):
    print_section("Supprimer un utilisateur")
    id_u = saisir_int("  ID de l'utilisateur : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT CONCAT(prenom_utilisateur,' ',nom_utilisateur) FROM Utilisateur WHERE id_utilisateur = %s",
        (id_u,))
    if not rows:
        print(f"  !  Utilisateur #{id_u} introuvable.")
        pause(); return conn
    if input(f"  Supprimer '{rows[0][0]}' et toutes ses donnees ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "DELETE FROM Utilisateur WHERE id_utilisateur = %s", (id_u,))
    if _ is not None:
        print(f"\n  OK  Utilisateur #{id_u} supprime.")
    pause()
    return conn

def stats_abonnements(conn):
    print_section("Statistiques - abonnes et revenus par plan")
    conn, rows = executer_lecture(conn, """
        SELECT ab.nomPlan_abonmt, COUNT(s.id_utilisateur) AS nb_abonnes,
               ab.prix_mensuel_abonmt,
               ROUND(COUNT(s.id_utilisateur) * ab.prix_mensuel_abonmt, 2) AS revenu_mensuel
        FROM Abonnement ab
        LEFT JOIN Souscription s ON ab.id_abonmt = s.id_abonmt AND s.est_actif = 1
        GROUP BY ab.id_abonmt, ab.nomPlan_abonmt, ab.prix_mensuel_abonmt
        ORDER BY nb_abonnes DESC
    """)
    print_table(rows, ["Plan", "Abonnes actifs", "Prix euro/mois", "Revenu mensuel euro"])
    pause()
    return conn

def classement_utilisateurs(conn):
    print_section("Classement utilisateurs par nombre d'ecoutes (R13)")
    conn, rows = executer_lecture(conn, """
        SELECT RANK() OVER (
                   ORDER BY COUNT(e.id_ecoute) DESC, SUM(e.duree_ecoute_sec) DESC
               ) AS classement,
               CONCAT(u.prenom_utilisateur, ' ', u.nom_utilisateur) AS utilisateur,
               COUNT(e.id_ecoute)      AS nb_ecoutes,
               SUM(e.duree_ecoute_sec) AS duree_totale_sec
        FROM Utilisateur u
        LEFT JOIN Ecoute e ON u.id_utilisateur = e.id_utilisateur
        GROUP BY u.id_utilisateur, u.nom_utilisateur, u.prenom_utilisateur
        ORDER BY classement
    """)
    print_table(rows, ["#", "Utilisateur", "Nb ecoutes", "Duree totale (s)"])
    pause()
    return conn


# =============================================================
#  MODULE PLAYLISTS
# =============================================================

def menu_playlists(conn):
    while True:
        print_header("GESTION DES PLAYLISTS")
        print("  1. Lister les playlists publiques")
        print("  2. Rechercher une playlist")
        print("  3. Afficher le contenu d'une playlist")
        print("  4. Creer une playlist")
        print("  5. Ajouter un morceau a une playlist")
        print("  6. Supprimer une playlist")
        print("  7. Playlists avec plus de 4 morceaux (R8)")
        print("  0. Retour")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = lister_playlists(conn)
        elif c == "2": conn = rechercher_playlist(conn)
        elif c == "3": conn = detail_playlist(conn)
        elif c == "4": conn = creer_playlist(conn)
        elif c == "5": conn = ajouter_morceau_playlist(conn)
        elif c == "6": conn = supprimer_playlist(conn)
        elif c == "7": conn = playlists_riches(conn)
        elif c == "0": break
        else: print("  !  Option invalide.")
    return conn

def lister_playlists(conn):
    print_section("Playlists publiques")
    conn, rows = executer_lecture(conn, """
        SELECT p.id_playlist, p.nom_playlist,
               CONCAT(u.prenom_utilisateur,' ',u.nom_utilisateur) AS proprio,
               p.date_creation_playlist, COUNT(ct.id_morceau) AS nb_morceaux
        FROM Playlist p
        JOIN Utilisateur u ON p.id_utilisateur = u.id_utilisateur
        LEFT JOIN contient ct ON p.id_playlist = ct.id_playlist
        WHERE p.est_publique = 1
        GROUP BY p.id_playlist, p.nom_playlist, proprio, p.date_creation_playlist
        ORDER BY p.nom_playlist
    """)
    print_table(rows, ["ID", "Nom", "Proprietaire", "Creee le", "Morceaux"])
    pause()
    return conn

def rechercher_playlist(conn):
    print_section("Recherche de playlist")
    mot = saisir("  Mot-cle : ")
    conn, rows = executer_lecture(conn, """
        SELECT p.id_playlist, p.nom_playlist,
               CONCAT(u.prenom_utilisateur,' ',u.nom_utilisateur) AS proprio,
               IF(p.est_publique,'Publique','Privee') AS visibilite
        FROM Playlist p JOIN Utilisateur u ON p.id_utilisateur = u.id_utilisateur
        WHERE p.nom_playlist LIKE %s OR p.description_playlist LIKE %s
        ORDER BY p.nom_playlist
    """, (f"%{mot}%",)*2)
    print_table(rows, ["ID", "Nom", "Proprietaire", "Visibilite"])
    pause()
    return conn

def detail_playlist(conn):
    print_section("Contenu d'une playlist")
    id_p = saisir_int("  ID de la playlist : ", min_val=1)
    conn, infos = executer_lecture(conn, """
        SELECT p.nom_playlist, CONCAT(u.prenom_utilisateur,' ',u.nom_utilisateur),
               p.description_playlist, IF(p.est_publique,'Publique','Privee')
        FROM Playlist p JOIN Utilisateur u ON p.id_utilisateur = u.id_utilisateur
        WHERE p.id_playlist = %s
    """, (id_p,))
    if not infos:
        print(f"  !  Playlist #{id_p} introuvable.")
        pause(); return conn
    i = infos[0]
    print(f"\n  Playlist : {i[0]} - {i[3]}")
    print(f"  Par      : {i[1]}")
    print(f"  Desc     : {i[2] or 'N/A'}")
    conn, rows = executer_lecture(conn, """
        SELECT ct.position_, m.titre_morceau, ar.nom_Artiste,
               CONCAT(m.dureeSeconde_morceau DIV 60,'min ',
                      m.dureeSeconde_morceau MOD 60,'s'),
               ct.date_ajout
        FROM contient ct
        JOIN Morceau m  ON ct.id_morceau  = m.id_morceau
        JOIN Album al   ON m.id_album     = al.id_album
        JOIN Artiste ar ON al.id_Artiste  = ar.id_Artiste
        WHERE ct.id_playlist = %s ORDER BY ct.position_
    """, (id_p,))
    print_table(rows, ["#", "Titre", "Artiste", "Duree", "Ajoute le"])
    pause()
    return conn

def creer_playlist(conn):
    print_section("Creer une playlist")
    id_u = saisir_int("  ID de l'utilisateur proprietaire : ", min_val=1)
    nom  = saisir("  Nom de la playlist : ")
    desc = input("  Description (opt.) : ").strip() or None
    pub  = input("  Publique ? (o/n)   : ").strip().lower() == "o"
    conn, id_p = executer_ecriture(conn, """
        INSERT INTO Playlist (nom_playlist, description_playlist, est_publique,
                              date_creation_playlist, id_utilisateur)
        VALUES (%s, %s, %s, CURDATE(), %s)
    """, (nom, desc, int(pub), id_u))
    if id_p is not None:
        print(f"\n  OK  Playlist '{nom}' creee (ID : {id_p}).")
    pause()
    return conn

def ajouter_morceau_playlist(conn):
    print_section("Ajouter un morceau a une playlist")
    id_p = saisir_int("  ID de la playlist : ", min_val=1)
    id_m = saisir_int("  ID du morceau     : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT MAX(position_) FROM contient WHERE id_playlist = %s", (id_p,))
    max_pos = (rows[0][0] or 0) if rows else 0
    conn, _ = executer_ecriture(conn, """
        INSERT INTO contient (id_morceau, id_playlist, position_, date_ajout)
        VALUES (%s, %s, %s, CURDATE())
    """, (id_m, id_p, max_pos + 1))
    if _ is not None:
        print(f"\n  OK  Morceau ajoute en position {max_pos + 1}.")
    pause()
    return conn

def supprimer_playlist(conn):
    print_section("Supprimer une playlist")
    id_p = saisir_int("  ID de la playlist : ", min_val=1)
    conn, rows = executer_lecture(conn,
        "SELECT nom_playlist FROM Playlist WHERE id_playlist = %s", (id_p,))
    if not rows:
        print(f"  !  Playlist #{id_p} introuvable.")
        pause(); return conn
    if input(f"  Supprimer '{rows[0][0]}' ? (oui/non) : ").strip().lower() != "oui":
        print("  Annule."); pause(); return conn
    conn, _ = executer_ecriture(conn,
        "DELETE FROM Playlist WHERE id_playlist = %s", (id_p,))
    if _ is not None:
        print(f"\n  OK  Playlist #{id_p} supprimee.")
    pause()
    return conn

def playlists_riches(conn):
    print_section("Playlists avec plus de 4 morceaux (R8)")
    conn, rows = executer_lecture(conn, """
        SELECT p.id_playlist, p.nom_playlist,
               CONCAT(u.prenom_utilisateur,' ',u.nom_utilisateur) AS proprio,
               COUNT(ct.id_morceau) AS nb_morceaux
        FROM Playlist p
        JOIN contient    ct ON p.id_playlist    = ct.id_playlist
        JOIN Utilisateur u  ON p.id_utilisateur = u.id_utilisateur
        GROUP BY p.id_playlist, p.nom_playlist, proprio
        HAVING COUNT(ct.id_morceau) > 4
        ORDER BY nb_morceaux DESC
    """)
    print_table(rows, ["ID", "Nom", "Proprietaire", "Morceaux"])
    pause()
    return conn


# =============================================================
#  MENU PRINCIPAL
# =============================================================

def menu_principal(conn):
    while True:
        print_header("PLATEFORME STREAMING MUSICAL - ALSI61")
        print(f"  Base : {DB_CONFIG['database']}  |  Hote : {DB_CONFIG['host']}")
        print()
        print("  1. Gestion des Artistes")
        print("  2. Gestion des Albums")
        print("  3. Gestion des Morceaux")
        print("  4. Gestion des Utilisateurs")
        print("  5. Gestion des Playlists")
        print()
        print("  0. Quitter")
        c = input("\n  Votre choix : ").strip()
        if   c == "1": conn = menu_artistes(conn)
        elif c == "2": conn = menu_albums(conn)
        elif c == "3": conn = menu_morceaux(conn)
        elif c == "4": conn = menu_utilisateurs(conn)
        elif c == "5": conn = menu_playlists(conn)
        elif c == "0": print("\n  Au revoir !\n"); break
        else: print("  !  Option invalide.")
    return conn


# =============================================================
#  POINT D'ENTREE
# =============================================================

if __name__ == "__main__":
    print(DSEP)
    conn = None
    while conn is None:
        print("  Connexion a la base de donnees...")
        conn = get_connection()
        if conn is None:
            if input("  Reessayer ? (o/n) : ").strip().lower() != "o":
                print("  Au revoir !\n"); sys.exit(0)
    print(f"  OK  Connecte a MySQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})")
    try:
        menu_principal(conn)
    except KeyboardInterrupt:
        print("\n\n  Interruption clavier - fermeture propre.")
    except Exception as e:
        print(f"\n  X  Erreur inattendue : {e}")
    finally:
        try:
            if conn and conn.is_connected():
                conn.close()
        except Exception:
            pass
        print("  Connexion fermee.")
