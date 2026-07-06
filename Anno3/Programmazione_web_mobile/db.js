const connection = mysql.createConnection({
    host: "localhost",
    user: "user1",
    password: "LolloIT2004",
    database: "mio_db"
});
connection.connect((err) => {
if (err) {
console.error("Errore nella connessione al database: " + err.stack);
return;
}
console.log("Connesso al database con ID " + connection.threadId);
});