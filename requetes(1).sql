

USE streaming_musical;

-- R1 - Liste de tous les morceaux triés par ordre alphabétique
-- Approche : SELECT simple avec ORDER BY sur le titre du morceau (entité principale).
SELECT
    id_morceau,
    titre_morceau,
    dureeSeconde_morceau,
    nbEcouteTotal_morceau
FROM Morceau
ORDER BY titre_morceau ASC;


-- R2 - Morceaux ayant plus de 2 milliards d'écoutes totales
-- Approche : Filtre numérique avec WHERE sur nbEcouteTotal_morceau.
SELECT
    id_morceau,
    titre_morceau,
    nbEcouteTotal_morceau
FROM Morceau
WHERE nbEcouteTotal_morceau > 2000000000
ORDER BY nbEcouteTotal_morceau DESC;


-- ============================================================
-- R3 - Tous les morceaux appartenant à un genre donné (id_genre = 3 : Hip-Hop)
-- ============================================================
-- Approche : Jointure avec la table categorise pour filtrer par id_genre.
SELECT
    m.id_morceau,
    m.titre_morceau,
    g.nom_genre
FROM Morceau m
JOIN categorise c ON m.id_morceau = c.id_morceau
JOIN Genre g      ON c.id_genre   = g.id_genre
WHERE g.id_genre = 3
ORDER BY m.titre_morceau;


-- R4 - Morceaux avec leur album et leur artiste (INNER JOIN)

-- Approche : INNER JOIN entre Morceau, Album et Artiste via les FK directes.
--            Seuls les morceaux rattachés à un album apparaissent.
SELECT
    m.titre_morceau,
    m.dureeSeconde_morceau,
    al.titre           AS titre_album,
    al.DateSortie_album,
    ar.nom_Artiste
FROM Morceau  m
JOIN Album    al ON m.id_album      = al.id_album
JOIN Artiste  ar ON al.id_Artiste   = ar.id_Artiste
ORDER BY ar.nom_Artiste, al.titre, m.numero_piste;


-- R5 - Tous les artistes, même sans album publié (LEFT JOIN)
-- Approche : LEFT JOIN depuis Artiste vers Album pour inclure les artistes
--            sans aucun album enregistré dans la base.
SELECT
    ar.id_Artiste,
    ar.nom_Artiste,
    COUNT(al.id_album) AS nb_albums
FROM Artiste ar
LEFT JOIN Album al ON ar.id_Artiste = al.id_Artiste
GROUP BY ar.id_Artiste, ar.nom_Artiste
ORDER BY nb_albums DESC;


-- R6 - Nombre total d'écoutes par genre (agrégat multi-tables)
-- Approche : Jointure Ecoute → Morceau → categorise → Genre,
--            puis COUNT et SUM de la durée écoutée par genre.
SELECT
    g.nom_genre,
    COUNT(e.id_ecoute)      AS nb_ecoutes,
    SUM(e.duree_ecoute_sec) AS duree_totale_sec
FROM Ecoute     e
JOIN Morceau    m ON e.id_morceau = m.id_morceau
JOIN categorise c ON m.id_morceau = c.id_morceau
JOIN Genre      g ON c.id_genre   = g.id_genre
GROUP BY g.id_genre, g.nom_genre
ORDER BY nb_ecoutes DESC;


-- R7 - Nombre de morceaux par genre, trié par ordre décroissant
-- Approche : GROUP BY sur Genre avec COUNT des morceaux via categorise.
SELECT
    g.nom_genre,
    COUNT(c.id_morceau) AS nb_morceaux
FROM Genre g
JOIN categorise c ON g.id_genre = c.id_genre
GROUP BY g.id_genre, g.nom_genre
ORDER BY nb_morceaux DESC;


-- ============================================================
-- R8 - Playlists contenant plus de 4 morceaux
-- ============================================================
-- Approche : GROUP BY sur Playlist puis filtre HAVING sur le COUNT des morceaux.
SELECT
    p.id_playlist,
    p.nom_playlist,
    u.nom_utilisateur,
    COUNT(ct.id_morceau) AS nb_morceaux
FROM Playlist    p
JOIN contient    ct ON p.id_playlist    = ct.id_playlist
JOIN Utilisateur u  ON p.id_utilisateur = u.id_utilisateur
GROUP BY p.id_playlist, p.nom_playlist, u.nom_utilisateur
HAVING COUNT(ct.id_morceau) > 4
ORDER BY nb_morceaux DESC;


-- R9 - Durée moyenne des écoutes par appareil (HAVING > 200 sec)

-- Approche : GROUP BY sur l'appareil, calcul AVG, filtre HAVING.
SELECT
    appareil,
    COUNT(*)                        AS nb_ecoutes,
    ROUND(AVG(duree_ecoute_sec), 2) AS duree_moyenne_sec
