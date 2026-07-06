const express = require('express');

module.exports = (db, verificaAutenticazioneAPI) => {
    const router = express.Router();

    // utente attualmente loggato
    router.get('/me', verificaAutenticazioneAPI, (req, res) => {
        db.query(
            `SELECT id_utente, nome, cognome, genere, is_admin
            FROM Utenti
            WHERE id_utente = ?`,
            [req.user.userId],
            (err, results) => {
                if (err || results.length === 0) {
                    return res.status(404).json({
                        error: 'Utente non trovato.'
                    });
                }

                res.json(results[0]);
            }
        );
    });

    //classifica
    router.get('/ranking', verificaAutenticazioneAPI, (req, res) => {
        const query = `
            SELECT  U.id_utente, U.nome, U.cognome, U.genere, C.punteggio_attuale
            FROM Utenti U
            JOIN Classifiche C 
            ON U.id_utente = C.id_giocatore
            ORDER BY C.punteggio_attuale DESC
        `;

        db.query(query, (err, results) => {
            if (err) {
                return res.status(500).json({
                    error: err.message
                });
            }

            res.json({
                maschile: results.filter(u => u.genere === 'M'),
                femminile: results.filter(u => u.genere === 'F')
            });
        });
    });

    // profilo singolo giocatore
    router.get('/giocatore/:id', verificaAutenticazioneAPI, (req, res) => {
        const query = `
            SELECT U.nome, U.cognome, U.genere, C.*
            FROM Utenti U
            JOIN Classifiche C 
            ON U.id_utente = C.id_giocatore
            WHERE U.id_utente = ?
        `;

        db.query(query, [req.params.id], (err, results) => {
            if (err || results.length === 0) {
                return res.status(404).json({
                    error: "Giocatore non trovato"
                });
            }

            res.json(results[0]);
        });
    });

    return router;
};