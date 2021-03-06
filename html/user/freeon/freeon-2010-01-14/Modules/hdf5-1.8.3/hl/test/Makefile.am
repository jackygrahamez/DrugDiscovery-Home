#
# Copyright by The HDF Group.
# Copyright by the Board of Trustees of the University of Illinois.
# All rights reserved.
#
# This file is part of HDF5.  The full HDF5 copyright notice, including
# terms governing use, modification, and redistribution, is contained in
# the files COPYING and Copyright.html.  COPYING can be found at the root
# of the source code distribution tree; Copyright.html can be found at the
# root level of an installed copy of the electronic HDF5 document set and
# is linked from the top-level documents page.  It can also be found at
# http://hdfgroup.org/HDF5/doc/Copyright.html.  If you do not have
# access to either file, you may request a copy from help@hdfgroup.org.
#
#
## Makefile.am
## Run automake to generate a Makefile.in from this file.
#
# HDF5 High-Level Test Makefile(.in)
#

include $(top_srcdir)/config/commence.am

# Add include directories to C preprocessor flags
AM_CPPFLAGS=-I. -I$(srcdir) -I$(top_builddir)/src -I$(top_srcdir)/src -I$(top_builddir)/test -I$(top_srcdir)/test -I$(top_srcdir)/hl/src

# The tests depend on the hdf5, hdf5 test,  and hdf5_hl libraries
LDADD=$(LIBH5_HL) $(LIBH5TEST) $(LIBHDF5)

# Test programs.  These are our main targets.  They should be listed in the
# order to be executed, generally most specific tests to least specific tests.
TEST_PROG=test_lite test_image test_table test_ds test_packet
check_PROGRAMS=$(TEST_PROG)

# Temporary files.  These files are the ones created by running `make test'.
CHECK_CLEANFILES+=combine_tables[1-2].h5 test_ds[1-7].h5 test_image[1-3].h5 \
        test_lite[1-2].h5 test_table.h5 test_packet_table.h5                \
        test_packet_compress.h5

EXTRA_DIST = \
  dsdata.txt \
  dslat.txt \
  dslon.txt \
  dtype_file.txt \
  dtype_file_readable.txt \
  earth.pal \
  h5hltest.h \
  image24pixel.txt \
  image24plane.txt \
  image8.txt \
  pal_rgb.h \
  sepia.pal \
  test_table_be.hdf5 \
  test_table_cray.hdf5 \
  test_table_le.hdf5 \
  usa.wri

include $(top_srcdir)/config/conclude.am
