## SHALLOW WATER MODEL
"""
Copyright (C) 2017,  Milan Kloewer (milan.kloewer@physics.ox.ac.uk, milank.de)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

A documentation is available at
http://www.github.com/milankl/swm/docu

## HOW TO INSTALL

(i)  This shallow water model requires the modules that are loaded in this script.
(ii) For the parallel matrix-vector multiplication from parallel_sparsetools, go to that
     folder and do:

        > python setup.py install

    Otherwise uncomment the line 'import _parallel_sparsetools' in this script and

        os.environ['OMP_NUM_THREADS'] = str(1)
        sparse.csr_matrix._mul_vector = _mul_vector

    in swm_param.py. parallel_sparsetools might yield a speed-up of up to 2.5x for up to 4 cores
    on some machines.
"""

from __future__ import print_function       # tested with python 3.6 and 2.7.12

# path
import os
path = os.getcwd() + '/'

# import modules
import numpy as np                          # version 1.11.3-py36
from scipy import sparse                    # version 0.19-py36
import time as tictoc
from netCDF4 import Dataset                 # version 1.2.4-py36, hdf5 version 1.8.17-py36, hdf4 version 4.2.12-py36
import glob
import zipfile
import _parallel_sparsetools                # uncomment if not available

## import all functions
exec(open(path+'swm_param.py').read())
exec(open(path+'swm_operators.py').read())
exec(open(path+'swm_rhs.py').read())
exec(open(path+'swm_integration.py').read())
exec(open(path+'swm_output.py').read())

## set all parameters and initial conditions, and run model
u,v,eta = set_param()
u,v,eta = time_integration(u,v,eta)
