/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#include "doomgeneric.h"

static int connection;
static uint64_t start_ms;
static uint64_t last_frame_ms;
static unsigned char pending_key[2];
static size_t pending_count;

static uint64_t monotonic_ms(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (uint64_t)now.tv_sec * 1000 + now.tv_nsec / 1000000;
}

void DG_Init(void)
{
    start_ms = monotonic_ms();
}

static void send_bytes(const void *data, size_t remaining)
{
    const unsigned char *bytes = data;
    while (remaining > 0) {
        ssize_t sent = write(connection, bytes, remaining);
        if (sent < 0 && errno == EINTR)
            continue;
        if (sent <= 0)
            exit(sent < 0 && errno == EPIPE ? EXIT_SUCCESS : EXIT_FAILURE);
        bytes += sent;
        remaining -= (size_t)sent;
    }
}

void DG_DrawFrame(void)
{
    uint64_t now = monotonic_ms();
    if (now - last_frame_ms < 28)
        return;
    last_frame_ms = now;

    send_bytes(DG_ScreenBuffer, DOOMGENERIC_RESX * DOOMGENERIC_RESY * sizeof(pixel_t));
}

void DG_SleepMs(uint32_t ms)
{
    struct timespec duration = {ms / 1000, (ms % 1000) * 1000000L};
    while (nanosleep(&duration, &duration) == -1 && errno == EINTR) {
    }
}

uint32_t DG_GetTicksMs(void)
{
    return (uint32_t)(monotonic_ms() - start_ms);
}

int DG_GetKey(int *pressed, unsigned char *key)
{
    while (pending_count < sizeof(pending_key)) {
        ssize_t received = recv(connection, pending_key + pending_count,
                                sizeof(pending_key) - pending_count, MSG_DONTWAIT);
        if (received < 0 && errno == EINTR)
            continue;
        if (received < 0 && (errno == EAGAIN || errno == EWOULDBLOCK))
            return 0;
        if (received <= 0)
            exit(received == 0 ? EXIT_SUCCESS : EXIT_FAILURE);
        pending_count += (size_t)received;
    }
    *key = pending_key[0];
    *pressed = pending_key[1];
    pending_count = 0;
    return 1;
}

void DG_SetWindowTitle(const char *title)
{
    (void)title;
}

int main(int argc, char **argv)
{
    const char *fd = getenv("DOOM_GLYPH_FD");
    if (fd == NULL || sscanf(fd, "%d", &connection) != 1 || connection < 3) {
        fputs("Start this backend through doom_glyph.py.\n", stderr);
        return EXIT_FAILURE;
    }
    signal(SIGPIPE, SIG_IGN);
    doomgeneric_Create(argc, argv);
    for (;;)
        doomgeneric_Tick();
}
