# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:46:59 2019

@author: qchat
"""

import numpy as np
import time

import autolab
autolab.get_device('PCBRUNO')
#from autolab import scan as s

# # Instantiation and preconfiguration of a device
# dummy = autolab.get_device('myDummy')
# dummy.sleep(0.5)

# # Instantiation of a Scanner manager
# scanner = s.Scanner()
# scanner.verbose = True # to print some information during scan, optional

# #scanner.set_datapath('.\myfolder\') # Optional (saving in current folder if no custom path provided)
# scanner.set_name('sample_8A') # basename of the HDF5 data file

# # Configure parameters of the multidimensional scan (here : only 2D)
# scanner.add_parameter('amplitude',s.Parameter(dummy.amplitude, np.linspace(0,1,100)))
# scanner.add_parameter('option',s.Parameter(dummy.option,[0,1]))

# # Configure init recipe
# scanner.add_init_recipe_step('open shutters',s.Execute(dummy.something))
# scanner.add_init_recipe_step('phase_ini',s.Measure(dummy.phase))

# # Configure main recipe (executed for each unique set of parameter)
# scanner.add_recipe_step('amplitude_mes',s.Measure(dummy.amplitude))
# scanner.add_recipe_step('phase_mes',s.Measure(dummy.phase))

# # Configure end recipe
# scanner.add_end_recipe_step('close shutters',s.Execute(dummy.something))
# scanner.add_end_recipe_step('phase_end',s.Measure(dummy.phase))

# # Check the global structure of the scan before starting it
# scanner.show_configuration()

# # Start scan
# scanner.start()
# time.sleep(5)

# # Pause scan 
# scanner.pause()
# time.sleep(5)

# # Resume scan 
# scanner.resume()
# time.sleep(5)

# # Stop / interrupt scan
# scanner.stop()
