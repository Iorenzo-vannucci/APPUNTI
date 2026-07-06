#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <sys/un.h>
#include <errno.h>
#include <ctype.h>
#include <unistd.h>
#include <signal.h>
#include <arpa/inet.h>

/***************************************************************************************/
// Riceve due argomenti:
// - il "Coomunication Domain", che può essere AF_UNIX o AF_INET
// - stringa da inviare al server per essere convertita in maiuscolo
/***************************************************************************************/
int main(int argc, char *argv[]) {
	int iRet = EXIT_SUCCESS, iDomain;
	
	if(argc >= 3) {
		if(!strcmp(argv[1], "AF_UNIX"))
			iDomain = AF_UNIX;
		else
			if(!strcmp(argv[1], "AF_INET"))
				iDomain = AF_INET;
			else {
				fprintf(stderr, "Communication Domain non gestito!\n");
				return EXIT_FAILURE;
			}
		
		int fdc, stSize;
		struct sockaddr_in sa_in; // per AF_INET
		struct sockaddr_un sa_un; // per AF:UNIX
		struct sockaddr *sa;
		
		/***************************************************************************************/
		// Se write() scrive quando il server ha chiuso la connessione il processo riceve
		// SIGPIPE, la cui disposition di default è di terminare. Ignoriamo SIGPIPE. In queso modo
		// write() ritoprna -1 ed errno è settato a EPIPE.
		/***************************************************************************************/
		struct sigaction stSigAction;
		memset(&stSigAction, '\0', sizeof(stSigAction));
		stSigAction.sa_handler = SIG_IGN;
		sigaction(SIGPIPE, &stSigAction, NULL);

		if((fdc = socket(iDomain, SOCK_STREAM, 0)) != -1) {
			if(iDomain == AF_UNIX) {
				sa_un.sun_family = AF_UNIX;
				strcpy(sa_un.sun_path, "/tmp/my_sock");
				sa = (struct sockaddr *)&sa_un;
				stSize = sizeof(struct sockaddr_un);
			}
			else {
				sa_in.sin_family = AF_INET;
				sa_in.sin_port = htons(6530);
				inet_aton("127.0.0.1", &sa_in.sin_addr);
				sa = (struct sockaddr *)&sa_in;
				stSize = sizeof(struct sockaddr_in);
			}
			if(connect(fdc, sa, stSize) != -1) {
				char sBuf[128];
				strcpy(sBuf, argv[2]);
				// usleep() esegue un'attesa in microsecondi
				usleep(100000L);
				/**************************************************************/
				// Commentare tutto il blocco relativo a write() per far sì che
				// nel clent la funzione read() ritorni 0 (EOF)
				/**************************************************************/
				if(write(fdc, sBuf, strlen(sBuf)) == -1) {
					if(errno == EPIPE) {
						// Vedi commento sopra relativo a SIGPIPE
						fprintf(stderr, "Connection closed by peer\n");
						iRet = EXIT_FAILURE;
					}
					else {
						perror("write()");
						iRet = EXIT_FAILURE;
					}
				}
				/**************************************************************/
			}	
			else {
				perror("connect()");
				iRet = EXIT_FAILURE;			
			}
			
			close(fdc);
		}
		else {
			perror("socket()");
			iRet = EXIT_FAILURE;
		}
	}
	else {
		fprintf(stderr, "Usage: %s comm_domain sgtringa\n", argv[0]);
		iRet = EXIT_FAILURE;
	}	
	printf("Client %d: exiting...\n", getpid());

	return iRet;
}