//  udpsend.c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define BUFLEN 512      // Max length of buffer
#define PORT 8888       // The port on which to send or listen for data
//#define REMOTE_ADDR  "192.168.1.72"
#define REMOTE_ADDR  "127.0.0.1"   // local loop
#define LOCAL_LOOP  "127.0.0.1"   // local loop

void die(char *s)      // exit with message
{
  perror(s); exit(1);
}

int main(void)
{
  struct sockaddr_in si_me, si_other;
  int s, i, slen = sizeof(si_other) , recv_len;
  char buf[BUFLEN];
  // create a UDP socket
  if ((s=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP))==-1){die("socket");}
  // zero out the structure me (sender) 
  // this structure and bind() are optional !
  memset((char *) &si_me, 0, sizeof(si_me));
  si_me.sin_family = AF_INET;
  si_me.sin_port = htons(PORT);
  //si_me.sin_addr.s_addr = htonl(INADDR_ANY);
  si_me.sin_addr.s_addr =inet_addr(LOCAL_LOOP);
  //bind socket to port
  if(bind(s,(struct sockaddr*)&si_me,sizeof(si_me) )==-1){die("bind");}
  // zero out the structure other (receiver) - this structure is mandatory
  memset((char *) &si_other, 0, sizeof(si_other));
  si_other.sin_family = AF_INET;
//si_other.sin_port = htons(PORT);    // to work remotely
  si_other.sin_port = htons(PORT+1);  // to work locally
//si_other.sin_addr.s_addr = htonl(INADDR_ANY); // to work locally
//si_other.sin_addr.s_addr = inet_addr(REMOTE_ADDR);   // to work remotely
  si_other.sin_addr.s_addr = inet_addr(LOCAL_LOOP);   // to work local loop
  //keep sending data
  while(1)
    {
    printf("write message:");scanf("%s\n",buf);
    //try to send data, this is a non blocking call
    if((sendto(s,buf,strlen(buf)+1,0,(struct sockaddr *)&si_other,slen)) == -1)
      { die("sendto()"); }
    }
  close(s);
  return 0;
}

