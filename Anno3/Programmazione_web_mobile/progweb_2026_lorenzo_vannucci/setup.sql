-- Tabella Utenti 
CREATE TABLE Utenti (
    id_utente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, 
    genere ENUM('M', 'F') NOT NULL,
    is_admin TINYINT(1) DEFAULT 0 NOT NULL
);

-- Tabella Classifiche
CREATE TABLE Classifiche (
    id_giocatore INT PRIMARY KEY, -- Coincide con id_utente per una relazione 1-a-1
    punteggio_attuale INT DEFAULT 0 NOT NULL,
    posizione_classifica INT NULL, -- Può essere calcolata dinamicamente o salvata qui
    livello VARCHAR(30) DEFAULT 'Principiante' NOT NULL, -- Livello (es. NC, 4.1, 3.5 o testuale)
    partite_vinte INT DEFAULT 0 NOT NULL,
    partite_perse INT DEFAULT 0 NOT NULL,
    FOREIGN KEY (id_giocatore) REFERENCES Utenti(id_utente) ON DELETE CASCADE
);

-- Tabella Partite 
CREATE TABLE Partite (
    id_partita INT AUTO_INCREMENT PRIMARY KEY,
    id_giocatore1 INT NOT NULL,
    id_giocatore2 INT NOT NULL,
    set1_g1 INT NOT NULL,
    set1_g2 INT NOT NULL,
    set2_g1 INT NOT NULL,
    set2_g2 INT NOT NULL,
    set3_g1 INT NULL,
    set3_g2 INT NULL,
    id_vincitore INT NOT NULL,
    data_match TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_giocatore1) REFERENCES Utenti(id_utente) ON DELETE CASCADE,
    FOREIGN KEY (id_giocatore2) REFERENCES Utenti(id_utente) ON DELETE CASCADE,
    FOREIGN KEY (id_vincitore) REFERENCES Utenti(id_utente) ON DELETE CASCADE
);