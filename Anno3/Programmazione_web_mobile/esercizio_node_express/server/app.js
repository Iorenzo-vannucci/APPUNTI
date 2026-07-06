const express = require('express')
const app = express()
const port = 3000

//Middleware per loggare il metodo HTTP, l'URL e la durata della richiesta
app.use((req,res, next) => {
    const start = Date.now() //tempo di inizio
    res.on('finish',() =>{
        const duration = Date.now() - start;
        console.log(req.method + ' '+ req.url +' '+ duration+'ms')
    });
    next();
})
//middleware che cerca in una cartelal specifica. Ad esempio dico
//tutti i file che può cercare l'utente sono all'interno della cartella public
app.use(express.static(__dirname + '/public'));
//se static non trova nulla allora posso prendere le richieste non prese in carico da static 
/*
app.use((req,res) => {
    res.status(404).sendFile(__dirname + '/public/404.html')
});
*/
app.get('/', (req, res) => {
    res.send('benvenuto nella homepage')
})

app.get('/time', (req, res) => {
    res.send('benvenuto nella homepage')
})

app.get('/contact', (req, res) => {
    res.send('benvenuto nella homepage')
})

app.get('/greet', (req, res) => { /* nell'url dopo il link metto ?name= nome da inserire*/
    const name = req.query.name || 'Ospite'
    res.send('Ciao, ' + name +  ' Benvenuto nel nostro sito ')
})

app.get('/greet2/:name', (req, res) => { /* inserisco direttamente nell'url con /nome da inserire*/ 
    const name = req.params.name 
    res.send('Ciao, ' + name +  ' Benvenuto nel nostro sito ')
})



app.use((req, res) => {
    res.status(404).send('Non trovata')
})

app.listen(port, () =>{
    console.log('Server avviato su http://127.0.0.1:' + port)
})
