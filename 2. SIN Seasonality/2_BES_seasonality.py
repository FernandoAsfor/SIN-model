
# -*- coding: utf-8 -*-
"""
Created on Thrus Jan 19 10:55 2023

@author: Natalia & Fernando
"""

import pandas as pd
import ixmp as ix
import message_ix
import itertools
from message_ix.utils import make_df
from matplotlib import pyplot as plt

# Loading modelling platform
mp = ix.Platform("default", jvmargs=["-Xmx8G"])

# %% Specifying model/scenario to be loaded from the database
model = 'SIN Brasil expandido'
scenario='base'
nodes = ['South', 'North', 'Northeast', 'Southeast']
base = message_ix.Scenario(mp, model, scenario= scenario)

# Cloning a scenario for adding time steps
scen = base.clone(model,'seasonal',keep_solution=False)
scen.check_out()

# Adding sub-annual time steps
time_steps_sea = ['winter','summer']

time_steps_win = ['winter_1','winter_2','winter_3','winter_4','winter_5','winter_6']

time_steps_sum = ['summer_1','summer_2','summer_3','summer_4','summer_5','summer_6']

time_steps = time_steps_win + time_steps_sum

time_steps_all = time_steps + time_steps_sea

scen.add_set('time', time_steps_all)


# We can see the elements of the set
scen.set('time')

# Defining a new temporal level

time_level_1 = ['season']
time_level_2 = ['subannual']
time_level_3 = ['winter_day']
time_level_4 = ['summer_day']

time_level = time_level_1 + time_level_2 + time_level_3 + time_level_4

scen.add_set('lvl_temporal', time_level)

# Adding temporal hierarchy
for t in time_steps_sea:
    scen.add_set('map_temporal_hierarchy', ['season', t, 'year'])

#for t in time_steps:
#    scen.add_set('map_temporal_hierarchy', ['subannual', t, 'year'])

for t in time_steps_win:
    scen.add_set('map_temporal_hierarchy', ['subannual', t, 'winter'])

for t in time_steps_sum:
    scen.add_set('map_temporal_hierarchy', ['subannual', t, 'summer'])

for t in time_steps_win:
    scen.add_set('map_temporal_hierarchy', ['winter_day', t, 'winter'])

for t in time_steps_sum:
    scen.add_set('map_temporal_hierarchy', ['summer_day', t, 'summer'])
    
# We can see the content of the set
scen.set('map_temporal_hierarchy')

# All parameters with at least one sub-annual time index
parameters = [p for p in scen.par_list() if 'time' in scen.idx_sets(p)]

# Those parameters with "time" index that are not empty in our model
[p for p in parameters if not scen.par(p).empty]

# Adding duration time
for t in time_steps:
    scen.add_par('duration_time', [t], 1/12, '-')

for t in time_steps_sea:
    scen.add_par('duration_time', [t], 1/2, '-')
    
# A function for adding sub-annual data to a parameter
def yearly_to_season(scen, parameter, data, filters=None):
    if filters:
        old = scen.par(parameter, filters)
    else:
        old = scen.par(parameter)
    scen.remove_par(parameter, old)
    
    # Finding "time" related indexes
    time_idx = [x for x in scen.idx_names(parameter) if 'time' in x]
    for h in data.keys():
        new = old.copy()
        for time in time_idx:
            new[time] = h
        new['value'] = data[h] * old['value']
        scen.add_par(parameter, new)

# Before modifying, let's look at "demand" in baseline
scen.par('demand')

# Modifying demand for each season
demand_data = {'winter_1':1/12,'winter_2':1/12,'winter_3':1/12,'winter_4':1/12,'winter_5':1/12,'winter_6':1/12,
               'summer_1':1/12,'summer_2':1/12,'summer_3':1/12,'summer_4':1/12,'summer_5':1/12,'summer_6':1/12}
yearly_to_season(scen, 'demand', demand_data)

# Modifying input and output parameters for each season
# output
fixed_data = {'winter_1':1,'winter_2':1,'winter_3':1,'winter_4':1,'winter_5':1,'winter_6':1,
              'summer_1':1,'summer_2':1,'summer_3':1,'summer_4':1,'summer_5':1,'summer_6':1}
yearly_to_season(scen, 'output', fixed_data)

# input
yearly_to_season(scen, 'input', fixed_data)

# Modifying growth rates for each season
#yearly_to_season(scen, 'growth_activity_lo', fixed_data)
#yearly_to_season(scen, 'growth_activity_up', fixed_data)
#yearly_to_season(scen, 'growth_new_capacity_lo', fixed_data)
#yearly_to_season(scen, 'growth_new_capacity_up', fixed_data)

yearly_to_season(scen, 'bound_activity_up', demand_data)

# Modifying capacity factor

# Converting yearly capacity factor to seasonal
yearly_to_season(scen, 'capacity_factor', fixed_data)
# the capacity factor data will be incorporated to the model throught manual insertion on the excel file generated

# Modifying historical activity 
yearly_to_season(scen, 'historical_activity', demand_data)

# Modifying variable cost
yearly_to_season(scen, 'var_cost', fixed_data)


scen.commit(comment='introducing seasonality')
scen.solve()
scen.set_as_default()



scen.var('OBJ')['lvl']
scen.to_excel('SIN expandido season.xlsx')
scen.version
