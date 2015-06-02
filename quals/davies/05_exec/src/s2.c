#include <stdio.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdlib.h>

char *socket_path = "/tmp/sock";

int main() {
  struct sockaddr_un addr;
  int fd,cl,rc;
  char byte;

  if ( (fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
    perror("socket error");
    exit(-1);
  }

  memset(&addr, 0, sizeof(addr));
  addr.sun_family = AF_UNIX;
  strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path)-1);

  unlink(socket_path);

  if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
    perror("bind error");
    exit(-1);
  }

  if (listen(fd, 5) == -1) {
    perror("listen error");
    exit(-1);
  }

  printf("ready...\n");
  
  while (1) {
    if ( (cl = accept(fd, NULL, NULL)) == -1) {
      perror("accept error");
      continue;
    }

    unsigned char state = 70;
    while(1) {
        if(recv(cl, &byte, 1, 0) != 1) {
            break;
        }

        if(byte % 2 == 0) {
            state -= byte;
        } else {
            state += byte;
        }

        if(send(cl, &state, 1, 0) != 1) {
            break;
        }
    }
    close(cl);
  }

  return 0;
}