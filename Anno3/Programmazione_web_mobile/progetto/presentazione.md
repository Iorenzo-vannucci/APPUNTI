# Proposta di Progetto: Ristoflow
**Corso:** Programmazione Web e Mobile con Laboratorio  
**Studente:** Lorenzo Vannucci  
**Anno Accademico:** 2025/2026  

---

## 1. Descrizione del Lavoro
**Ristoflow** è un'applicazione web gestionale per la ristorazione concepita con un duplice obiettivo: ottimizzare l'esperienza del cliente al tavolo e semplificare la gestione delle comande lato staff (cucina e camerieri). 

L'applicativo si divide in due macro-aree:
*   **Lato Cliente:** Il cliente al tavolo, tramite il proprio dispositivo mobile, può consultare il menu digitale interattivo, comporre il proprio ordine, inviarlo direttamente in cucina e monitorarne lo stato di preparazione in tempo reale.
*   **Lato Staff:** Un'area riservata e protetta da credenziali permette al personale di cucina e di sala di visualizzare la lista degli ordini attivi, aggiornare lo stato di avanzamento dei piatti e gestire la chiusura dei tavoli.

L'architettura segue il modello Client-Server, sfruttando un frontend in JavaScript Vanilla, un backend sviluppato in Node.js con il framework Express, e la persistenza dei dati affidata a un database relazionale MySQL.

---

## 2. Contenuto delle Pagine
L'applicazione è composta da 5 pagine HTML collegate a un unico foglio di stile CSS comune. Ciascuna pagina include un `header` standard con menu di navigazione responsivo, una sezione `<main>` per il contenuto dinamico e un `footer` con i dettagli del locale.

*   **`index.html` (Home Page / Selezione Tavolo):** 
    *   Benvenuto del ristorante, orari di apertura e contatti.
    *   Form di simulazione o inserimento del numero del tavolo (es. tramite parametro URL o input manuale).
    *   Pulsante d'azione (Call to Action) "Sfoglia il Menu" per avviare l'esperienza.
*   **`menu.html` (Catalogo Piatti e Carrello):**
    *   Barra dei filtri rapida per categorie (Antipasti, Primi, Secondi, Bevande).
    *   Griglia dinamica dei piatti contenente: foto, nome, descrizione, prezzo e bottone "Aggiungi".
    *   Sidebar o sezione a comparsa del "Carrello" con il riepilogo dei piatti selezionati, calcolo del totale in tempo reale e pulsante "Invia Ordine".
*   **`ordine.html` (Stato Comanda Cliente):**
    *   Riepilogo dell'ordine appena inviato con l'identificativo numerico e il numero del tavolo.
    *   Indicatore grafico dello stato corrente dell'ordine (es. *In attesa*, *In preparazione*, *Pronto*, *Servito*).
*   **`login.html` (Accesso Personale):**
    *   Interfaccia pulita con form di autenticazione (Username e Password) dedicato ai dipendenti del ristorante.
*   **`dashboard.html` (Pannello Controllo Cucina/Staff):**
    *   Area accessibile solo previa autenticazione.
    *   Griglia dei tavoli attivi ordinata cronologicamente per orario di arrivo della comanda.
    *   Interfaccia con bottoni rapidi per avanzare lo stato dell'ordine (es. da "In preparazione" a "Pronto") o per archiviare il tavolo a seguito del pagamento.

---

## 3. Funzionalità e Interazioni Utente (JavaScript Client-Side)
*   **Manipolazione del DOM:** Generazione asincrona delle schede dei piatti nella pagina del menu a partire dai dati JSON ricevuti dal server. Aggiornamento dinamico del testo, dei contatori del carrello e del prezzo totale.
*   **Gestione degli Eventi:** 
    *   Ascolto del click sul menu hamburger per l'apertura/chiusura della navigazione su dispositivi mobili.
    *   Gestione degli eventi di aggiunta/rimozione elementi dal carrello.
    *   Intercettazione del `submit` dei form (login e invio ordine) per prevenire il comportamento di default e gestire la trasmissione dati via API.
*   **Persistenza Locale:** Utilizzo del `localStorage` del browser per mantenere memorizzato il carrello del cliente anche in caso di ricaricamento accidentale della pagina `menu.html`.
*   **Interazione con il Server (Fetch API) & Polling:** 
    *   Richieste `GET` asincrone per popolare il menu.
    *   Richieste `POST` per l'invio dell'ordine in formato JSON e per il login dello staff.
    *   Implementazione di una funzione di **polling asincrono** (`setInterval`) nella pagina `ordine.html` e `dashboard.html` che interroga il server ogni 10 secondi per aggiornare l'interfaccia senza ricaricare la pagina.

---

## 4. Modello dei Dati e Database MySQL
Le informazioni dell'applicazione vengono modellate e memorizzate all'interno di un database MySQL strutturato in 4 tabelle principali:

```sql
-- Tabella degli utenti dello staff
CREATE TABLE Utenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    ruolo ENUM('admin', 'cameriere', 'cucina') NOT NULL
);

-- Tabella del menu del giorno
CREATE TABLE Piatti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT,
    prezzo DECIMAL(6,2) NOT NULL,
    categoria ENUM('antipasto', 'primo', 'secondo', 'dolce', 'bevanda') NOT NULL,
    disponibile BOOLEAN DEFAULT TRUE
);

-- Tabella delle comande principali
CREATE TABLE Ordini (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_tavolo INT NOT NULL,
    ora_ordine TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stato ENUM('in attesa', 'in preparazione', 'pronto', 'servito', 'completato') DEFAULT 'in attesa',
    totale_conto DECIMAL(8,2) NOT NULL
);

-- Tabella di giunzione per i dettagli dei piatti ordinati (Relazione Molti-a-Molti)
CREATE TABLE Dettagli_Ordine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ordine_id INT,
    piatto_id INT,
    quantita INT NOT NULL,
    FOREIGN KEY (ordine_id) REFERENCES Ordini(id) ON DELETE CASCADE,
    FOREIGN KEY (piatto_id) REFERENCES Piatti(id)
);