find_package(PkgConfig)

# INCLUDE(FindPkgConfig)
# PKG_CHECK_MODULES(PC_NTSDR_LOCAL nTSDR_Local) #gnuradio-nTSDR_Local

FIND_PATH(
    NTSDR_LOCAL_INCLUDE_DIRS
    NAMES nTSDR_Local/api.h
    HINTS $ENV{NTSDR_LOCAL_DIR}/include
        ${PC_NTSDR_LOCAL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    NTSDR_LOCAL_LIBRARIES
    NAMES nTSDR_Local
    HINTS $ENV{NTSDR_LOCAL_DIR}/lib
        ${PC_NTSDR_LOCAL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/nTSDR_LocalTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NTSDR_LOCAL DEFAULT_MSG NTSDR_LOCAL_LIBRARIES NTSDR_LOCAL_INCLUDE_DIRS)
MARK_AS_ADVANCED(NTSDR_LOCAL_LIBRARIES NTSDR_LOCAL_INCLUDE_DIRS)
