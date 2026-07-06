const express = require("express");
const cookieParser = require("cookie-parser");

const app = express();
const port = 3000;

app.use(cookieParser()); //imposto il middleware cookieParser
app.use(express.static("public")); // Serve tutti i file statici da public/

// Login - imposta il cookie
app.get("/login", (req, res) => {
    res.cookie("auth", "true", { maxAge: 600000, httpOnly: true, secure: true }); 
    // auth: nome del cookie, httpOnly: può funzionare solo tramite protocollo http; 
    // secure: funziona solo in https
    res.redirect("/restricted.html"); // reindirizza all'area riservata
});

// Logout - cancella il cookie
app.get("/logout", (req, res) => {
    res.clearCookie("auth"); //chiamo la funzione di middleware per cancellare il cookie di nome auth 
    res.redirect("/");
});

// Accesso all'area riservata
app.get("/restricted.html", (req, res) => {
    if (req.cookies.auth === "true") { // faccio un check, se cookie.auth è con valore True allora gli mando il file
        //altrimenti rimando sulla pagina denied
        res.sendFile(__dirname + "/private/restricted.html");
    }
    else {
        res.redirect("/denied.html");
    }
});

app.listen(port, () => {
    console.log("Server in ascolto su http://localhost:" + port);
});

