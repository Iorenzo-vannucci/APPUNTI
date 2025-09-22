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

# Crea la cartella log se non esiste
mkdir -p log

# Pulisce i vecchi log
rm -f log/incrocio.txt log/auto.txt

echo -e "${GREEN_BOLD}Avvio del sistema dell'incrocio...${RESET}"

# 1) Avvia garage in background: crea shm + semafori
echo -e "${YELLOW_BOLD}Avviando processo garage...${RESET}"
./build/garage &

# 2) Breve attesa per essere sicuri che shm e semafori esistano
sleep 1

# 3) Avvia incrocio
echo -e "${YELLOW_BOLD}Avviando processo incrocio...${RESET}"
./build/incrocio