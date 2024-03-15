# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT nTSDR_Local_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT nTSDR_Local_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND nTSDR_Local_python_files
    python_bindings.cc)

GR_PYBIND_MAKE_OOT(nTSDR_Local
   ../../..
   gr::nTSDR_Local
   "${nTSDR_Local_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(TARGET nTSDR_Local_python POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:nTSDR_Local_python>
    ${PROJECT_BINARY_DIR}/test_modules/gnuradio/nTSDR_Local/
)

install(TARGETS nTSDR_Local_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/nTSDR_Local COMPONENT pythonapi)
