// Variabile globale per sapere chi è l'utente loggato
let utenteAttuale = null; 

// avvio della pagina
async function inizializzaPagina() {
    try {
        const responseMe = await fetch('/api/me');
        if (responseMe.ok) {
            utenteAttuale = await responseMe.json();
            console.log("Accesso confermato come:", utenteAttuale.nome, utenteAttuale.cognome);
        }

        await caricaRanking();

    } catch (error) {
        console.error("Errore durante l'inizializzazione:", error);
    }
}

// carica classifiche
async function caricaRanking() {
    try {
        const response = await fetch('/api/ranking');
        const data = await response.json();

        const boxMaschile = document.getElementById('classificaMaschile');
        const boxFemminile = document.getElementById('classificaFemminile');

        
        if (data.maschile.length === 0) {
            boxMaschile.innerHTML = '<p class="text-empty">Nessun giocatore registrato.</p>';
        } else {
            boxMaschile.innerHTML = data.maschile.map((g, index) => {
                const pos = index + 1;
                const classePodio = (pos === 1) ? 'podium-1' : '';
                
                return `
                    <a href="giocatore.html?id=${g.id_utente}" class="player-card ${classePodio}">
                        <div class="rank-number">${pos}</div>
                        <p class="player-name">${g.nome.charAt(0)}. ${g.cognome}</p>
                        <p class="player-score">${g.punteggio_attuale} pt</p>
                    </a>
                `;
            }).join('');
        }

        if (data.femminile.length === 0) {
            boxFemminile.innerHTML = '<p class="text-empty">Nessuna giocatrice registrata.</p>';
        } else {
            boxFemminile.innerHTML = data.femminile.map((g, index) => {
                const pos = index + 1;
                const classePodio = (pos === 1) ? 'podium-1' : '';
                
                return `
                    <a href="giocatore.html?id=${g.id_utente}" class="player-card ${classePodio}">
                        <div class="rank-number">${pos}</div>
                        <p class="player-name">${g.nome.charAt(0)}. ${g.cognome}</p>
                        <p class="player-score">${g.punteggio_attuale} pt</p>
                    </a>
                `;
            }).join('');
        }

        await caricaTuttiMatch();

    } catch (error) {
        console.error("Errore nel recupero delle classifiche:", error);
    }
}

// carica tutti match circolo
async function caricaTuttiMatch() {
    const isAdmin = utenteAttuale && utenteAttuale.is_admin === 1;
    if (!isAdmin) return; 

    document.getElementById('sezioneTuttiMatch').style.display = 'block';
    const listaTuttiMatch = document.getElementById('listaTuttiMatch');

    try {
        const response = await fetch('/api/partite');
        const partite = await response.json();

        if (partite.length === 0) {
            listaTuttiMatch.innerHTML = `<p class="text-italic">Nessun match registrato nel circolo.</p>`;
            return;
        }

        listaTuttiMatch.innerHTML = partite.map(p => {
            let punteggioStr = `${p.set1_g1}-${p.set1_g2}, ${p.set2_g1}-${p.set2_g2}`;
            if (p.set3_g1 !== null && p.set3_g2 !== null) {
                punteggioStr += `, ${p.set3_g1}-${p.set3_g2}`;
            }

            const dataFormatted = new Date(p.data_match).toLocaleDateString('it-IT', {
                day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            return `
                <div class="match-history-card">
                    <div class="match-card-row">
                        <div>
                            <span class="match-badge-incontro">Incontro</span>
                            <span class="match-title">${p.nome_g1} ${p.cognome_g1} vs ${p.nome_g2} ${p.cognome_g2}</span>
                        </div>
                        <span class="match-date">${dataFormatted}</span>
                    </div>
                    <div class="match-card-body">
                        Punteggio: <strong class="match-score">${punteggioStr}</strong><br>
                        Vincitore: <span class="match-winner">${p.nome_vincitore} ${p.cognome_vincitore}</span>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error("Errore nel recupero dei match:", err);
        listaTuttiMatch.innerHTML = `<p class="msg error">Errore nel recupero dei match.</p>`;
    }
}

window.addEventListener('DOMContentLoaded', inizializzaPagina);