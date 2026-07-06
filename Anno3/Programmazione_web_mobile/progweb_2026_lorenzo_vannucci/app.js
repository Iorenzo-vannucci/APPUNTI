const express = require('express');
const mysql = require('mysql2');
const path = require('path');
const cookieParser = require('cookie-parser');

const {
    verificaAutenticazioneAPI,
    verificaAutenticazionePagine
} = require('./middleware/auth');

const app = express();
const PORT = 3000;


// conf db sql

const db = mysql.createConnection({
    host: "localhost",
    user: "admin_tennis",
    password: "Pippo04!",
    database: "circolo_tennis",
    waitForConnections: true
});

db.connect((err) => {
    if (err) return console.error('Errore database:', err);
    console.log('Connesso al database MySQL con successo.');
});

app.use(express.json());
app.use(cookieParser());


app.get(
    ['/ranking.html', '/giocatore.html'],
    verificaAutenticazionePagine,
    (req, res) => {
        res.sendFile(path.join(__dirname, 'private', req.path));
    }
);

app.use(express.static(path.join(__dirname, 'public')));
app.use('/script', express.static(path.join(__dirname, 'script')));


// routes api

app.use('/api', require('./routes/auth')(db));
app.use('/api', require('./routes/player')(db, verificaAutenticazioneAPI));
app.use('/api', require('./routes/match')(db, verificaAutenticazioneAPI));

app.use((req, res) => {

    res.status(404).sendFile(path.join(__dirname, 'public', '404.html'));

});

app.listen(PORT, () => {
    console.log(`Server attivo su http://localhost:${PORT}`);
});