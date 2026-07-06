#!/bin/bash

ServerIsRunning(){
    echo -e "\n `ps j -C ${SERVER}` \n"       #aggiungo delle sequenze di escape 
}

if test $# -lt 1
then 
    echo "Usage: `basename $0` comm-domain" >&2
    exit -1
fi

RET=0
SOCKET="$1"
SERVER=s
CLIENT=c
SOCKET_PATH="/tmp/my_sock"

STRINGAEXIT="EXIT"
if test "$SOCKET" != AF_UNIX -a "$SOCKET" != AF_INET
then    
    echo "Communication Domain $SOCKET non gestito" >&2
    exit -1
fi

if test ! -f "${SERVER}.c" -a ! -f "${CLIENT}.c"
then    
    echo "Eseguibile/i non trovato/i" >&2
    exit -1
fi

gcc -o "${SERVER}" "${SERVER}.c"
RET=$?
if test $RET -eq 0
then
    gcc -o "${CLIENT}" "${CLIENT}.c"
    RET=$?
        if test $RET -eq 0
        then
            rm "${SOCKET_PATH}"
        
        ./"${SERVER}" "$SOCKET" &

        STRINGA="aaa"
        while test "${STRINGA}^^" != "${STRINGAEXIT}"
        do

            ServerIsRunning 
            read -p "Inserisci la stringa da inviare al server: " STRINGA


            ./"${CLIENT}" $SOCKET "${STRINGA}"
            if test $? -ne 0

            then
                break
            fi
        done

        wait 
    fi  
fi

exit $RET

    