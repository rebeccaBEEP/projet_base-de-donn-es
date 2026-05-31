-- Projet- Plateforme de Streaming Musical
-- Script DDL + DML 
-- SGBD : MySQL


CREATE DATABASE IF NOT EXISTS streaming_musical
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE streaming_musical;

-- SUPPRESSION DES TABLES 

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS suivre;
DROP TABLE IF EXISTS contient;
DROP TABLE IF EXISTS Ecoute;
DROP TABLE IF EXISTS Playlist;
DROP TABLE IF EXISTS Souscription;
DROP TABLE IF EXISTS Morceau;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Artiste;
DROP TABLE IF EXISTS categorise;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Utilisateur;
DROP TABLE IF EXISTS Abonnement;

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================
-- DDL - CRÉATION DES TABLES
-- =============================================================

CREATE TABLE Genre (
    id_genre          INT          NOT NULL AUTO_INCREMENT,
    nom_genre         VARCHAR(100) NOT NULL UNIQUE,
    description_genre VARCHAR(500) NULL,
    PRIMARY KEY (id_genre)
);

CREATE TABLE Artiste (
    id_Artiste            INT          NOT NULL AUTO_INCREMENT,
    nom_Artiste           VARCHAR(150) NOT NULL,
    biographie_artiste    TEXT         NULL,
    paysOrigine_Artiste   VARCHAR(100) NULL,
    Date_debut_Artiste    DATE         NULL,
    nb_auditeurs_mensuels INT          NOT NULL DEFAULT 0 CHECK (nb_auditeurs_mensuels >= 0),
    est_verifie           TINYINT(1)   NOT NULL DEFAULT 0,
    PRIMARY KEY (id_Artiste)
);

