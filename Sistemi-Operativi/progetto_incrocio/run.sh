#!/usr/bin/env bash
set -e

# Colori ANSI
GREEN_BOLD='\033[1;32m'
RED_BOLD='\033[1;31m'
YELLOW_BOLD='\033[1;33m'
RESET='\033[0m'

cat <<'CROSS'
 ▄▄▄▄▄▄▄▄▄▄▄ ▄▄        ▄ ▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▐░░▌      ▐░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▌
 ▀▀▀▀█░█▀▀▀▀▐░▌░▌     ▐░▐░█▀▀▀▀▀▀▀▀▀▐░█▀▀▀▀▀▀▀█░▐░█▀▀▀▀▀▀▀█░▐░█▀▀▀▀▀▀▀▀▀ ▀▀▀▀█░█▀▀▀▀▐░█▀▀▀▀▀▀▀█░▌
     ▐░▌    ▐░▌▐░▌    ▐░▐░▌         ▐░▌       ▐░▐░▌       ▐░▐░▌              ▐░▌    ▐░▌       ▐░▌
     ▐░▌    ▐░▌ ▐░▌   ▐░▐░▌         ▐░█▄▄▄▄▄▄▄█░▐░▌       ▐░▐░▌              ▐░▌    ▐░▌       ▐░▌
     ▐░▌    ▐░▌  ▐░▌  ▐░▐░▌         ▐░░░░░░░░░░░▐░▌       ▐░▐░▌              ▐░▌    ▐░▌       ▐░▌
     ▐░▌    ▐░▌   ▐░▌ ▐░▐░▌         ▐░█▀▀▀▀█░█▀▀▐░▌       ▐░▐░▌              ▐░▌    ▐░▌       ▐░▌
     ▐░▌    ▐░▌    ▐░▌▐░▐░▌         ▐░▌     ▐░▌ ▐░▌       ▐░▐░▌              ▐░▌    ▐░▌       ▐░▌
 ▄▄▄▄█░█▄▄▄▄▐░▌     ▐░▐░▐░█▄▄▄▄▄▄▄▄▄▐░▌      ▐░▌▐░█▄▄▄▄▄▄▄█░▐░█▄▄▄▄▄▄▄▄▄ ▄▄▄▄█░█▄▄▄▄▐░█▄▄▄▄▄▄▄█░▌
▐░░░░░░░░░░░▐░▌      ▐░░▐░░░░░░░░░░░▐░▌       ▐░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀▀▀ ▀        ▀▀ ▀▀▀▀▀▀▀▀▀▀▀ ▀         ▀ ▀▀▀▀▀▀▀▀▀▀▀ ▀▀▀▀▀▀▀▀▀▀▀ ▀▀▀▀▀▀▀▀▀▀▀ ▀▀▀▀▀▀▀▀▀▀▀ 
                                                                                                 
CROSS

# Funzione per terminare tutti i processi
cleanup() {
    echo -e "${YELLOW_BOLD}Terminazione in corso...${RESET}"
    pkill -f "./build/garage" 2>/dev/null || true
    pkill -f "./build/incrocio" 2>/dev/null || true 
    pkill -f "./build/automobile" 2>/dev/null || true
    echo -e "${GREEN_BOLD}Tutti i processi terminati${RESET}"
    exit 0
}

# Gestione errori con messaggio colorato
trap 'echo -e "${RED_BOLD} Errore durante l'\''esecuzione!${RESET}"; cleanup' ERR

# Cattura Ctrl+C (SIGINT) e altri segnali di terminazione
trap cleanup SIGINT SIGTERM

# Crea la cartella log se non esiste
mkdir -p log

# Pulisce i vecchi log
rm -f log/incrocio.txt log/auto.txt

# 1) Avvia garage in background: crea shm + semafori
./build/garage &
GARAGE_PID=$!

# 2) Breve attesa per essere sicuri che shm e semafori esistano
sleep 1

# 3) Avvia incrocio (attenderà sem_garage)
./build/incrocio

# 4) Quando incrocio termina, pulisce garage
cleanup