#!/usr/bin/env bash
#
# build.sh – compila e (facoltativamente) lancia il progetto "Incrocio".
# usage:
#   ./build.sh           # solo build
#   ./build.sh run       # build + esecuzione automatica
#   ./build.sh clean     # rimuove artefatti di build
#

set -euo pipefail        # stop immediato su errori

SRC_DIR="src"
BUILD_DIR="build"
BIN_DIR="${BUILD_DIR}/bin"

CFLAGS="-std=c11 -Wall -Wextra -pedantic"
LIBS="-pthread"

clean() {
  echo "Cleaning build artefacts..."
  rm -rf "${BUILD_DIR}"
  rm -f incrocio.txt auto.txt          # log della sessione precedente
  # eventuale pulizia di risorse IPC residue
  ipcrm -M 0x1234 2>/dev/null || true  # memoria condivisa
  ipcrm -S 0x5678 2>/dev/null || true  # semafori
}

build() {
  echo "Building binaries..."
  mkdir -p "${BIN_DIR}"

  # compila oggetti comuni
  gcc ${CFLAGS} -c "${SRC_DIR}/utils.c"   -o "${BUILD_DIR}/utils.o"

  # compila gli eseguibili principali
  gcc ${CFLAGS} "${SRC_DIR}/incrocio.c"  "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/incrocio"  ${LIBS}
  gcc ${CFLAGS} "${SRC_DIR}/garage.c"    "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/garage"    ${LIBS}
  gcc ${CFLAGS} "${SRC_DIR}/automobile.c" "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/automobile" ${LIBS}

  echo "Build completed. Binaries in ${BIN_DIR}/"
}

run() {
  echo "Launching application..."
  rm -f incrocio.txt auto.txt            # log freschi

  "${BIN_DIR}/incrocio" & INC_PID=$!
  sleep 1                                # assicura che incrocio sia pronto
  "${BIN_DIR}/garage"   & GAR_PID=$!

  trap 'echo -e "\n↳ Stopping..."; kill -TERM ${INC_PID} ${GAR_PID} 2>/dev/null; wait ${INC_PID}; exit' INT
  wait ${INC_PID}                        # incrocio termina per ultimo
}

case "${1:-build}" in
  clean) clean ;;
  run)   build && run ;;
  *)     build ;;
esac