const elencoFoto = [
    "foto/torneo1.png",
    "foto/torneo2.png",
    "foto/torneo3.png",
    "foto/torneo4.png"
];

let indice = 0;

function cambiaFoto(indice) {
    const elementoImg = document.getElementById('sliderImg');
    const tuttiIPallini = document.getElementsByClassName('dot');
    
    elementoImg.src = elencoFoto[indice];
    
    for (let i = 0; i < tuttiIPallini.length; i++) {
        if (i === indice) {
            tuttiIPallini[i].classList.add('active');
        } else {
            tuttiIPallini[i].classList.remove('active');
        }
    };
}

// Avvia l'autoplay in background
setInterval(function() {
    indice = (indice + 1) % elencoFoto.length;
    cambiaFoto(indice);
}, 4000);