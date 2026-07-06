#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <errno.h>
#include <ctype.h>
#include <unistd.h>
#include <signal.h>
#include <arpa/inet.h>

void Handler(int iSigNum) {
	printf("Handler: ricevuto %d, %s\n", iSigNum, strsignal(iSigNum));
	return;
}

/***************************************************************************************/
// Socket Server che converte in maiuscolo e visualizza una stringa ricevuta dai client.
// Accetta connessioni fin quando un client non invia la stringa "exit", dopodiché
// termina.
// Riceve un argomento che è il "Coomunication Domain", che può essere AF_UNIX o AF_INET
/***************************************************************************************/
int main(int argc, char *argv[]) {
	int iRet = EXIT_SUCCESS, iDomain;
	
	if(argc >= 2) {
		if(!strcmp(argv[1], "AF_UNIX"))
			iDomain = AF_UNIX;
		else
			if(!strcmp(argv[1], "AF_INET"))
				iDomain = AF_INET;
			else {
				// fprintf() è una funzione della Standard I/O Library del C.
				// Funziona come printf() ma invece che scrivere a video scrive
				// nel file riferito dal primo argomento (di tipo FILE *). Nel nostro
				// caso standard error
				fprintf(stderr, "Communication Domain non gestito!\n");
				return EXIT_FAILURE;
			}
		
		int fds, fdc, stSize;
		struct sockaddr_in sa_in; // per AF_INET
		struct sockaddr_un sa_un; // per AF_UNIX
		struct sockaddr *sa;
		
		struct sigaction stSigAction;
		memset(&stSigAction, '\0', sizeof(stSigAction));
		stSigAction.sa_handler = Handler;
		sigaction(SIGINT, &stSigAction, NULL);

		if((fds = socket(iDomain, SOCK_STREAM, 0)) != -1) {
			if(iDomain == AF_UNIX) {
				sa_un.sun_family = AF_UNIX;
				strcpy(sa_un.sun_path, "/tmp/my_sock");
				sa = (struct sockaddr *)&sa_un;
				stSize = sizeof(struct sockaddr_un);
			}
			else {
				sa_in.sin_family = AF_INET;
				sa_in.sin_port = htons(6530); // Host to netword byte order
				inet_aton("127.0.0.1", &sa_in.sin_addr); // converte in neywork byte order
				sa = (struct sockaddr *)&sa_in;
				stSize = sizeof(struct sockaddr_in);
			}
			if(bind(fds, sa, stSize) != -1) {
				if(listen(fds, 16) != -1) {
					char sBuf[128];
					sBuf[0] ='\0';
					while(strcmp(sBuf, "EXIT")) {
						do { fdc = accept(fds, NULL, NULL); } while(fdc == -1 && errno == EINTR);
						if(fdc != -1) {
							int iReadRet;
							printf("Accepted connession #%d\n", fdc);
							/********************************************************************/
							// Se si utilizza AF_UNIX (in AF_INET è più complicato...),
							// decommentare il seguente bolocco per ottenere nel client l'errore 
							// "Connection closed by peer". Il client scrive con write() quando
							// il server ha chiuso la connessione, il processo client riceve
							// SIGPIPE, la write si interrompe tornando -1 ed impostando errno a
							// EPIPE
							/********************************************************************/
							/* close(fdc);
							continue; */
							/********************************************************************/
							
							do {
									iReadRet = read(fdc, sBuf, sizeof(sBuf) - 1);
							   } while(iReadRet == -1 && errno == EINTR);
							if(iReadRet == -1) {
								perror("read()");
								iRet = EXIT_FAILURE;
							}
							else {
								if(iReadRet == 0) {
									/********************************************************************/
									// Se il client ha chiuso la connessione read() torna 0
									/********************************************************************/
									fprintf(stderr, "read(): Connection closed by peer\n");
									iRet = EXIT_FAILURE;
								}
								else {
									sBuf[iReadRet] = '\0';
									for(int i = 0; i < iReadRet; i++)
										sBuf[i] = toupper(sBuf[i]);
									printf("Server: ho convertito in %s\n", sBuf);
								}
							}
							close(fdc);
						}
						else {
							perror("accept()");
							iRet = EXIT_FAILURE;
							break;
						}
					}
				}
				else {
					perror("listen()");
					iRet = EXIT_FAILURE;
				}			
			}
			else {
				perror("bind()");
				iRet = EXIT_FAILURE;
			}	
			
			close(fds);
		}
		else {
			perror("socket()");
			iRet = EXIT_FAILURE;
		}
	}
	else {
		fprintf(stderr, "Usage: %s Communication_domain (AF_UNIX or AF_UNET)\n", argv[0]);
		iRet = EXIT_FAILURE;
	}
	printf("Server %d: exiting...\n", getpid());

	return iRet;
}
