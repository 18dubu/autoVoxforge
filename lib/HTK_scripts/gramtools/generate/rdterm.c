/*
 * Copyright (c) 1991-2006 Kawahara Lab., Kyoto University
 * Copyright (c) 2000-2005 Shikano Lab., Nara Institute of Science and Technology
 * Copyright (c) 2005-2006 Julius project team, Nagoya Institute of Technology
 * All rights reserved
 */

#include <sent/stddefs.h>
#include <sent/vocabulary.h>
#include <sent/dfa.h>
#include <sent/speech.h>
#include "common.h"

void
init_term(char *filename, char **termname)
{
  FILE *fd;
  int n;
  static char buf[512];
  
  j_printerr("Reading in term file (optional)...");
  
  if ((fd = fopen_readfile(filename)) == NULL) {
    termname[0] = NULL;
    j_printerr("not found\n");
    return;
  }

  while (getl(buf, sizeof(buf), fd) != NULL) {
    n = atoi(first_token(buf));
    termname[n] = strdup(next_token());
  }
  if (fclose_readfile(fd) == -1) {
    j_printerr("close error\n");
    exit(1);
  }

  j_printerr("done\n");
}
