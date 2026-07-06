google.charts.load('current', { packages: ['corechart'] });

let utenteAttuale = null;
let idProfilo = null;
const partiteCache = {}; //cache

const $ = id => document.getElementById(id);
const isAdmin = () => utenteAttuale && utenteAttuale.is_admin === 1;

// leggo punteggi form
function leggiPunteggi(idPartita = null) {
    const s1g1 = idPartita ? $(`edit_s1_1_${idPartita}`).value : $('g1_mio').value;
    const s1g2 = idPartita ? $(`edit_s1_2_${idPartita}`).value : $('g1_lui').value;
    const s2g1 = idPartita ? $(`edit_s2_1_${idPartita}`).value : $('g2_mio').value;
    const s2g2 = idPartita ? $(`edit_s2_2_${idPartita}`).value : $('g2_lui').value;
    const s3g1 = idPartita ? $(`edit_s3_1_${idPartita}`).value : $('g3_mio').value;
    const s3g2 = idPartita ? $(`edit_s3_2_${idPartita}`).value : $('g3_lui').value;

    if (s1g1 === '' || s1g2 === '' || s2g1 === '' || s2g2 === '') {
        return null;
    }

    return {
        set1_g1: parseInt(s1g1),
        set1_g2: parseInt(s1g2),
        set2_g1: parseInt(s2g1),
        set2_g2: parseInt(s2g2),
        set3_g1: s3g1 === '' ? null : parseInt(s3g1),
        set3_g2: s3g2 === '' ? null : parseInt(s3g2)
    };
}

function matchValido(p) {
    let setVintiG1 = 0;
    let setVintiG2 = 0;

    if (p.set1_g1 > p.set1_g2) setVintiG1++; else setVintiG2++;
    if (p.set2_g1 > p.set2_g2) setVintiG1++; else setVintiG2++;
    if (p.set3_g1 !== null && p.set3_g2 !== null) {
        if (p.set3_g1 > p.set3_g2) setVintiG1++; else setVintiG2++;
    }

    return setVintiG1 !== setVintiG2;
}

async function caricaProfilo() {
    const urlCompleto = window.location.href;
    const partiUrl = urlCompleto.split('?'); 
    const parametri = partiUrl[1].split('=');
    idProfilo = parseInt(parametri[1]);
    if (!idProfilo) return;

    try {
        const resMe = await fetch('/api/me');
        if (resMe.ok) utenteAttuale = await resMe.json();

        const giocatore = await fetch(`/api/giocatore/${idProfilo}`).then(r => r.json());

        $('playerTitle').innerText = `${giocatore.nome} ${giocatore.cognome}`;
        $('playerLevel').innerText = `Livello: ${giocatore.livello}`;
        $('statPunti').innerText = giocatore.punteggio_attuale;
        $('statVinte').innerText = giocatore.partite_vinte;
        $('statPerse').innerText = giocatore.partite_perse;

        if ($('avatarContainer')) {
            const iconName = giocatore.genere === 'F' ? 'person_2' : 'person';
            $('avatarContainer').innerHTML = `<span class="material-symbols-outlined" style="font-size: 80px;">${iconName}</span>`;
        }

        google.charts.setOnLoadCallback(() => drawChart(giocatore.partite_vinte, giocatore.partite_perse));

        if (isAdmin() || utenteAttuale.id_utente === idProfilo) {
            await preparaFormInserimento();
        }

        await caricaStoricoPartite();

    } catch (err) {
        console.error("Errore nel caricamento del profilo:", err);
    }
}

