"""
=============================================================
Compute PDC spectrum source space connectivity between labels
=============================================================

The connectivity is computed between 4 labels across the spectrum
between 5 and 40 Hz.
"""

# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#          Martin Billinger <martin.billinger@tugraz.at>
#
# License: BSD (3-clause)

import sys
import os

try:
    import mne
except ImportError:
    sys.path.insert(1, os.path.expanduser('~/git-working/mne-python'))
    import mne

try:
    import scot
except ImportError:
    sys.path.insert(1, os.path.expanduser('~/git-working/SCoT'))
    import scot    

from mne.datasets import sample
from mne.fiff import Raw, pick_types
from mne.minimum_norm import apply_inverse_epochs, read_inverse_operator
from mne.connectivity import spectral_connectivity

from scot.backend_sklearn import VAR
from scot.connectivity import connectivity
import scot.connectivity_statistics as scs
import scot.plotting as splt
import numpy as np

import math
A = np.zeros((3, 5, 5))
A[0, 0, 0] = 0.95 * math.sqrt(2)
A[1, 0, 0] = -0.9025
A[1, 1, 0] = 0.5
A[2, 2, 0] = -0.4
A[1, 3, 0] = -0.5
A[0, 3, 3] = 0.25 * math.sqrt(2)
A[0, 3, 4] = 0.25 * math.sqrt(2)
A[0, 4, 3] = -0.25 * math.sqrt(2)
A[0, 4, 4] = 0.25 * math.sqrt(2)

# simulate processes
n = 10 ** 4
# sigma = np.array([0.0001, 1, 1, 1, 1])
# sigma = np.array([0.01, 1, 1, 1, 1])
sigma = np.array([1., 1., 1., 1., 1.])
import test_scot
Y = test_scot.mvar_generate(A, n, sigma)
# rearrange data to fit scot's format
label_ts = []
for i in xrange(100):
    label_ts.append(Y[:,i*100:(i+1)*100])
    
label_ts = np.array(label_ts).transpose(2, 1, 0)

# remove mean over epochs (evoked response) to improve stationarity
label_ts -= label_ts.mean(axis=2, keepdims=True)

# create VAR model of order 9
mvar = VAR(3)

# generate connectivity surrogates under the null-hypothesis of no connectivity
c_surrogates = scs.surrogate_connectivity('PDC', label_ts, mvar)
c0 = np.percentile(c_surrogates, 95, axis=0)
fig = splt.plot_connectivity_spectrum([c0], fs=100, freq_range=[0, 40], diagonal=-1)

# estimate and plot connectivity
mvar.fit(label_ts)
con = connectivity('PDC', mvar.coef, mvar.rescov)
splt.plot_connectivity_spectrum(con, fs=100, freq_range=[0, 40], diagonal=-1, fig=fig)

splt.show_plots()