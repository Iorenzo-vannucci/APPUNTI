window.onload = function() {
    let banWords = ["pippo"];
    let submit = document.getElementById("submit");
    let inputTesto = document.getElementById("testo_inserito");
    function check_ban() {
            let valore = inputTesto.value;
            if (banWords.includes(valore)) {
                alert("Hai inserito una parola bannata: " + valore);
            }
    }
    submit.addEventListener("click", check_ban);
}