async function caricaStoricoPartite() {
    const lista = $('listaPartite');
    if (!lista) return;

    try {
        const response = await fetch(`/api/giocatore/${idProfilo}/partite`);
        const partite = await response.json();

        if (partite.length === 0) {
            lista.innerHTML = '<p class="text-italic">Nessuna partita registrata per questo giocatore.</p>';
            return;
        }

        lista.innerHTML = partite.map(p => {
            // salvo il match nella cache così da poter rileggere i dati al click del tasto modifica
            partiteCache[p.id_partita] = p;

            const vittoria = p.id_vincitore === idProfilo;
            let punteggioStr = `${p.set1_g1}-${p.set1_g2}, ${p.set2_g1}-${p.set2_g2}`;
            if (p.set3_g1 !== null && p.set3_g2 !== null) {
                punteggioStr += `, ${p.set3_g1}-${p.set3_g2}`;
            }

            const dataFormatted = new Date(p.data_match).toLocaleDateString('it-IT', {
                day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            // Se l'utente è admin, genera il pulsante per attivare la modifica
            const adminButton = isAdmin() ? `
                <div class="admin-edit-controls" style="margin-top: 10px;">
                    <button class="btn-modifica-match" onclick="mostraFormModifica(${p.id_partita})">Modifica Punteggio</button>
                </div>
            ` : '';

            return `
                <div class="match-history-card" id="match-card-${p.id_partita}">
                    <div class="match-card-row">
                        <div>
                            <span class="match-esito-badge ${vittoria ? 'esito-vittoria' : 'esito-sconfitta'}">
                                ${vittoria ? 'Vittoria' : 'Sconfitta'}
                            </span>
                            <span class="match-title">${p.nome_g1} ${p.cognome_g1} vs ${p.nome_g2} ${p.cognome_g2}</span>
                        </div>
                        <span class="match-date">${dataFormatted}</span>
                    </div>
                    <div class="match-card-body">
                        Punteggio: <strong class="match-score">${punteggioStr}</strong>
                    </div>
                    ${adminButton}
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error(err);
        lista.innerHTML = '<p class="msg error">Errore nel caricamento dello storico.</p>';
    }
}


function mostraFormModifica(idPartita) {
    const p = partiteCache[idPartita]; 
    const card = $(`match-card-${idPartita}`);

    const val3_1 = p.set3_g1 !== null ? p.set3_g1 : '';
    const val3_2 = p.set3_g2 !== null ? p.set3_g2 : '';

    card.innerHTML = `
        <div class="tennis-scoreboard edit-board-box">
            <h4 class="edit-board-title">Modifica Punteggio</h4>
            
            <div class="score-row">
                <span class="row-label">${p.nome_g1}</span>
                <input type="number" id="edit_s1_1_${idPartita}" class="select-game" min="0" max="7" value="${p.set1_g1}" required>
                <input type="number" id="edit_s2_1_${idPartita}" class="select-game" min="0" max="7" value="${p.set2_g1}" required>
                <input type="number" id="edit_s3_1_${idPartita}" class="select-game" min="0" max="7" value="${val3_1}" placeholder="-">
            </div>
            
            <div class="score-row">
                <span class="row-label">${p.nome_g2}</span>
                <input type="number" id="edit_s1_2_${idPartita}" class="select-game" min="0" max="7" value="${p.set1_g2}" required>
                <input type="number" id="edit_s2_2_${idPartita}" class="select-game" min="0" max="7" value="${p.set2_g2}" required>
                <input type="number" id="edit_s3_2_${idPartita}" class="select-game" min="0" max="7" value="${val3_2}" placeholder="-">
            </div>
            
            <div class="edit-actions-wrap">
                <button class="btn-salva btn-salva-modifica" onclick="salvaModificaMatch(${idPartita})">Salva</button>
                <button class="btn-annulla-modifica" onclick="location.reload()">Annulla</button>
            </div>
            <div id="edit-error-${idPartita}" class="edit-error-msg"></div>
        </div>
    `;
}

async function salvaModificaMatch(idPartita) {
    const errDiv = $(`edit-error-${idPartita}`);
    const punteggi = leggiPunteggi(idPartita); // Legge passando l'idPartita per differenziare i campi

    if (!punteggi) {
        errDiv.innerText = "I primi 2 set sono obbligatori.";
        return;
    }

    if (!matchValido(punteggi)) {
        errDiv.innerText = "Errore: non può finire in pareggio!";
        return;
    }

    try {
        const response = await fetch(`/api/match/${idPartita}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                set1_g1: punteggi.set1_g1,
                set1_g2: punteggi.set1_g2,
                set2_g1: punteggi.set2_g1,
                set2_g2: punteggi.set2_g2,
                set3_g1: punteggi.set3_g1,
                set3_g2: punteggi.set3_g2
            })
        });

        if (response.ok) {
            location.reload(); // Ricarica per vedere i dati e i grafici aggiornati
        } else {
            const data = await response.json();
            errDiv.innerText = data.error || "Errore nel salvataggio.";
        }
    } catch {
        errDiv.innerText = "Errore di connessione.";
    }
}
//nuovi match
async function preparaFormInserimento() {
    $('boxInserimentoRisultati').classList.add('is-visible');

    const ranking = await fetch('/api/ranking').then(r => r.json());
    const arrayMaschile = ranking.maschile || [];
    const arrayFemminile = ranking.femminile || [];
    const soci = arrayMaschile.concat(arrayFemminile);

    $('selectAvversario').innerHTML = soci
        .filter(s => s.id_utente !== idProfilo)
        .map(s => `<option value="${s.id_utente}">${s.cognome} ${s.nome}</option>`)
        .join('');

    attivaAscoltoForm();
}

// ascolta inserimento match
function attivaAscoltoForm() {
    $('matchForm').onsubmit = async e => {
        e.preventDefault(); 
        const msg = $('matchMsg');
        const punteggi = leggiPunteggi();

        if (!punteggi || !matchValido(punteggi)) {
            msg.innerText = 'Errore nel punteggio! Compila almeno 2 set senza pareggi.';
            return;
        }

        try {
            const response = await fetch('/api/match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_avversario: parseInt($('selectAvversario').value),
                    set1_g1: punteggi.set1_g1,
                    set1_g2: punteggi.set1_g2,
                    set2_g1: punteggi.set2_g1,
                    set2_g2: punteggi.set2_g2,
                    set3_g1: punteggi.set3_g1,
                    set3_g2: punteggi.set3_g2
                })
            });

            if (response.ok) {
                msg.innerText = 'Match registrato con successo!';
                setTimeout(() => location.reload(), 1200); 
            } else {
                const data = await response.json();
                msg.innerText = data.error || 'Errore nel salvataggio.';
            }
        } catch {
            msg.innerText = 'Errore di connessione col server.';
        }
    };
}


function drawChart(vinte, perse) {
    if (vinte === 0 && perse === 0) return;

    const data = google.visualization.arrayToDataTable([
        ['Esito', 'Match'],
        ['Vinte', vinte],
        ['Perse', perse]
    ]);

    new google.visualization.PieChart($('winLossChart')).draw(data, {
        colors: ['#053C26', '#CB5A3E'],
        pieHole: 0.4,
        backgroundColor: 'transparent'
    });
}

window.addEventListener('DOMContentLoaded', caricaProfilo);