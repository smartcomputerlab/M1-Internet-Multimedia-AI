// tcpsend.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BUFLEN 512      // Max length of buffer
#define PORT 8888       // the port on which to send or listen for data
#define REMOTE_ADDR  "192.168.1.72"
#define LOCAL_LOOP  "127.0.0.1"

void die(char *s)      // exit with message
{
        perror(s);exit(1);
}

int main(void)
{
  struct sockaddr_in si_me, si_other;
  int s, i, slen = sizeof(si_other) , recv_len;
  char buf[BUFLEN];
  s = socket(AF_INET, SOCK_STREAM, 0);
  memset((char *) &si_other, 0, sizeof(si_other));
  si_other.sin_family = AF_INET;
//si_other.sin_port = htons(PORT);    // to work remotely
  si_other.sin_port = htons(PORT+1);  // to work locally
//si_other.sin_addr.s_addr = htonl(INADDR_ANY); // to work locally
//si_other.sin_addr.s_addr = inet_addr(REMOTE_ADDR);   // to work remotely 
  si_other.sin_addr.s_addr = inet_addr(LOCAL_LOOP);   // to work on local loop 
  if(connect(s,(struct sockaddr *)&si_other,sizeof(si_other))<0)
	die("connect") ;
  else
    {
    while(1)
      {
      memset(buf,0x00,BUFLEN);
      printf("write the message, replace spaces by _, end session with . message\n");
      scanf("%s",buf);
      if(write(s,buf,strlen(buf)+1)<0) die("write") ;
      sleep(3);
      if(buf[0]=='.') break;
      }
    }
  close(s);
}


