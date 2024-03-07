# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT nTSDR_Local_sources)
	MESSAGE(STATUS "No C++ sources... skipping swig/")
	return()
endif(NOT nTSDR_Local_sources)

########################################################################
# Include swig generation macros
########################################################################
find_package(SWIG)
find_package(PythonLibs 3)

# Location path bugged
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    message( FATAL_ERROR "swig package not found. You need to Install Package swig")
    return()
elseif(NOT PYTHONLIBS_FOUND)
    message( FATAL_ERROR "PythonLibs not found. You need to Install Package python-scipy")
    return()
endif()

include(GrSwig)
include(GrPython)

########################################################################
# Setup swig generation
########################################################################
# foreach(incdir ${GNURADIO_RUNTIME_INCLUDE_DIRS})
#     list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/gnuradio/swig)
# endforeach(incdir)
list(APPEND GR_SWIG_INCLUDE_DIRS "/usr/local/include/gnuradio/swig")
list(APPEND GR_SWIG_INCLUDE_DIRS "/usr/include/gnuradio/swig")

set(GR_SWIG_LIBRARIES nTSDR_Local)
set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/nTSDR_Local_swig_doc.i)
set(GR_SWIG_DOC_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../include)

GR_SWIG_MAKE(nTSDR_Local_swig nTSDR_Local_swig.i)

########################################################################
# Install the build swig module
########################################################################
GR_SWIG_INSTALL(TARGETS nTSDR_Local_swig DESTINATION ${GR_PYTHON_DIR}/nTSDR_Local)

########################################################################
# Install swig .i files for development
########################################################################
install(
    FILES
    nTSDR_Local_swig.i
    ${CMAKE_CURRENT_BINARY_DIR}/nTSDR_Local_swig_doc.i
    DESTINATION ${GR_INCLUDE_DIR}/nTSDR_Local/swig
)