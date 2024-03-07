/* -*- c++ -*- */
/* 

 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */


#ifndef INCLUDED_NTSDR_LOCAL_VECTOR_SINK_CN_H
#define INCLUDED_NTSDR_LOCAL_VECTOR_SINK_CN_H

#include "api.h"
#include <gnuradio/sync_block.h>
#include <gnuradio/feval.h>

namespace gr {
  namespace nTSDR_Local {

    /*!
     * \brief gr_complex sink that writes to a vector
     * \ingroup nTSDR_Local
     */
    class NTSDR_LOCAL_API vector_sink_cn : virtual public sync_block
    {
    public:
      // gr::blocks::vector_sink_cn::sptr
      typedef std::shared_ptr<vector_sink_cn> sptr;

      static sptr make(int vlen = 1, bool finite=false, int nsamp=0, int num_channels=1, feval * fullness_norifier=NULL);

      virtual void reset() = 0;
      virtual std::vector< std::vector<gr_complex> > data() const = 0;
      virtual std::vector<tag_t> tags() const = 0;
    };

  } // namespace nTSDR_Local
} // namespace gr

#endif /* INCLUDED_NTSDR_LOCAL_VECTOR_SINK_CN_H */


