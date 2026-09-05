import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq

class AerodynamicDatabase: 
    def __init__(self, cl_file ="Cl_lookup_table.csv", cd_file ="Cd_lookup_table.csv"):
        
    # load the data
        df_cl = pd.read_csv(cl_file, index_col='delta')
        df_cd = pd.read_csv(cd_file, index_col='delta')

    # define 1D grid arrays for the axes of RegularGridInterpolator
        self.deltas = df_cl.index.values.astype(float)
        self.alphas = np.array([float(col.replace("alpha_", "").replace("deg", "")) for col in df_cl.columns])

        self.delta_max = float(self.deltas.max()) # -0.10
        self.delta_min = float(self.deltas.min()) # +0.10

    # interpolate lookup table values -- extrapolate if value lands outside the grid boundaries
        self.cl_interp = RegularGridInterpolator(
            (self.deltas, self.alphas),
            df_cl.values,
            bounds_error=False,
            fill_value=None
        )

        self.cd_interp = RegularGridInterpolator(
            (self.deltas, self.alphas),
            df_cd.values,
            bounds_error=False,
            fill_value=None
        )

    def get_cd(self, delta, alpha):
            cd_value = self.cd_interp((delta, alpha))
            
            return float(cd_value)

# calculate the maximum and minimum lift the morphing airfoil can generate at local angle of attack
    def solve_delta(self, cl_target, alpha_eff):
        cl_min = float(self.cl_interp((self.delta_min, alpha_eff)))
        cl_max = float(self.cl_interp((self.delta_max, alpha_eff)))

    # if a lift is requested that is PHYSICALLY impossible to reach at the local angle of attack:
        if cl_target <= cl_min: 
            return self.delta_min
        
        if cl_target >= cl_max: 
            return self.delta_max
        
    # define a function for the root-finding algorithm; it must equal zero (d = deflection)
        def function(d):
            return float(self.cl_interp((d, alpha_eff))) - cl_target

    # solve for the delta value 
        delta_solved = brentq(function, self.delta_min, self.delta_max)

        return float(delta_solved)

