CREATE DATABASE IF NOT EXISTS zechlin;

USE zechlin;

DROP TABLE IF EXISTS quelle_nutzung;
DROP TABLE IF EXISTS nutzung;
DROP TABLE IF EXISTS ausgabe;
DROP TABLE IF EXISTS werk_rism;
DROP TABLE IF EXISTS werk;
DROP TABLE IF EXISTS verlag;
DROP TABLE IF EXISTS werkart;
DROP TABLE IF EXISTS detailgattung;
DROP TABLE IF EXISTS untergattung;
DROP TABLE IF EXISTS gattung;
DROP TABLE IF EXISTS ort;
DROP TABLE IF EXISTS rism;
DROP TABLE IF EXISTS rism_kategorie;

CREATE TABLE gattung
(
    gattung_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    gattung_name VARCHAR(200) NOT NULL
);

CREATE TABLE untergattung
(
    untergattung_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    untergattung_name VARCHAR(200) NOT NULL,
    fk_gattung_id SMALLINT NOT NULL,
    FOREIGN KEY (fk_gattung_id) REFERENCES gattung (gattung_id)
);

CREATE TABLE detailgattung
(
    detailgattung_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    detailgattung_name VARCHAR(200) NOT NULL,
    fk_untergattung_id SMALLINT NOT NULL,
    FOREIGN KEY (fk_untergattung_id) REFERENCES untergattung (untergattung_id)
);

CREATE TABLE werkart
(
    werkart_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    werkart_name VARCHAR(200) NOT NULL
);

CREATE TABLE verlag
(
    verlag_id                 SMALLINT AUTO_INCREMENT PRIMARY KEY,
    verlag_name               VARCHAR(200) NOT NULL,
    verlag_dnb      VARCHAR(500) NULL,
    verlag_webseite VARCHAR(500) NULL
);

CREATE TABLE ort
(
    ort_id        SMALLINT AUTO_INCREMENT PRIMARY KEY,
    ort_name      VARCHAR(200) NOT NULL,
    ort_adresse   VARCHAR(200) NULL,
    ort_latitude  FLOAT(10, 7)  NOT NULL,
    ort_longitude FLOAT(10, 7)  NOT NULL,
    ort_kommentar VARCHAR(200) NULL
);

CREATE TABLE werk
(
    werk_id                     SMALLINT AUTO_INCREMENT PRIMARY KEY,
    werk_titel                  VARCHAR(200)                          NOT NULL,
    werk_untertitel             VARCHAR(500)                          NULL,
    werk_inhalt                 VARCHAR(1500)                          NULL,
    werk_jahr_entstehung_beginn SMALLINT                              NULL,
    werk_jahr_entstehung_ende   SMALLINT                              NULL,
    werk_nummer_zechlin         VARCHAR(50)                           NULL,
    werk_textgrundlage_person   VARCHAR(500)                          NULL,
    werk_textgrundlage_werk     VARCHAR(200)                          NULL,
    werk_kuenstler_name         ENUM ('Ruth Zechlin', 'Ruth Oschatz') NOT NULL,
    werk_spieldauer_in_s        SMALLINT                              NULL,
    werk_ort_autograph          VARCHAR(500)                          NULL,
    werk_ort_autograph_kopie    VARCHAR(500)                          NULL,
    werk_existenzhinweis        VARCHAR(500)                          NULL,
    werk_verlag_hyperlink       VARCHAR(500)                          NULL,
    werk_widmung                VARCHAR(200)                          NULL,
    fk_werk_id_gesamtwerk       SMALLINT                              NULL,
    fk_werk_id_fassung_von      SMALLINT                              NULL,
    fk_werkart_id               SMALLINT                              NOT NULL,
    fk_gattung_id               SMALLINT                              NULL,
    fk_untergattung_id          SMALLINT                              NULL,
    fk_detailgattung_id         SMALLINT                              NULL,
    fk_verlag_id_aktuell        SMALLINT                              NULL,
    FOREIGN KEY (fk_werk_id_gesamtwerk) REFERENCES werk (werk_id),
    FOREIGN KEY (fk_werk_id_fassung_von) REFERENCES werk (werk_id),
    FOREIGN KEY (fk_werkart_id) REFERENCES werkart (werkart_id),
    FOREIGN KEY (fk_gattung_id) REFERENCES gattung (gattung_id),
    FOREIGN KEY (fk_untergattung_id) REFERENCES untergattung (untergattung_id),
    FOREIGN KEY (fk_detailgattung_id) REFERENCES detailgattung (detailgattung_id),
    FOREIGN KEY (fk_verlag_id_aktuell) REFERENCES verlag (verlag_id)
);

