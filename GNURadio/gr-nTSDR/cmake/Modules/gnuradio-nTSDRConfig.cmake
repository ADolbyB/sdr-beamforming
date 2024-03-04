find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_NTSDR gnuradio-nTSDR)

FIND_PATH(
    GR_NTSDR_INCLUDE_DIRS
    NAMES gnuradio/nTSDR/api.h
    HINTS $ENV{NTSDR_DIR}/include
        ${PC_NTSDR_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_NTSDR_LIBRARIES
    NAMES gnuradio-nTSDR
    HINTS $ENV{NTSDR_DIR}/lib
        ${PC_NTSDR_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-nTSDRTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_NTSDR DEFAULT_MSG GR_NTSDR_LIBRARIES GR_NTSDR_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_NTSDR_LIBRARIES GR_NTSDR_INCLUDE_DIRS)
