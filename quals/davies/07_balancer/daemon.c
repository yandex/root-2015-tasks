#include <stdio.h>
#include <errno.h>
#include <sys/socket.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>
#include <stdlib.h>
#include <strings.h>
#include <unistd.h>
#include <time.h>
#include <openssl/pem.h>
#include <openssl/ssl.h>
#include <openssl/rsa.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/err.h>
#include <stdio.h>

#define MY_PORT     9000 /* Скомпилить с разными портами */
#define MAXBUF      1024
#define PADDING RSA_PKCS1_PADDING
static char encoding_table[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                                'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                                'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
                                'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                                'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                                'w', 'x', 'y', 'z', '0', '1', '2', '3',
                                '4', '5', '6', '7', '8', '9', '+', '/'};
static int mod_table[] = {0, 2, 1};


char *base64_encode(const unsigned char *data,
                    size_t input_length,
                    size_t *output_length) {

    int i, j;

    *output_length = 4 * ((input_length + 2) / 3);

    char *encoded_data = malloc(*output_length);
    if (encoded_data == NULL) return NULL;

    for (i = 0, j = 0; i < input_length;) {

        uint32_t octet_a = i < input_length ? (unsigned char)data[i++] : 0;
        uint32_t octet_b = i < input_length ? (unsigned char)data[i++] : 0;
        uint32_t octet_c = i < input_length ? (unsigned char)data[i++] : 0;

        uint32_t triple = (octet_a << 0x10) + (octet_b << 0x08) + octet_c;

        encoded_data[j++] = encoding_table[(triple >> 3 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 2 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 1 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 0 * 6) & 0x3F];
    }

    for (i = 0; i < mod_table[input_length % 3]; i++)
        encoded_data[*output_length - 1 - i] = '=';

    return encoded_data;
}

int main(int Count, char *Strings[])
{   int sockfd;
    int one = 1;
    struct sockaddr_in self;
    char buffer[MAXBUF];
    char current = 0;
    char publicKey[] = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC4cqgmcwp9TaeucqhFli0HtmnH\nKfn5iy91tyoG3o4ZAdU4wIw/NH5c8IAlPqTo/tYP9O3xUg50ep0/+x3Lp02vjDF8\n51UfnQSoj/z76qtXN66IGXT11QpenhGzLIOyex0uh0LuqC96jyQrtIEwsx0BQLGp\n3jXS0l1BfnHH9U+E7wIDAQAB\n-----END PUBLIC KEY-----\n";
    BIO *bio = BIO_new_mem_buf((void*)publicKey, -1);
    RSA *rsa = PEM_read_bio_RSA_PUBKEY(bio, NULL, NULL, NULL);
    BIO_free(bio);

    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0 )
    {
        perror("Socket");
        exit(errno);
    }
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    bzero(&self, sizeof(self));
    self.sin_family = AF_INET;
    self.sin_port = htons(MY_PORT);
    self.sin_addr.s_addr = INADDR_ANY;
    if ( bind(sockfd, (struct sockaddr*)&self, sizeof(self)) != 0 )
    {
        perror("socket--bind");
        exit(errno);
    }
    if ( listen(sockfd, 20) != 0 )
    {
        perror("socket--listen");
        exit(errno);
    }
    while (1)
    {   int clientfd;
        struct sockaddr_in client_addr;
        unsigned int addrlen=sizeof(client_addr);
        char *response;
        unsigned char encrypted[1024] = { 0 };
        char plainText[30];
        size_t length = 0;
        clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        sprintf(plainText, "%d%ld", MY_PORT, time(NULL));
        RSA_public_encrypt(strlen(plainText), plainText, encrypted, rsa, PADDING);
        response = base64_encode(encrypted, strlen(encrypted), &length);
        send(clientfd, response, strlen(response), 0);
        close(clientfd);
    }
    close(sockfd);
    return 0;
}
