function toggleMenu() {
    document.getElementById('menu').classList.toggle('active');
}

function toggleDropdown(event) {
    event.stopPropagation();
    document.getElementById('myDropdown').classList.toggle('show');
}


async function logout() {
    try {
        // Il server cancella il cookie JWT 
        await fetch('/api/logout', { method: 'POST' });

        window.location.href = '/index.html';
    } catch (error) {
        console.error('Errore durante il logout:', error);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const loginBtn = document.getElementById('menuLoginBtn');
    const userDropdown = document.getElementById('menuUserDropdown');
    const navUserIcon = document.getElementById('navUserIcon');
    const linkGestisciAccount = document.getElementById('linkGestisciAccount');

    try {
        const response = await fetch('/api/me');

        //se utentente no loggato
        if (response.status === 401) {
            if (loginBtn) loginBtn.style.display = 'block';
            if (userDropdown) userDropdown.style.display = 'none';
            return;
        }

        // Errore diverso dal 401
        if (!response.ok) {
            throw new Error('Errore nel recupero dell’utente.');
        }

        const utente = await response.json();

        if (loginBtn) loginBtn.style.display = 'none';
        if (userDropdown) userDropdown.style.display = 'block';

        if (navUserIcon) {
            navUserIcon.innerText =
                utente.genere === 'F' ? 'person_2' : 'person';
        }

        if (linkGestisciAccount) {
            linkGestisciAccount.href =
                `/giocatore.html?id=${utente.id_utente}`;
        }

    } catch (error) {
        console.error('Errore nel controllo dello stato utente:', error);
    }
});