FROM Ecoute
GROUP BY appareil
HAVING AVG(duree_ecoute_sec) > 200
ORDER BY duree_moyenne_sec DESC;


-- ============================================================
-- R10 - Morceau le plus long et le plus court par artiste
-- ============================================================
-- Approche : GROUP BY sur Artiste avec MAX/MIN de la durée,
--            jointure Morceau → Album → Artiste via FK directes.
SELECT
    ar.nom_Artiste,
    MAX(m.dureeSeconde_morceau) AS duree_max_sec,
    MIN(m.dureeSeconde_morceau) AS duree_min_sec
FROM Artiste  ar
JOIN Album    al ON ar.id_Artiste = al.id_Artiste
JOIN Morceau  m  ON al.id_album   = m.id_album
GROUP BY ar.id_Artiste, ar.nom_Artiste
ORDER BY duree_max_sec DESC;


-- R11 - Morceaux dont la durée est supérieure à la durée moyenne globale
-- Approche : Sous-requête scalaire dans le WHERE calculant la moyenne globale
--            de dureeSeconde_morceau sur toute la table.
SELECT
    id_morceau,
    titre_morceau,
    dureeSeconde_morceau
FROM Morceau
WHERE dureeSeconde_morceau > (
    SELECT AVG(dureeSeconde_morceau) FROM Morceau
)
ORDER BY dureeSeconde_morceau DESC;


-- R12 - Utilisateurs ayant écouté TOUS les morceaux de la playlist 1

-- Approche : Double NOT EXISTS — pour chaque utilisateur, on vérifie qu'il
--            n'existe aucun morceau de la playlist 1 qu'il n'a pas écouté.
SELECT
    u.id_utilisateur,
    CONCAT(u.prenom_utilisateur, ' ', u.nom_utilisateur) AS utilisateur
FROM Utilisateur u
WHERE NOT EXISTS (
    SELECT ct.id_morceau
    FROM contient ct
    WHERE ct.id_playlist = 1
      AND NOT EXISTS (
          SELECT 1
          FROM Ecoute e
          WHERE e.id_utilisateur = u.id_utilisateur
            AND e.id_morceau     = ct.id_morceau
      )
);


-- R13 - Classement des utilisateurs par nb d'écoutes, départage sur durée totale
-- Approche : Fonction de fenêtre RANK() avec ORDER BY multi-colonnes
--            (nb_ecoutes DESC, puis duree_totale_sec DESC pour les ex-aequo).
SELECT
    RANK() OVER (
        ORDER BY COUNT(e.id_ecoute) DESC, SUM(e.duree_ecoute_sec) DESC
    ) AS classement,
    CONCAT(u.prenom_utilisateur, ' ', u.nom_utilisateur) AS utilisateur,
    COUNT(e.id_ecoute)      AS nb_ecoutes,
    SUM(e.duree_ecoute_sec) AS duree_totale_sec
FROM Utilisateur u
LEFT JOIN Ecoute e ON u.id_utilisateur = e.id_utilisateur
GROUP BY u.id_utilisateur, u.nom_utilisateur, u.prenom_utilisateur
ORDER BY classement;


-- R14 - Morceaux présents dans au moins 2 playlists différentes
-- Approche : Sous-requête corrélée avec COUNT DISTINCT pour compter
--            le nombre de playlists distinctes par morceau.
SELECT
    m.id_morceau,
    m.titre_morceau,
    (
        SELECT COUNT(DISTINCT ct2.id_playlist)
        FROM contient ct2
        WHERE ct2.id_morceau = m.id_morceau
    ) AS nb_playlists
FROM Morceau m
WHERE (
    SELECT COUNT(DISTINCT ct2.id_playlist)
    FROM contient ct2
    WHERE ct2.id_morceau = m.id_morceau
) >= 2
ORDER BY nb_playlists DESC, m.titre_morceau;


-- R15 - Pour chaque artiste, le(s) morceau(x) le(s) plus écouté(s)
--        En cas d'égalité, tous les ex-aequo sont affichés
-- Approche : Sous-requête corrélée qui calcule le MAX de nbEcouteTotal_morceau
--            pour l'artiste courant, puis on garde tous les morceaux atteignant
--            ce maximum (gestion native des égalités).
SELECT
    ar.nom_Artiste,
    m.titre_morceau,
    m.nbEcouteTotal_morceau
FROM Artiste  ar
JOIN Album    al ON ar.id_Artiste = al.id_Artiste
JOIN Morceau  m  ON al.id_album   = m.id_album
WHERE m.nbEcouteTotal_morceau = (
    SELECT MAX(m2.nbEcouteTotal_morceau)
    FROM Album   al2
    JOIN Morceau m2 ON al2.id_album = m2.id_album
    WHERE al2.id_Artiste = ar.id_Artiste
)
ORDER BY ar.nom_Artiste, m.nbEcouteTotal_morceau DESC;

