#!/bin/bash

# Script per compilare e avviare l'applicazione Incrocio
# Progetto di Sistemi Operativi con Laboratorio

echo "=================================================="
echo "     PROGETTO INCROCIO - AVVIO APPLICAZIONE"
echo "=================================================="

# Pulizia file precedenti
echo "Pulizia file di log precedenti..."
rm -f incrocio.txt auto.txt

# Compilazione
echo "Compilazione del progetto..."
if ! ./build.sh; then
    echo "Errore nella compilazione!"
    exit 1
fi

echo ""
echo "Compilazione completata con successo!"
echo ""

# Pulizia risorse IPC precedenti (nel caso fossero rimaste)
echo "Pulizia risorse IPC precedenti..."
ipcrm -M 0x1234 2>/dev/null || true
ipcrm -S 0x5678 2>/dev/null || true

echo ""
echo "Avvio dell'applicazione..."
echo "=================================================="
echo ""

# Avvia il processo incrocio in background
echo "Avvio processo incrocio..."
./build/bin/incrocio &
INCROCIO_PID=$!

# Aspetta un momento per l'inizializzazione
sleep 2

# Avvia il processo garage in background  
echo "Avvio processo garage..."
./build/bin/garage &
GARAGE_PID=$!

echo ""
echo "PROCESSI AVVIATI:"
echo "   Incrocio PID: $INCROCIO_PID"
echo "   Garage PID: $GARAGE_PID"
echo ""
echo "COMANDI UTILI:"
echo "   - Per vedere i processi: ps aux | grep -E '(incrocio|garage|automobile)'"
echo "   - Per terminare gracefully: kill -TERM $INCROCIO_PID"
echo "   - Per vedere i file di log: tail -f incrocio.txt auto.txt"
echo ""
echo "L'applicazione sta funzionando..."
echo "    Ctrl+C NON termina gracefully secondo le specifiche!"
echo "    Per terminare correttamente: kill -TERM $INCROCIO_PID"
echo ""

# Gestione della terminazione (solo per script)
trap "echo ''; echo ' Terminazione forzata dello script...'; kill -TERM $INCROCIO_PID 2>/dev/null; sleep 2; kill -9 $INCROCIO_PID $GARAGE_PID 2>/dev/null; exit 0" INT TERM

# Attende la terminazione dei processi
wait $INCROCIO_PID $GARAGE_PID

echo ""
echo "Applicazione terminata"

# Mostra i risultati
echo ""
echo "RISULTATI:"
echo "=================================================="

if [ -f "incrocio.txt" ] && [ -f "auto.txt" ]; then
    echo "Contenuto incrocio.txt:"
    cat incrocio.txt
    echo ""
    echo "Contenuto auto.txt:"
    cat auto.txt
    echo ""
    
    # Verifica che i file siano identici
    if diff incrocio.txt auto.txt >/dev/null; then
        echo "SUCCESS: I file incrocio.txt e auto.txt sono identici!"
    else
        echo "ERROR: I file incrocio.txt e auto.txt sono diversi!"
        echo "Differenze:"
        diff incrocio.txt auto.txt
    fi
else
    echo "I file di output non sono stati creati"
fi

echo ""
echo "==================================================" 