
//  udprecv.c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define BUFLEN 512      //Max length of buffer
#define PORT 8889       //The port on which to listen for incoming data
#define LOCAL_LOOP	"127.0.0.1"

void die(char *s)
{
        perror(s);
        exit(1);
}

int main(void)
{
  struct sockaddr_in si_me, si_other;
  int s, i, slen = sizeof(si_other),rlen;
  char buf[BUFLEN];
  //create a UDP socket
  if ((s=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP))==-1) {die("socket");}
  // zero out the structure
  memset((char *) &si_me, 0, sizeof(si_me));
  si_me.sin_family = AF_INET;
  si_me.sin_port = htons(PORT);
  //si_me.sin_addr.s_addr = htonl(INADDR_ANY);
  si_me.sin_addr.s_addr = inet_addr(LOCAL_LOOP);
  //bind socket to port
  if( bind(s,(struct sockaddr*)&si_me,sizeof(si_me))==-1) {die("bind");}
  //keep listening for data
  while(1)
    {
    printf("Waiting for data...");
    //try to receive some data, this is a blocking call
    if((rlen=recvfrom(s,buf,BUFLEN,0,(struct sockaddr *)&si_other,&slen))==-1)
      {die("recvfrom()"); }
    //print details of the client/peer and the data received
    printf("IP, port %s:%d\n",inet_ntoa(si_other.sin_addr),
				      ntohs(si_other.sin_port));
    printf("Received data: %s\n", buf);
    }
  close(s);
  return 0;
}

