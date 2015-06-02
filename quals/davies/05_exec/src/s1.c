#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/wait.h>
 
/* the port users will be connecting to */
#define MYPORT 3255
/* how many pending connections queue will hold */
#define BACKLOG 1000
  
char *socket_path = "/tmp/sock";


int main(int argc, char *argv[ ])
{
    int sockfd, new_fd;
    struct sockaddr_in my_addr;
    struct sockaddr_in their_addr;
    struct sockaddr_un u_addr;

    int sin_size;
    int yes = 1;
    char byte;
     
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        exit(1);
    }
     
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));
     
    my_addr.sin_family = AF_INET;
    my_addr.sin_port = htons(MYPORT);
    my_addr.sin_addr.s_addr = INADDR_ANY;
     
    printf("Listen on %s and port %d...\n", inet_ntoa(my_addr.sin_addr), MYPORT);
     
    /* zero the rest of the struct */
    memset(&(my_addr.sin_zero), '\0', 8);
     
    if(bind(sockfd, (struct sockaddr *)&my_addr, sizeof(struct sockaddr)) == -1) {
        printf("Bind failed\n");
        exit(1);
    }
     
    if(listen(sockfd, BACKLOG) == -1) {
        printf("Listen failed\n");
        exit(1);
    }
          
    while(1) {

        sin_size = sizeof(struct sockaddr_in);
        if((new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size)) == -1) {
            continue;
        }
        printf("Got connection from %s\n", inet_ntoa(their_addr.sin_addr));
                  
        if(send(new_fd, "Hi!\n", 4, 0) == -1) {
             perror("Send error");
             continue;
        }
        
        unsigned char state = 55;

        int u_fd;
        if ( (u_fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
            perror("socket error");
            exit(1);
        }

        memset(&u_addr, 0, sizeof(u_addr));
        u_addr.sun_family = AF_UNIX;
        strncpy(u_addr.sun_path, socket_path, sizeof(u_addr.sun_path) - 1);

        if (connect(u_fd, (struct sockaddr*)&u_addr, sizeof(u_addr)) == -1) {
            perror("connect error");
            close(new_fd);
            continue;
        }

        while(1) {
            if(recv(new_fd, &byte, 1, 0) != 1) {
                break;
            }

            if(byte % 2 == 0) {
                state += byte;
            } else {
                state -= byte;
            }

            if(send(u_fd, &state, 1, 0) != 1) {
                break;
            }

            if(recv(u_fd, &byte, 1, 0) != 1) {
                break;
            }

            if(send(new_fd, &byte, 1, 0) != 1) {
                break;
            }
        }

        /* parent doesn’t need this*/
        close(u_fd);
        close(new_fd);
    }
    printf("End is reached\n");
    return 0;
}
