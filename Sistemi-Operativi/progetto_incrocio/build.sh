#!/usr/bin/env bash
set -e

# Colori ANSI
GREEN_BOLD='\033[1;32m'
RED_BOLD='\033[1;31m'
RESET='\033[0m'

# Gestione errori con messaggio colorato
trap 'echo -e "${RED_BOLD}Build fallita!${RESET}"; exit 1' ERR

# Crea la cartella build se non esiste
mkdir -p build

# su macOS non serve -lrt, su Linux invece sì
if [[ "$(uname)" == "Darwin" ]]; then
  EXTRA_LIBS=""
else
  EXTRA_LIBS="-lrt"
fi

gcc -o build/garage     src/garage.c     src/direzioni.c $EXTRA_LIBS
gcc -o build/incrocio   src/incrocio.c   src/direzioni.c $EXTRA_LIBS
gcc -o build/automobile src/automobile.c                   $EXTRA_LIBS

echo -e "${GREEN_BOLD}Build completata! Eseguibili creati nella cartella build/${RESET}"