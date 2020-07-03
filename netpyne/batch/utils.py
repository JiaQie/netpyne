"""
batch/utils.py 

Helper functions to set up and run batch simulations
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import numpy as np

# -------------------------------------------------------------------------------
# function to create a folder if it does not exist
# -------------------------------------------------------------------------------
def createFolder(folder):
    import os
                
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except OSError:
            print(' Could not create %s' %(folder))


# -------------------------------------------------------------------------------
# function to define template for bash submission
# -------------------------------------------------------------------------------

def bashTemplate(template):
    """
    return the bash commands required by template for batch simulation
    """
    
    if template=='mpi_direct':
        return """#!/bin/bash 
%s
cd %s
%s
        """
    elif template=='hpc_slurm':
        return """#!/bin/bash 
#SBATCH --job-name=%s
#SBATCH -A %s
#SBATCH -t %s
#SBATCH --nodes=%d
#SBATCH --ntasks-per-node=%d
#SBATCH -o %s.run
#SBATCH -e %s.err
#SBATCH --mail-user=%s
#SBATCH --mail-type=end
%s
%s
source ~/.bashrc
cd %s
%s
wait
        """
    elif template=='hpc_torque':
        return """#!/bin/bash 
#PBS -N %s
#PBS -l walltime=%s
#PBS -q %s
#PBS -l %s
#PBS -o %s.run
#PBS -e %s.err
%s
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
%s
        """

def cp(obj, verbose=True, die=True):
    ''' Shortcut to perform a shallow copy operation 
    from https://github.com/sciris/sciris/blob/develop/sciris/sc_utils.py'''
    try:
        output = copy.copy(obj)
    except Exception as E:
        output = obj
        errormsg = 'Warning: could not perform shallow copy, returning original object: %s' % str(E)
        if die: raise Exception(errormsg)
        else:   print(errormsg)
    return output

def dcp(obj, verbose=True, die=False):
    ''' Shortcut to perform a deep copy operation 
        from https://github.com/sciris/sciris/blob/develop/sciris/sc_utils.py '''
    import copy

    try:
        output = copy.deepcopy(obj)
    except Exception as E:
        output = cp(obj)
        errormsg = 'Warning: could not perform deep copy, performing shallow instead: %s' % str(E)
        if die: raise Exception(errormsg)
        else:   print(errormsg)
    return output



def sigfig(X, sigfigs=5, SI=False, sep=False, keepints=False):
    '''
    Return a string representation of variable x with sigfigs number of significant figures --
    copied from asd.py.
    If SI=True,  then will return e.g. 32433 as 32.433K
    If sep=True, then will return e.g. 32433 as 32,433

    from https://github.com/sciris/sciris/blob/develop/sciris/sc_utils.py
    '''
    output = []

    try:
        n=len(X)
        islist = True
    except:
        X = [X]
        n = 1
        islist = False
    for i in range(n):
        x = X[i]

        suffix = ''
        formats = [(1e18,'e18'), (1e15,'e15'), (1e12,'t'), (1e9,'b'), (1e6,'m'), (1e3,'k')]
        if SI:
            for val,suff in formats:
                if abs(x)>=val:
                    x = x/val
                    suffix = suff
                    break # Find at most one match

        try:
            if x==0:
                output.append('0')
            elif sigfigs is None:
                output.append(flexstr(x)+suffix)
            elif x>(10**sigfigs) and not SI and keepints: # e.g. x = 23432.23, sigfigs=3, output is 23432
                roundnumber = int(round(x))
                if sep: string = format(roundnumber, ',')
                else:   string = '%0.0f' % x
                output.append(string)
            else:
                magnitude = np.floor(np.log10(abs(x)))
                factor = 10**(sigfigs-magnitude-1)
                x = round(x*factor)/float(factor)
                digits = int(abs(magnitude) + max(0, sigfigs - max(0,magnitude) - 1) + 1 + (x<0) + (abs(x)<1)) # one because, one for decimal, one for minus
                decimals = int(max(0,-magnitude+sigfigs-1))
                strformat = '%' + '%i.%i' % (digits, decimals)  + 'f'
                string = strformat % x
                if sep: # To insert separators in the right place, have to convert back to a number
                    if decimals>0:  roundnumber = float(string)
                    else:           roundnumber = int(string)
                    string = format(roundnumber, ',') # Allow comma separator
                string += suffix
                output.append(string)
        except:
            output.append(flexstr(x))
    if islist:
        return tuple(output)
    else:
        return output[0]