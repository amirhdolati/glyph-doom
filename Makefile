# SPDX-License-Identifier: GPL-2.0-or-later
.DEFAULT_GOAL := all

CC = cc
BUILD = .build
DOOM = $(BUILD)/upstream/doomgeneric
OBJ = $(BUILD)/pixel-objects

# Use the pinned upstream core list and replace its X11 platform.
DOOM_OBJECTS = $(filter-out doomgeneric_xlib.o,$(shell sed -n 's/^SRC_DOOM = //p' "$(DOOM)/Makefile"))
OBJECTS = $(addprefix $(OBJ)/,$(DOOM_OBJECTS)) $(OBJ)/glyph_platform.o
CPPFLAGS += -I. -I$(DOOM) -DDOOMGENERIC_RESX=320 -DDOOMGENERIC_RESY=200
CFLAGS += -O2 -std=gnu11 -fwrapv -fno-strict-aliasing -MMD -MP
LDLIBS += -lm

.PHONY: all
all: $(BUILD)/doom-pixels

$(BUILD)/doom-pixels: $(OBJECTS)
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@

$(OBJ)/%.o: $(DOOM)/%.c | $(OBJ)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(OBJ)/glyph_platform.o: glyph_platform.c | $(OBJ)
	$(CC) $(CPPFLAGS) $(CFLAGS) -Wall -Wextra -c $< -o $@

$(OBJ):
	mkdir -p "$@"

-include $(OBJECTS:.o=.d)
