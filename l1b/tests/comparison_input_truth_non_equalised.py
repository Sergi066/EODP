from pathlib import Path
import numpy as np
# import xarray as xr
import matplotlib.pyplot as plt

truth_dir = Path()
eq_dir = Path()
non_eq_dir = Path()
"""
# explanation of the plot: 
    The blue line is the "radiation" that arrives to the satellite. What it is being plotted is a cross section of the
    image (4 bands are being recorded: 0-green, 1-red, 2-NIR, 3-NIR). Energy received in W*m-2*sr-1*cm-1 (sr are
    steradians). The red line is the response of our system. How our sistem receives the radiation. The black line is
    the response of our system after calibration. Explain what calibration is: the exercise of understanding the
    behaviour of our system in order to correct it so that it reflects the truth.
    
    If the system is not characterised via calibration, the system is blind as it wont be able to catch errors in
    measurements.
"""