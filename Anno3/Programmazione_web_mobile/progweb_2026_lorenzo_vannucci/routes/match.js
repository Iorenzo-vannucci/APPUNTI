const express = require('express');

module.exports = (db, verificaAutenticazioneAPI) => {
    const router = express.Router();

    const dbPromise = db.promise();
    
    const calcolaVincitore = (id1, id2, s1_1, s1_2, s2_1, s2_2, s3_1, s3_2) => {
        let set1 = 0;
        let set2 = 0;

        if (parseInt(s1_1) > parseInt(s1_2)) {
            set1++;
        } else if (parseInt(s1_2) > parseInt(s1_1)) {
            set2++;
        }

        if (parseInt(s2_1) > parseInt(s2_2)) {
            set1++;
        } else if (parseInt(s2_2) > parseInt(s2_1)) {
            set2++;
        }

        if (s3_1 && s3_2) {
            if (parseInt(s3_1) > parseInt(s3_2)) {
                set1++;
            } else if (parseInt(s3_2) > parseInt(s3_1)) {
                set2++;
            }
        }

        return set1 > set2 ? id1 : id2;
    };

    // query storico partite
    const queryPartite = `
        SELECT 
            p.*,
            u1.nome AS nome_g1,
            u1.cognome AS cognome_g1,
            u2.nome AS nome_g2,
            u2.cognome AS cognome_g2,
            uv.nome AS nome_vincitore,
            uv.cognome AS cognome_vincitore
        FROM Partite p
        JOIN Utenti u1 
            ON p.id_giocatore1 = u1.id_utente
        JOIN Utenti u2 
            ON p.id_giocatore2 = u2.id_utente
        JOIN Utenti uv 
            ON p.id_vincitore = uv.id_utente
    `;

    //storico partite
    router.get('/partite', verificaAutenticazioneAPI, (req, res) => {
        db.query(
            `${queryPartite} ORDER BY p.data_match DESC`,
            (err, results) => {
                res.json(err ? { error: err.message } : results);
            }
        );
    });

    //partite di un giocatore specifico
    router.get('/giocatore/:id/partite', verificaAutenticazioneAPI, (req, res) => {
        db.query(
            `${queryPartite}
            WHERE p.id_giocatore1 = ? OR p.id_giocatore2 = ?
            ORDER BY p.data_match DESC`,
            [req.params.id, req.params.id],
            (err, results) => {
                res.json(err ? { error: err.message } : results);
            }
        );
    });

    // inserimento match
    router.post('/match', verificaAutenticazioneAPI, async (req, res) => {
        const { id_avversario, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2 } = req.body;
        const id_utente = req.user.userId;

        if ( !id_avversario || set1_g1 === undefined || set1_g2 === undefined) {
            return res.status(400).json({
                error: "Dati incompleti."
            });
        }

        const id_vincitore = calcolaVincitore(id_utente, id_avversario, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2);
        const id_perdente = id_vincitore === id_utente ? id_avversario : id_utente;

        try {
            // partita
            await dbPromise.query(
                `INSERT INTO Partite 
                (id_giocatore1, id_giocatore2, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2, id_vincitore) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [id_utente, id_avversario, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1 || null, set3_g2 || null, id_vincitore]
            );

            // vincitore
            await dbPromise.query(
                `UPDATE Classifiche 
                SET punteggio_attuale = punteggio_attuale + 10, partite_vinte = partite_vinte + 1 
                WHERE id_giocatore = ?`,
                [id_vincitore]
            );

            // perdente
            await dbPromise.query(
                `UPDATE Classifiche 
                SET partite_perse = partite_perse + 1 
                WHERE id_giocatore = ?`,
                [id_perdente]
            );

            res.json({ message: "Match registrato con successo!" });

        } catch (err) {
            console.error(err);
            return res.status(500).json({ error: "Errore durante il salvataggio del match: " + err.message });
        }
    });


    // modifica match
    router.put('/match/:id', verificaAutenticazioneAPI, async (req, res) => {
        const { set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2 } = req.body;

        try {
            // recuopero datti vecchi match
            const [results] = await dbPromise.query(
                `SELECT id_giocatore1, id_giocatore2, id_vincitore FROM Partite WHERE id_partita = ?`,
                [req.params.id]
            );

            if (results.length === 0) {
                return res.status(404).json({ error: "Match non trovato." });
            }

            const {
                id_giocatore1: id_g1,
                id_giocatore2: id_g2,
                id_vincitore: old_vincitore
            } = results[0];

            // ricalcolo vincitore
            const new_vincitore = calcolaVincitore(
                id_g1, id_g2, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2
            );

            // recupero perdente vecchio e nuovo
            const old_perdente = old_vincitore === id_g1 ? id_g2 : id_g1;
            const new_perdente = new_vincitore === id_g1 ? id_g2 : id_g1;

            // aggiorno dati su tabella Partite
            await dbPromise.query(
                `UPDATE Partite
                SET set1_g1 = ?, set1_g2 = ?, set2_g1 = ?, set2_g2 = ?, set3_g1 = ?, set3_g2 = ?, id_vincitore = ? 
                WHERE id_partita = ?`,
                [set1_g1, set1_g2, set2_g1, set2_g2, set3_g1 || null, set3_g2 || null, new_vincitore, req.params.id]
            );

            //se cambia vincitore aggiorno dati partita e classifica
            if (old_vincitore !== new_vincitore) {
                
                
                await dbPromise.query(
                    `UPDATE Classifiche
                    SET punteggio_attuale = GREATEST(0, punteggio_attuale - 10),
                        partite_vinte = GREATEST(0, partite_vinte - 1),
                        partite_perse = partite_perse + 1
                    WHERE id_giocatore = ?`,
                    [old_vincitore]
                );

                
                await dbPromise.query(
                    `UPDATE Classifiche
                    SET punteggio_attuale = punteggio_attuale + 10,
                        partite_vinte = partite_vinte + 1,
                        partite_perse = GREATEST(0, partite_perse - 1)
                    WHERE id_giocatore = ?`,
                    [new_vincitore]
                );

                return res.json({ message: "Aggiornato con cambio vincitore ricalcolato!" });
            }

            
            res.json({ message: "Punteggio modificato (vincitore invariato)." });

        } catch (err) {
            console.error(err);
            return res.status(500).json({ error: "Errore durante la modifica del match: " + err.message });
        }
    });

    return router;
};