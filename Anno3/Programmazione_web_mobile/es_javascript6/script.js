let libreria = new Array ()
window.onload = function(){
    document.getElementById('add_book').addEventListener("click", function(event){
        event.preventDefault()
        add_book()
    })
    let stampa_libro = document.getElementById("stampa_collezione")   
    stampa_libro.addEventListener("click", function(event){
        event.preventDefault()
        stampa_collezione()
    })
}
function add_book(){
        let titolo = document.getElementById("titolo").value
        let autore = document.getElementById('autore').value
        let anno = document.getElementById('anno').value
        let libro = {
            titolo:titolo,
            anno:anno,
            autore:autore
        }
        libreria.push(libro)
        console.log(libreria)
    }

function stampa_collezione(){
    for(let libro of libreria){
        let newP = document.createElement("p")
        let text = ""
        for(let prop in libro){
            text += prop + ": "+ libro[prop] +" "
        }
        newP.textContent = text
        document.body.appendChild(newP)
    }
}

