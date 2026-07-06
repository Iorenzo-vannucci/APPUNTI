const jwt = require('jsonwebtoken');
const JWT_SECRET = 'esame_prog_web_circolo_tennis_secret';

function verificaAutenticazioneAPI(req, res, next) {
    const token = req.cookies.token;

    if (!token) {
        return res.status(401).json({ error: 'Accesso negato.' });
    }

    try {
        req.user = jwt.verify(token, JWT_SECRET);
        next();
    } catch (err) {
        res.clearCookie('token');
        return res.status(401).json({
            error: 'Sessione non valida o scaduta.'
        });
    }
}

function verificaAutenticazionePagine(req, res, next) {
    const token = req.cookies.token;

    if (!token) {
        return res.redirect('/denied.html');
    }

    try {
        req.user = jwt.verify(token, JWT_SECRET);
        next();
    } catch (err) {
        res.clearCookie('token');
        return res.redirect('/denied.html');
    }
}

module.exports = {
    JWT_SECRET,
    verificaAutenticazioneAPI,
    verificaAutenticazionePagine
};