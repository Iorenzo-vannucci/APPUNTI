function paragraphs(n){
    const num_paragraphs = parseInt(n)
    for(let i=0; i<num_paragraphs; i++){
        let nodo = document.createElement("p");
        nodo.textContent = "Molti supereroi volano";
        document.body.appendChild(nodo);
    }
}