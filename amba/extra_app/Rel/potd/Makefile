#
#	Copyright (C) 2012 Delta Networks Inc.
#

#CC = gcc
#include $(ACOSTOPDIR)/config.mk
#include $(ACOSTOPDIR)/config.in

default: all

# CFLAGS += -I. -I$(ACOSTOPDIR)/nvram -I$(ACOSTOPDIR)/shared -I$(ACOSTOPDIR)/include
CFLAGS	+= -s -O2

FILES = pot.c excmd.c common.h config.h
TARGET = potd potval ntpst stamac
CFLAGS += -Wall -Wunused -g
# LDFLAGS += -lconfig
# LDFLAGS += -L$(ACOSTOPDIR)/lib/libnvram -lacos_nvram
# LDFLAGS += -L$(ACOSTOPDIR)/shared -lacos_shared
LDFLAGS += -lm
LDFLAGS += -lgcc_s

all : $(TARGET)

potd : $(FILES)
	$(CC) $(CFLAGS) $(FILES) -o $@ $(EXTRA_LDFLAGS) $(LDFLAGS)
	@echo "make $@ finished on `date`"

potval: $(FILES)
	$(CC) $(CFLAGS) $(FILES) -o $@ $(EXTRA_LDFLAGS) $(LDFLAGS)
	@echo "make $@ finished on `date`"

ntpst: $(FILES)
	$(CC) $(CFLAGS) $(FILES) -o $@ $(EXTRA_LDFLAGS) $(LDFLAGS)
	@echo "make $@ finished on `date`"

stamac: $(FILES)
	$(CC) $(CFLAGS) $(FILES) -o $@ $(EXTRA_LDFLAGS) $(LDFLAGS)
	@echo "make $@ finished on `date`"

%.o : %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f *.o
	rm -f $(TARGET)