CREATE TABLE Album (
    id_album               INT          NOT NULL AUTO_INCREMENT,
    titre                  VARCHAR(200) NOT NULL,
    DateSortie_album       DATE         NOT NULL,
    type_album             ENUM('Album','EP','Single','Compilation') NOT NULL DEFAULT 'Album',
    imagesCouverture_album VARCHAR(500) NULL,
    id_Artiste             INT          NOT NULL,
    PRIMARY KEY (id_album),
    CONSTRAINT fk_album_artiste FOREIGN KEY (id_Artiste)
        REFERENCES Artiste(id_Artiste)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Morceau (
    id_morceau              INT          NOT NULL AUTO_INCREMENT,
    titre_morceau           VARCHAR(200) NOT NULL,
    dureeSeconde_morceau    INT          NOT NULL CHECK (dureeSeconde_morceau > 0),
    numero_piste            INT          NULL CHECK (numero_piste > 0),
    explicit_morceau        TINYINT(1)   NOT NULL DEFAULT 0,
    nbEcouteTotal_morceau   BIGINT       NOT NULL DEFAULT 0 CHECK (nbEcouteTotal_morceau >= 0),
    url_fichiers_morceau    VARCHAR(500) NOT NULL,
    id_album                INT          NULL,
    PRIMARY KEY (id_morceau),
    CONSTRAINT fk_morceau_album FOREIGN KEY (id_album)
        REFERENCES Album(id_album)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Association porteuse d'attributs : categorise (Morceau <-> Genre)
CREATE TABLE categorise (
    id_morceau INT NOT NULL,
    id_genre   INT NOT NULL,
    PRIMARY KEY (id_morceau, id_genre),
    CONSTRAINT fk_categorise_morceau FOREIGN KEY (id_morceau)
        REFERENCES Morceau(id_morceau)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_categorise_genre FOREIGN KEY (id_genre)
        REFERENCES Genre(id_genre)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Abonnement (
    id_abonmt            INT            NOT NULL AUTO_INCREMENT,
    nomPlan_abonmt       VARCHAR(100)   NOT NULL UNIQUE,
    prix_mensuel_abonmt  DECIMAL(6,2)   NOT NULL CHECK (prix_mensuel_abonmt >= 0),
    ecoute_horsLigne_abonmt TINYINT(1)  NOT NULL DEFAULT 0,
    qualite_audio        ENUM('Normal','Haute','Très Haute') NOT NULL DEFAULT 'Normal',
    nb_appareils         INT            NOT NULL DEFAULT 1 CHECK (nb_appareils > 0),
    PRIMARY KEY (id_abonmt)
);

CREATE TABLE Utilisateur (
    id_utilisateur             INT          NOT NULL AUTO_INCREMENT,
    nom_utilisateur            VARCHAR(100) NOT NULL,
    prenom_utilisateur         VARCHAR(100) NOT NULL,
    email_utilisateur          VARCHAR(200) NOT NULL UNIQUE,
    mdp_utilisateur            VARCHAR(255) NOT NULL,
    dateNaissance_utilisateur  DATE         NOT NULL,
    dateInscription_utilisateur DATE        NOT NULL DEFAULT (CURRENT_DATE),
    pays                       VARCHAR(100) NULL,
    PRIMARY KEY (id_utilisateur)
);

CREATE TABLE Souscription (
    id_souscription INT        NOT NULL AUTO_INCREMENT,
    date_debut      DATE       NOT NULL,
    date_fin        DATE       NULL,
    est_actif       TINYINT(1) NOT NULL DEFAULT 1,
    id_abonmt       INT        NOT NULL,
    id_utilisateur  INT        NOT NULL UNIQUE,
    PRIMARY KEY (id_souscription),
    CONSTRAINT fk_souscription_abonnement FOREIGN KEY (id_abonmt)
        REFERENCES Abonnement(id_abonmt)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_souscription_utilisateur FOREIGN KEY (id_utilisateur)
        REFERENCES Utilisateur(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_dates CHECK (date_fin IS NULL OR date_fin >= date_debut)
);

CREATE TABLE Playlist (
    id_playlist             INT          NOT NULL AUTO_INCREMENT,
    nom_playlist            VARCHAR(200) NOT NULL,
    description_playlist    VARCHAR(500) NULL,
    est_publique            TINYINT(1)   NOT NULL DEFAULT 1,
    date_creation_playlist  DATE         NOT NULL DEFAULT (CURRENT_DATE),
    id_utilisateur          INT          NOT NULL,
    PRIMARY KEY (id_playlist),
    CONSTRAINT fk_playlist_utilisateur FOREIGN KEY (id_utilisateur)
        REFERENCES Utilisateur(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Association porteuse d'attributs : contient (Morceau <-> Playlist)
CREATE TABLE contient (
    id_morceau  INT  NOT NULL,
    id_playlist INT  NOT NULL,
    position_   INT  NOT NULL CHECK (position_ > 0),
    date_ajout  DATE NOT NULL DEFAULT (CURRENT_DATE),
    PRIMARY KEY (id_morceau, id_playlist),
    CONSTRAINT fk_contient_morceau FOREIGN KEY (id_morceau)
        REFERENCES Morceau(id_morceau)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_contient_playlist FOREIGN KEY (id_playlist)
        REFERENCES Playlist(id_playlist)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Ecoute (
    id_ecoute        INT          NOT NULL AUTO_INCREMENT,
    date_ecoute      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duree_ecoute_sec INT          NOT NULL CHECK (duree_ecoute_sec >= 0),
    appareil         VARCHAR(100) NULL,
    id_morceau       INT          NOT NULL,
    id_utilisateur   INT          NOT NULL,
    PRIMARY KEY (id_ecoute),
    CONSTRAINT fk_ecoute_morceau FOREIGN KEY (id_morceau)
        REFERENCES Morceau(id_morceau)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ecoute_utilisateur FOREIGN KEY (id_utilisateur)
        REFERENCES Utilisateur(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Association porteuse d'attributs : suivre (Utilisateur <-> Artiste)
CREATE TABLE suivre (
    id_utilisateur INT  NOT NULL,
    id_Artiste     INT  NOT NULL,
    date_suivi     DATE NOT NULL DEFAULT (CURRENT_DATE),
    PRIMARY KEY (id_utilisateur, id_Artiste),
    CONSTRAINT fk_suivre_utilisateur FOREIGN KEY (id_utilisateur)
        REFERENCES Utilisateur(id_utilisateur)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_suivre_artiste FOREIGN KEY (id_Artiste)
        REFERENCES Artiste(id_Artiste)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- =============================================================
-- DML - JEU DE DONNÉES
-- =============================================================

INSERT INTO Genre (nom_genre, description_genre) VALUES
('Pop',         'Musique populaire grand public'),
('Rock',        'Musique électrique avec guitares'),
('Hip-Hop',     'Musique urbaine avec rap et beatmaking'),
('R&B',         'Rhythm and Blues, soul moderne'),
('Électronique','Musique produite électroniquement'),
('Jazz',        'Genre improvisé aux racines afro-américaines'),
('Classique',   'Musique savante occidentale'),
('Reggae',      'Musique jamaïcaine au tempo syncopé');

INSERT INTO Artiste (nom_Artiste, biographie_artiste, paysOrigine_Artiste, Date_debut_Artiste, nb_auditeurs_mensuels, est_verifie) VALUES
('Taylor Swift',   'Auteure-compositrice américaine, icône de la pop.',        'USA',          '2006-10-24', 82000000, 1),
('Drake',          'Rappeur, chanteur et producteur canadien.',                 'Canada',       '2006-10-27', 75000000, 1),
('Daft Punk',      'Duo de musique électronique français.',                     'France',       '1993-01-01', 15000000, 1),
('Adele',          'Chanteuse et auteure-compositrice britannique.',            'Royaume-Uni',  '2006-01-01', 50000000, 1),
('Kendrick Lamar', 'Rappeur et compositeur américain de Compton.',              'USA',          '2003-01-01', 45000000, 1),
('Stromae',        'Artiste belge mêlant électro, pop et world music.',         'Belgique',     '2009-01-01', 12000000, 1),
('Billie Eilish',  'Chanteuse américaine connue pour son style sombre et pop.', 'USA',          '2015-11-18', 60000000, 1),
('Miles Davis',    'Trompettiste de jazz américain, légende du genre.',         'USA',          '1944-01-01',  3000000, 1);

INSERT INTO Album (titre, DateSortie_album, type_album, imagesCouverture_album, id_Artiste) VALUES
('1989',                         '2014-10-27', 'Album',  'covers/1989.jpg',       1),
('Midnights',                    '2022-10-21', 'Album',  'covers/midnights.jpg',  1),
('Certified Lover Boy',          '2021-09-03', 'Album',  'covers/clb.jpg',        2),
('Scorpion',                     '2018-06-29', 'Album',  'covers/scorpion.jpg',   2),
('Random Access Memories',       '2013-05-17', 'Album',  'covers/ram.jpg',        3),
('25',                           '2015-11-20', 'Album',  'covers/25.jpg',         4),
('30',                           '2021-11-19', 'Album',  'covers/30.jpg',         4),
('Mr. Morale & The Big Steppers','2022-05-13', 'Album',  'covers/mrmoral.jpg',    5),
('Multitude',                    '2013-03-11', 'Album',  'covers/multitude.jpg',  6),
('Racine Carrée',                '2013-08-23', 'Album',  'covers/racine.jpg',     6),
('When We All Fall Asleep',      '2019-03-29', 'Album',  'covers/wwafa.jpg',      7),
('Happier Than Ever',            '2021-07-30', 'Album',  'covers/hte.jpg',        7),
('Kind of Blue',                 '1959-08-17', 'Album',  'covers/kindofblue.jpg', 8),
('Lover',                        '2019-08-23', 'Album',  'covers/lover.jpg',      1),
('One Dance',                    '2016-04-05', 'Single', 'covers/onedance.jpg',   2);

INSERT INTO Morceau (titre_morceau, dureeSeconde_morceau, numero_piste, explicit_morceau, nbEcouteTotal_morceau, url_fichiers_morceau, id_album) VALUES
('Shake It Off',              219, 1, 0, 3500000000, 'audio/shake_it_off.mp3',  1),
('Blank Space',               231, 2, 0, 3100000000, 'audio/blank_space.mp3',   1),
('Anti-Hero',                 200, 1, 0, 4200000000, 'audio/anti_hero.mp3',     2),
('Lavender Haze',             202, 2, 0, 2100000000, 'audio/lavender_haze.mp3', 2),
('Gods Plan',                 198, 1, 1, 5000000000, 'audio/gods_plan.mp3',     4),
('In My Feelings',            217, 2, 1, 2900000000, 'audio/in_my_feelings.mp3',4),
('One Dance',                 173, 1, 0, 4800000000, 'audio/one_dance.mp3',    15),
('Get It Together',           255, 3, 1, 1200000000, 'audio/get_it_together.mp3',3),
('Get Lucky',                 369, 1, 0, 2500000000, 'audio/get_lucky.mp3',     5),
('Instant Crush',             337, 2, 0, 1100000000, 'audio/instant_crush.mp3', 5),
('Hello',                     295, 1, 0, 3800000000, 'audio/hello.mp3',         6),
('Someone Like You',          285, 2, 0, 3600000000, 'audio/someone_like_you.mp3',6),
('Easy On Me',                224, 1, 0, 3000000000, 'audio/easy_on_me.mp3',    7),
('Oh God',                    210, 2, 0,  950000000, 'audio/oh_god.mp3',        7),
('N95',                       198, 1, 1,  820000000, 'audio/n95.mp3',           8),
('Die Hard',                  271, 2, 0,  750000000, 'audio/die_hard.mp3',      8),
('Papaoutai',                 244, 1, 0, 1800000000, 'audio/papaoutai.mp3',    10),
('Formidable',                233, 2, 0, 2200000000, 'audio/formidable.mp3',    9),
('bad guy',                   194, 1, 0, 4100000000, 'audio/bad_guy.mp3',      11),
('when the party is over',    245, 2, 0, 2000000000, 'audio/party_over.mp3',   11),
('Happier Than Ever',         295, 1, 0, 1900000000, 'audio/happier.mp3',      12),
('Oxytocin',                  200, 2, 1,  850000000, 'audio/oxytocin.mp3',     12),
('So What',                   565, 1, 0,  500000000, 'audio/so_what.mp3',      13),
('Freddie Freeloader',        596, 2, 0,  420000000, 'audio/freddie.mp3',      13),
('Lover',                     221, 1, 0, 2300000000, 'audio/lover.mp3',        14);

INSERT INTO categorise (id_morceau, id_genre) VALUES
(1,1),(2,1),(3,1),(4,1),(25,1),
(9,5),(10,5),
(5,3),(6,3),(7,3),(8,3),(15,3),(16,3),
(11,1),(12,1),(13,1),(14,1),
(17,5),(18,5),(17,1),(18,1),
(19,1),(20,1),(21,1),(22,1),
(19,4),(21,4),
(23,6),(24,6),
(7,4),(11,4);

INSERT INTO Abonnement (nomPlan_abonmt, prix_mensuel_abonmt, ecoute_horsLigne_abonmt, qualite_audio, nb_appareils) VALUES
('Gratuit',  0.00, 0, 'Normal',      1),
('Premium',  9.99, 1, 'Haute',       1),
('Famille', 14.99, 1, 'Très Haute',  6),
('Étudiant', 4.99, 1, 'Haute',       1);

INSERT INTO Utilisateur (nom_utilisateur, prenom_utilisateur, email_utilisateur, mdp_utilisateur, dateNaissance_utilisateur, dateInscription_utilisateur, pays) VALUES
('Dupont',  'Alice',    'alice.dupont@email.com',    'hashed_pwd_1',  '1998-03-15', '2022-01-10', 'France'),
('Martin',  'Baptiste', 'baptiste.martin@email.com', 'hashed_pwd_2',  '2001-07-22', '2022-05-20', 'France'),
('Leroy',   'Camille',  'camille.leroy@email.com',   'hashed_pwd_3',  '1995-11-30', '2021-09-05', 'Belgique'),
('Moreau',  'Dylan',    'dylan.moreau@email.com',    'hashed_pwd_4',  '2003-01-08', '2023-02-14', 'France'),
('Garcia',  'Emma',     'emma.garcia@email.com',     'hashed_pwd_5',  '1990-06-19', '2020-11-01', 'Espagne'),
('Petit',   'Florian',  'florian.petit@email.com',   'hashed_pwd_6',  '1997-09-25', '2023-06-30', 'France'),
('Bernard', 'Grace',    'grace.bernard@email.com',   'hashed_pwd_7',  '2000-04-12', '2022-08-17', 'Canada'),
('Nguyen',  'Hugo',     'hugo.nguyen@email.com',     'hashed_pwd_8',  '1988-12-03', '2021-03-22', 'France'),
('Dubois',  'Inès',     'ines.dubois@email.com',     'hashed_pwd_9',  '2002-08-27', '2023-01-05', 'France'),
('Lambert', 'Jules',    'jules.lambert@email.com',   'hashed_pwd_10', '1994-05-14', '2020-07-19', 'Suisse');

INSERT INTO Souscription (date_debut, date_fin, est_actif, id_abonmt, id_utilisateur) VALUES
('2022-01-10', NULL,         1, 2, 1),
('2022-05-20', NULL,         1, 4, 2),
('2021-09-05', NULL,         1, 3, 3),
('2023-02-14', NULL,         1, 4, 4),
('2020-11-01', NULL,         1, 2, 5),
('2023-06-30', NULL,         1, 1, 6),
('2022-08-17', NULL,         1, 3, 7),
('2021-03-22', '2024-03-22', 0, 2, 8),
('2023-01-05', NULL,         1, 4, 9),
('2020-07-19', NULL,         1, 2, 10);

INSERT INTO Playlist (nom_playlist, description_playlist, est_publique, date_creation_playlist, id_utilisateur) VALUES
('Mes hits du moment',   'Tous les titres que j écoute en boucle', 1, '2023-01-15', 1),
('Road trip',            'Parfait pour les longs trajets',          1, '2022-11-20', 2),
('Concentration',        'Musique pour travailler',                 0, '2023-03-10', 3),
('Soirée Pop',           'Les meilleurs hits pop',                  1, '2023-07-04', 4),
('Hip-Hop Essentials',   'Les classiques du rap',                   1, '2022-09-18', 5),
('Chill Vibes',          'Relaxation et détente',                   1, '2023-05-22', 6),
('Années 2010',          'Nostalgie des années 2010',               0, '2023-02-28', 7),
('Jazz & Soul',          'Pour les amateurs de jazz',               1, '2021-12-01', 8),
('Workout',              'Motivation sport',                        1, '2023-04-11', 9),
('Best of Français',     'Artistes francophones',                   1, '2022-06-05', 10);

INSERT INTO contient (id_morceau, id_playlist, position_, date_ajout) VALUES
(3,1,1,'2023-01-15'),(1,1,2,'2023-01-15'),(19,1,3,'2023-02-01'),(11,1,4,'2023-02-10'),
(7,2,1,'2022-11-20'),(9,2,2,'2022-11-20'),(1,2,3,'2022-12-01'),(17,2,4,'2022-12-15'),(5,2,5,'2023-01-05'),
(9,3,1,'2023-03-10'),(10,3,2,'2023-03-10'),(23,3,3,'2023-03-15'),
(1,4,1,'2023-07-04'),(2,4,2,'2023-07-04'),(3,4,3,'2023-07-05'),(11,4,4,'2023-07-05'),(25,4,5,'2023-07-06'),
(5,5,1,'2022-09-18'),(6,5,2,'2022-09-18'),(7,5,3,'2022-09-20'),(15,5,4,'2022-10-01'),(16,5,5,'2022-10-01'),
(20,6,1,'2023-05-22'),(12,6,2,'2023-05-22'),(4,6,3,'2023-05-23'),(13,6,4,'2023-06-01'),
(1,7,1,'2023-02-28'),(2,7,2,'2023-02-28'),(9,7,3,'2023-03-05'),(11,7,4,'2023-03-05'),
(23,8,1,'2021-12-01'),(24,8,2,'2021-12-01'),
(3,9,1,'2023-04-11'),(5,9,2,'2023-04-11'),(7,9,3,'2023-04-12'),(19,9,4,'2023-04-12'),
(17,10,1,'2022-06-05'),(18,10,2,'2022-06-05'),(4,10,3,'2022-06-10');

INSERT INTO Ecoute (date_ecoute, duree_ecoute_sec, appareil, id_morceau, id_utilisateur) VALUES
('2024-01-05 08:15:00', 219, 'Mobile',   1,  1),
('2024-01-05 09:00:00', 231, 'Mobile',   2,  1),
('2024-01-06 14:30:00', 200, 'Desktop',  3,  1),
('2024-01-07 17:00:00', 198, 'Mobile',   5,  2),
('2024-01-07 17:04:00', 217, 'Mobile',   6,  2),
('2024-01-08 10:00:00', 173, 'Tablette', 7,  2),
('2024-01-09 20:00:00', 369, 'Desktop',  9,  3),
('2024-01-09 20:07:00', 337, 'Desktop', 10,  3),
('2024-01-10 12:00:00', 295, 'Mobile',  11,  3),
('2024-01-10 13:00:00', 198, 'Mobile',  15,  4),
('2024-01-10 13:05:00', 271, 'Mobile',  16,  4),
('2024-01-11 08:00:00', 200, 'Mobile',   3,  4),
('2024-01-12 09:00:00', 295, 'Desktop', 11,  5),
('2024-01-12 09:05:00', 285, 'Desktop', 12,  5),
('2024-01-13 21:00:00', 224, 'TV',      13,  5),
('2024-01-14 07:30:00', 244, 'Mobile',  17,  6),
('2024-01-14 07:35:00', 233, 'Mobile',  18,  6),
('2024-01-15 15:00:00', 194, 'Mobile',  19,  7),
('2024-01-15 15:05:00', 245, 'Mobile',  20,  7),
('2024-01-16 11:00:00', 565, 'Desktop', 23,  8),
('2024-01-16 11:10:00', 596, 'Desktop', 24,  8),
('2024-01-17 18:00:00', 200, 'Mobile',   3,  9),
('2024-01-17 18:05:00', 219, 'Mobile',   1,  9),
('2024-01-18 14:00:00', 369, 'Desktop',  9, 10),
('2024-01-18 14:08:00', 221, 'Desktop', 25, 10),
('2024-02-01 09:00:00', 200, 'Mobile',   3,  1),
('2024-02-02 10:00:00', 219, 'Mobile',   1,  2),
('2024-02-03 11:00:00', 198, 'Mobile',   5,  3),
('2024-02-05 15:00:00', 173, 'Mobile',   7,  5),
('2024-02-06 16:00:00', 200, 'Mobile',  19,  7);

INSERT INTO suivre (id_utilisateur, id_Artiste, date_suivi) VALUES
(1,1,'2022-01-15'),(1,7,'2022-02-10'),(1,4,'2022-03-05'),
(2,2,'2022-05-21'),(2,5,'2022-06-10'),(2,1,'2023-01-01'),
(3,3,'2021-09-10'),(3,6,'2021-10-01'),
(4,5,'2023-02-15'),(4,2,'2023-03-01'),
(5,4,'2020-11-05'),(5,1,'2021-01-20'),(5,7,'2022-05-15'),
(6,6,'2023-07-01'),
(7,7,'2022-08-20'),(7,1,'2022-09-01'),
(8,8,'2021-04-01'),(8,3,'2021-05-15'),
(9,7,'2023-01-10'),(9,1,'2023-02-01'),
(10,1,'2020-07-20'),(10,3,'2020-08-01'),(10,6,'2021-01-10');

