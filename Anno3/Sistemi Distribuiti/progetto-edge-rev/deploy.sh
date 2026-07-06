#!/bin/bash

# Controllo argomenti
if [ -z "$1" ]; then
  echo "Uso: ./deploy.sh <numero_di_dispatcher>"
  exit 1
fi

NUM_NODES=$1

if ! [[ "$NUM_NODES" =~ ^[0-9]+$ ]] || [ "$NUM_NODES" -lt 1 ]; then
  echo "Errore: il numero di nodi deve essere un intero positivo maggiore di 0."
  exit 1
fi

COMPOSE_FILE="docker-compose.yml"

echo "Generazione del file yaml per $NUM_NODES nodi..."

# Inizio del file docker-compose.yml
cat <<EOF > $COMPOSE_FILE
services:
  dispatcher-seed:
    build:
      context: .
      dockerfile: Dockerfile.dispatcher
    container_name: dispatcher-seed
    ports:
      - "5005:5005"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./shared_tasks:/app/shared_tasks
    environment:
      - HOST_SHARED_TASKS=\${PWD}/shared_tasks
      - LOCAL_SHARED_TASKS=/app/shared_tasks
    command: python dispatcher.py 5005 dispatcher-seed
    networks:
      - chord-net
EOF

# Generazione dei nodi peer aggiuntivi
for i in $(seq 1 $NUM_NODES); do
  PORT=$((5005 + i)) 

  cat <<EOF >> $COMPOSE_FILE

  dispatcher-$i:
    build:
      context: .
      dockerfile: Dockerfile.dispatcher
    container_name: dispatcher-$i
    ports:
      - "${PORT}:5005"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./shared_tasks:/app/shared_tasks
    environment:
      - HOST_SHARED_TASKS=\${PWD}/shared_tasks
      - LOCAL_SHARED_TASKS=/app/shared_tasks
    command: python dispatcher.py 5005 dispatcher-$i dispatcher-seed:5005
    depends_on:
      - dispatcher-seed
    networks:
      - chord-net
EOF
done

# Aggiunta della definizione di rete
cat <<EOF >> $COMPOSE_FILE

networks:
  chord-net:
    driver: bridge
EOF

echo "File yaml generato con successo."
echo "Eseguo il deploy del cluster..."

# Smonta eventuale cluster precedente e avvia il nuovo
docker compose down
docker compose up -d --build

echo "Deploy completato!"
