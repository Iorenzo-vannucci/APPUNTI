const express = require('express');
const jwt = require('jsonwebtoken');
const JWT_SECRET = 'esame_prog_web_circolo_tennis_secret';

module.exports = (db) => {
    const router = express.Router();
    const dbPromise = db.promise();
    
    // registrazione utente 
    
    router.post('/register', async (req, res) => {
        const { nome, cognome, email, password, genere } = req.body;

        if (!nome || !cognome || !email || !password || !genere) {
            return res.status(400).json({
                error: 'Campi obbligatori mancanti.'
            });
        }

        try {
            // inserimento del nuovo utente
            
            const [result] = await dbPromise.query(
                `INSERT INTO Utenti 
                (nome, cognome, email, password, genere, is_admin) 
                VALUES (?, ?, ?, ?, ?, 0)`,
                [nome, cognome, email, password, genere]
            );

            // classifica iniziale
            
            await dbPromise.query(
                `INSERT INTO Classifiche 
                (id_giocatore, punteggio_attuale, livello, partite_vinte, partite_perse) 
                VALUES (?, 0, 'Principiante', 0, 0)`,
                [result.insertId]
            );

    
            res.status(201).json({
                message: 'Socio registrato!'
            });

        } catch (err) {
            console.error(err);

            if (err.code === 'ER_DUP_ENTRY') {
                return res.status(400).json({ error: 'Email già in uso.' });
            }

            return res.status(500).json({ error: err.message });
        }
    });

    router.post('/login', (req, res) => {
        const { nome, password } = req.body;

        db.query(
            `SELECT * FROM Utenti WHERE nome = ? AND password = ?`,
            [nome, password],
            (err, results) => {
                if (err) {
                    return res.status(500).json({
                        error: err.message
                    });
                }

                if (results.length === 0) {
                    return res.status(401).json({
                        error: 'Credenziali errate.'
                    });
                }

                const utente = results[0];

                const token = jwt.sign(
                    {
                        userId: utente.id_utente,
                        isAdmin: utente.is_admin
                    },
                    JWT_SECRET,
                    {
                        expiresIn: '1h'
                    }
                );

                res.cookie('token', token, {
                    httpOnly: true,
                    sameSite: 'strict',
                    secure: false,
                    maxAge: 3600000
                });

                res.json({
                    message: 'Accesso eseguito!',
                    utente: {
                        id_utente: utente.id_utente,
                        nome: utente.nome,
                        cognome: utente.cognome,
                        email: utente.email,
                        genere: utente.genere,
                        is_admin: utente.is_admin
                    }
                });
            }
        );
    });

    router.post('/logout', (req, res) => {
        res.clearCookie('token');

        res.json({
            message: 'Logout effettuato.'
        });
    });

    return router;
};