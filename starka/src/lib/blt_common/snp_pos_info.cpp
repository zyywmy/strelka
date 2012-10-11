// -*- mode: c++; indent-tabs-mode: nil; -*-
//
// Copyright (c) 2009-2012 Illumina, Inc.
//
// This software is covered by the "Illumina Genome Analyzer Software
// License Agreement" and the "Illumina Source Code License Agreement",
// and certain third party copyright/licenses, and any user of this
// source file is bound by the terms therein (see accompanying files
// Illumina_Genome_Analyzer_Software_License_Agreement.pdf and
// Illumina_Source_Code_License_Agreement.pdf and third party
// copyright/license notices).
//
//

/// \file

/// \author Chris Saunders
///

#include "blt_common/snp_pos_info.hh"

#include <iomanip>
#include <iostream>



std::ostream&
operator<<(std::ostream& os,
           const base_call& bc){
    const char strand(bc.is_fwd_strand ? 'F' : 'R');
    os << "base: " << id_to_base(bc.base_id)
       << " P(error) " << std::setw(14) << std::setprecision(8) << std::left << bc.error_prob()
       << " strand: " << strand
#ifdef BC_DEBUG
       << " read_pos: " << (bc.read_pos+1)
       << " read_size: " << bc.read_size
#endif
       << " is_call_filter: " << bc.is_call_filter
       << " is_tscf?: " << bc.is_tier_specific_call_filter;
    return os;
}



std::ostream&
operator<<(std::ostream& os,
           const snp_pos_info& pci){
    os << "ref: " << pci.ref_base;
    const unsigned bs(pci.calls.size());
    for(unsigned i(0);i<bs;++i) os << "\nt1: " << pci.calls[i];
    const unsigned bs2(pci.tier2_calls.size());
    for(unsigned i(0);i<bs2;++i) os << "\nt2: " << pci.tier2_calls[i];
    return os;
}



void
snp_pos_info::
print_known_counts(std::ostream& os,
                   const int min_qscore) const {

    unsigned base_count[N_BASE];
    get_known_counts(base_count,min_qscore);

    for(unsigned b(0);b<N_BASE;++b) {
        os << '\t' << base_count[b];
    }
}



void
snp_pos_info::
print_known_qscore(std::ostream& os,
                   const int min_qscore) const {

    double qscore_tot[N_BASE];
    for(unsigned i(0);i<N_BASE;++i) qscore_tot[i] = 0;
    unsigned qscore_count[N_BASE];
    for(unsigned i(0);i<N_BASE;++i) qscore_count[i] = 0;
    
    const unsigned n_calls(calls.size());
    for(unsigned i(0);i<n_calls;++i){
        if(calls[i].base_id==BASE_ID::ANY) continue;
        if(calls[i].get_qscore()<min_qscore) continue;
        qscore_tot[calls[i].base_id] += calls[i].get_qscore();
        qscore_count[calls[i].base_id]++;
    }

    os << std::setprecision(2) << std::fixed;
    for(unsigned b(0);b<N_BASE;++b) {
        if(qscore_count[b]) {
            os << '\t' << qscore_tot[b]/qscore_count[b];
        } else {
            os << "\tNA";
        }
    }
    os.unsetf(std::ios::fixed);
}
