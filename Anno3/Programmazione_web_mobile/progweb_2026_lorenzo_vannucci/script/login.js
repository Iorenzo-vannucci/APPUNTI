document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msgDiv = document.getElementById('loginMsg');
    
    const dati = {
        nome: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dati)
        });
        const result = await response.json();

        if (response.ok) {
            msgDiv.className = "msg success";
            msgDiv.innerText = `Benvenuto, ${result.utente.nome}! Accesso in corso...`;
            setTimeout(() => window.location.href = 'ranking.html', 1500); 
        
        } else {
            msgDiv.className = "msg error";
            msgDiv.innerText = result.error || "Email o Password errati.";
        }
    } catch (err) {
        msgDiv.className = "msg error";
        msgDiv.innerText = "Errore di connessione al server.";
    }
});