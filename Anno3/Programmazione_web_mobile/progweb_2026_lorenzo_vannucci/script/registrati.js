document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msgDiv = document.getElementById('registerMsg');

        const dati = {
            nome: document.getElementById('regNome').value,
            cognome: document.getElementById('regCognome').value,
            email: document.getElementById('regEmail').value,
            password: document.getElementById('regPassword').value,
            genere: document.getElementById('regGenere').value
        };

        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dati)
        });
        const result = await response.json();

        if (response.ok) {
            msgDiv.className = "msg success";
            msgDiv.innerText = "Registrazione completata! Verrai reindirizzato all'accesso...";
            form.reset();
            setTimeout(() => window.location.href = 'login.html', 2000);
        } else {
            msgDiv.className = "msg error";
            msgDiv.innerText = result.error || "Errore durante la registrazione.";
        }
       
        }
    );
});