CREATE TABLE ausgabe
(
    ausgabe_id   SMALLINT AUTO_INCREMENT PRIMARY KEY,
    ausgabe_typ  VARCHAR(50) NULL,
    ausgabe_jahr SMALLINT    NULL,
    ausgabe_gnd VARCHAR(500) NULL,
    fk_verlag_id SMALLINT    NOT NULL,
    fk_werk_id   SMALLINT    NOT NULL,
    FOREIGN KEY (fk_verlag_id) REFERENCES verlag (verlag_id),
    FOREIGN KEY (fk_werk_id) REFERENCES werk (werk_id)
);

CREATE TABLE nutzung
(
    nutzung_id                        SMALLINT AUTO_INCREMENT PRIMARY KEY,
    nutzung_kontext                   VARCHAR(500) NULL,
    nutzung_art                       VARCHAR(100) NOT NULL,
    nutzung_ist_urauffuehrung         BOOLEAN      NOT NULL,
    nutzung_ist_erstauffuehrung       BOOLEAN      NOT NULL,
    nutzung_erstauffuehrung_kommentar VARCHAR(200) NULL,
    nutzung_kommentar                 VARCHAR(200) NULL,
    nutzung_datum_tag                 TINYINT      NULL,
    nutzung_datum_monat               TINYINT      NULL,
    nutzung_datum_jahr                SMALLINT     NULL,
    nutzung_zeit_stunde               TINYINT      NULL,
    nutzung_zeit_minute               TINYINT      NULL,
    nutzung_datum_kommentar           VARCHAR(200) NULL,
    nutzung_beteiligte                VARCHAR(500) NULL,
    nutzung_spieldauer_in_s           SMALLINT     NULL,
    fk_ort_id                         SMALLINT     NULL,
    fk_werk_id                        SMALLINT     NULL,
    FOREIGN KEY (fk_ort_id) REFERENCES ort (ort_id),
    FOREIGN KEY (fk_werk_id) REFERENCES werk (werk_id)
);

CREATE TABLE quelle_nutzung
(
    quelle_nutzung_id               SMALLINT AUTO_INCREMENT PRIMARY KEY,
    quelle_nutzung_name             VARCHAR(500) NOT NULL,
    quelle_nutzung_datum_aufgerufen DATE         NULL,
    quelle_nutzung_hyperlink        VARCHAR(500) NULL,
    fk_nutzung_id                   SMALLINT     NOT NULL,
    FOREIGN KEY (fk_nutzung_id) REFERENCES nutzung (nutzung_id)
);

CREATE TABLE rism_kategorie
(
    rism_kategorie_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    rism_kategorie_name VARCHAR(100) NOT NULL
);

CREATE TABLE rism
(
    rism_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    rism_code VARCHAR(50) NOT NULL,
    rism_beschreibung VARCHAR(200) NOT NULL,
    fk_rism_kategorie_id SMALLINT NOT NULL,
    FOREIGN KEY (fk_rism_kategorie_id) REFERENCES rism_kategorie (rism_kategorie_id)
);

CREATE TABLE werk_rism
(
    werk_rism_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    fk_werk_id SMALLINT NOT NULL,
    fk_rism_id SMALLINT NOT NULL,
    FOREIGN KEY (fk_werk_id) REFERENCES werk (werk_id),
    FOREIGN KEY (fk_rism_id) REFERENCES rism (rism_id)
);