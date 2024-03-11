/* -*- c++ -*- */

#define NTSDR_LOCAL_API

%include "gnuradio.i"			// the common stuff
%include "feval.i"

//load generated python docstrings
%include "nTSDR_Local_swig_doc.i"

%{
// #include "vector_sink_cn.h"
%}

%include "nTSDR_Local/vector_sink_cn.h"
GR_SWIG_BLOCK_MAGIC2(nTSDR_Local, vector_sink_cn);
