
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism
from nc_compare import compare_folders
import traceback

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\EODP\EODP\auxiliary'
indir = r"C:\EODP\EODP_TER_2021\EODP-TS-ISM\input\gradient_alt100_act150" # small scene
outdir = r"C:\EODP\EODP_TER_2021\EODP-TS-ISM\my_outputs(sergio)"
referencedir = r"C:\EODP\EODP_TER_2021\EODP-TS-ISM\output"
# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
try:
    myIsm.processModule()
except Exception:
    traceback.print_exc()
compare_folders(outdir, referencedir)
