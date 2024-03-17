# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 00:15:25 2020

@author: hunt
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm1
import xarray as xr
import datetime
from datetime import timedelta

# Count the time though the script
now = datetime.datetime.now()
file_path = r'C:\Users\Fernando\Desktop\Modelo\finalmente\2.1 Timeclustering (12ts - 2s)'
# Download the hourly data from the 11 regions in one file. 
data = pd.read_excel(file_path + '//Fontes alternativas - caso baseline_teste.xlsx')
dt = data.values

# region => 0 = Norte, 1 = Nordeste, 2 = Sudeste, 3 = Sul
region = 0
regions = ['Norte','Nordeste','Sudeste','Sul']
        
# Cicle to create the time slices for all regions, working one by one as shown above. 
while region < 4:
        
    # Hourly salor, wind, hydro and demand data.
    solar = dt[:,1+5*region]
    wind = dt[:,2+5*region]
    hydro = dt[:,4+5*region]
    demand = dt[:,3+5*region]
    demand_MW = dt[:,5+5*region]
        
    # Yearly hourly load curve
    solar_load_curve_annual = np.sort(solar, axis=None)[::-1]
    wind_load_curve_annual = np.sort(wind, axis=None)[::-1]
    demand_load_curve_annual = np.sort(demand, axis=None)[::-1]
    hydro_load_curve_annual = np.sort(hydro, axis=None)[::-1]
    
    # Seasonal yearly load curve 
    solar_load_curve_Wi = np.sort(solar[0:4380], axis=None)[::-1]
    wind_load_curve_Wi = np.sort(wind[0:4380], axis=None)[::-1]
    hydro_load_curve_Wi = np.sort(hydro[0:4380], axis=None)[::-1]    
    demand_load_curve_Wi = np.sort(demand[0:4380], axis=None)[::-1]
    
    solar_load_curve_Su = np.sort(solar[4380:8760], axis=None)[::-1]
    wind_load_curve_Su = np.sort(wind[4380:8760], axis=None)[::-1]
    hydro_load_curve_Su = np.sort(hydro[4380:8760], axis=None)[::-1]
    demand_load_curve_Su = np.sort(demand[4380:8760], axis=None)[::-1]
    
    # Reducing the hour resolution to 4 hourly resolution.
    solar_4h = np.zeros(shape=(2190))
    wind_4h = np.zeros(shape=(2190))
    hydro_4h = np.zeros(shape=(2190))
    demand_4h = np.zeros(shape=(2190))
    
    # Adjust the starting day of the series to midnight. 
    x = 0
    while x < 8760:          
        solar_4h[int(x/4)] = solar_4h[int(x/4)] + solar[x]/4
        wind_4h[int(x/4)] = wind_4h[int(x/4)] + wind[x]/4 
        hydro_4h[int(x/4)] = hydro_4h[int(x/4)] + hydro[x]/4        
        demand_4h[int(x/4)] = demand_4h[int(x/4)] + demand[x]/4 
        x = x + 1
        
        # NEW METHOD: Pick the most representative day in the season, then pick a scrambles day to better represent the season and the week. 
        # How to do it: First pick the best representative day in the season. Then look for the other times slices in the week. 
    
    # Calculating separetely Winter, Spring, Summer and Autumn. 
    
    # For each season,  there are 547.5 comparisonas required. 
    # For each comparison, the 2190 days will be compared with the 2 days of the representative week. 
    
    #(mininum sum non 0,w,d1,h1,h2,h3,h4,)
   
    w_minimum = [10000000000,0,0]
    su_minimum = [10000000000,0,0]
   
    solar_results_seasonal = np.zeros(shape=(12))
    wind_results_seasonal = np.zeros(shape=(12))
    hydro_results_seasonal = np.zeros(shape=(12))
    demand_results_seasonal = np.zeros(shape=(12))
        
    solar_results_sorted_seasonal = np.zeros(shape=(12))
    wind_results_sorted_seasonal = np.zeros(shape=(12))
    hydro_results_sorted_seasonal = np.zeros(shape=(12))
    demand_results_sorted_seasonal = np.zeros(shape=(12))
        
    w = 0
    x1 = 0
    while w < 13*2:
        #This is the equation that balances the load curve and the clustered values, thus it should vary between - and + numbers. And the number closest to 0 should be selected. 
        x2 = 0
        s_w_4_sorted1  = solar_4h[w*42:w*42+42]
        s_su_4_sorted1 = solar_4h[547+548+w*42:547+548+w*42+42] 
        
        w_w_4_sorted1  = wind_4h[w*42:w*42+42]
        w_su_4_sorted1 = wind_4h[547+548+w*42:547+548+w*42+42]
        
        h_w_4_sorted1  = hydro_4h[w*42:w*42+42]
        h_su_4_sorted1 = hydro_4h[547+548+w*42:547+548+w*42+42]
            
        d_w_4_sorted1  = demand_4h[w*42:w*42+42]
        d_su_4_sorted1 = demand_4h[547+548+w*42:547+548+w*42+42]  
        
        d1 = 0
        while d1 < 7:                          
            s_w_4_sorted  = np.sort(s_w_4_sorted1[0+d1*6:6+d1*6])
            s_su_4_sorted = np.sort(s_su_4_sorted1[0+d1*6:6+d1*6])
                
            w_w_4_sorted  = np.sort(w_w_4_sorted1[0+d1*6:6+d1*6])
            w_su_4_sorted = np.sort(w_su_4_sorted1[0+d1*6:6+d1*6])
        
            h_w_4_sorted  = np.sort(h_w_4_sorted1[0+d1*6:6+d1*6])
            h_su_4_sorted = np.sort(h_su_4_sorted1[0+d1*6:6+d1*6])
                
            d_w_4_sorted  = np.sort(d_w_4_sorted1[0+d1*6:6+d1*6])
            d_su_4_sorted = np.sort(d_su_4_sorted1[0+d1*6:6+d1*6])
                                
            x2 = 0
            sum1 = 0
            sum3 = 0
            while x2 < 2190 + 2190:
                sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/365/2)])**2) #Inverno         
                sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/365/2)])**2) #Verao   
                
                sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/365/2)])**2)         
                sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/365/2)])**2)          
        
                if region == 1:
                    sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/365/2)])**2)     
                    sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/365/2)])**2)
                else:
                    sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/365/2)])**2)/3     
                    sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/365/2)])**2)/3 
                        
                sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/365/2)])**2)           
                sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/365/2)])**2)            
                x2 = x2 + 1
                                
            if sum1 != 0 and sum1 < w_minimum[0]:
                w_minimum = [sum1,w,d1]
                solar_results_seasonal[0:6] = s_w_4_sorted1[0+d1*6:6+d1*6]
                wind_results_seasonal[0:6] = w_w_4_sorted1[0+d1*6:6+d1*6]
                hydro_results_seasonal[0:6] = h_w_4_sorted1[0+d1*6:6+d1*6]
                demand_results_seasonal[0:6] = d_w_4_sorted1[0+d1*6:6+d1*6]
                solar_results_sorted_seasonal[0:6] = s_w_4_sorted
                wind_results_sorted_seasonal[0:6] = w_w_4_sorted
                hydro_results_sorted_seasonal[0:6] = h_w_4_sorted
                demand_results_sorted_seasonal[0:6] = d_w_4_sorted                        
                                                                    
            if sum3 != 0 and sum3 < su_minimum[0]:
                su_minimum = [sum3,w,d1]
                solar_results_seasonal[6:12] = s_su_4_sorted1[0+d1*6:6+d1*6]
                wind_results_seasonal[6:12] = w_su_4_sorted1[0+d1*6:6+d1*6]
                hydro_results_seasonal[6:12] = h_su_4_sorted1[0+d1*6:6+d1*6]
                demand_results_seasonal[6:12] = d_su_4_sorted1[0+d1*6:6+d1*6]
                solar_results_sorted_seasonal[6:12] = s_su_4_sorted
                wind_results_sorted_seasonal[6:12] = w_su_4_sorted
                hydro_results_sorted_seasonal[6:12] = h_su_4_sorted
                demand_results_sorted_seasonal[6:12] = d_su_4_sorted 
                                    
            d1 = d1 + 1
            print('r ' + regions[region] + ' - w '+ str(w) + ' - d '+ str(d1))
        w = w + 1
        
    solar_load_curve_seasonal =  np.zeros(shape=(8760))
    wind_load_curve_seasonal =  np.zeros(shape=(8760))
    hydro_load_curve_seasonal =  np.zeros(shape=(8760))
    demand_load_curve_seasonal =  np.zeros(shape=(8760))
        
    solar_load_curve_seasonal[0:4380] = solar_load_curve_Wi
    solar_load_curve_seasonal[4380:8760] = solar_load_curve_Su
    wind_load_curve_seasonal[0:4380] = wind_load_curve_Wi
    wind_load_curve_seasonal[4380:8760] = wind_load_curve_Su
    hydro_load_curve_seasonal[0:4380] = hydro_load_curve_Wi
    hydro_load_curve_seasonal[4380:8760] = hydro_load_curve_Su
    demand_load_curve_seasonal[0:4380] = demand_load_curve_Wi
    demand_load_curve_seasonal[4380:8760] = demand_load_curve_Su
    
    #solar_results_annual = np.sort(solar_results_seasonal, axis=None)[::-1]
    #wind_results_annual = np.sort(wind_results_seasonal, axis=None)[::-1]
    #hydro_results_annual = np.sort(hydro_results_seasonal, axis=None)[::-1]
    #demand_results_annual = np.sort(demand_results_seasonal, axis=None)[::-1]
        
    #solar_results_sorted_annual = np.sort(solar_results_sorted_seasonal, axis=None)[::-1]
    #wind_results_sorted_annual = np.sort(wind_results_sorted_seasonal, axis=None)[::-1]
    #hydro_results_sorted_annual = np.sort(hydro_results_sorted_seasonal, axis=None)[::-1]
    #demand_results_sorted_annual = np.sort(demand_results_sorted_seasonal, axis=None)[::-1]
        
    solar_and_wind_seasonal = np.vstack((solar_results_seasonal,wind_results_seasonal,hydro_results_seasonal,demand_results_seasonal))
    solar_and_wind_sorter_seasonal = np.vstack((solar_results_sorted_seasonal,wind_results_sorted_seasonal,hydro_results_sorted_seasonal,demand_results_sorted_seasonal)) 
    solar_and_wind_duration_curve_seasonal = np.vstack((solar_load_curve_seasonal,wind_load_curve_seasonal,hydro_load_curve_seasonal,demand_load_curve_seasonal))
    
    #solar_and_wind_annual = np.vstack((solar_and_wind_annual,solar_results_annual,wind_results_annual,hydro_results_annual,demand_results_annual))
    #solar_and_wind_sorter_annual = np.vstack((solar_and_wind_sorter_annual,solar_results_sorted_annual,wind_results_sorted_annual,hydro_results_sorted_annual,demand_results_sorted_annual)) 
    #solar_and_wind_duration_curve_annual = np.vstack((solar_and_wind_duration_curve_annual,solar_load_curve_annual,wind_load_curve_annual,hydro_load_curve_annual,demand_load_curve_annual))
        
    # Save the time slices        
    panda = pd.DataFrame(solar_and_wind_seasonal.T)
    panda.to_excel(file_path + '//' + regions[region] +'Results.xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_seasonal.T)
    panda.to_excel(file_path + '//' + regions[region] +'Results Sorted.xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_seasonal.T)
    panda.to_excel(file_path + '//' + regions[region] +'Results Duration Curve.xlsx')

    #panda = pd.DataFrame(solar_and_wind_annual.T)
    #panda.to_excel(path+'Results/12 Time Slices (Annual).xlsx')

    #panda = pd.DataFrame(solar_and_wind_sorter_annual.T)
    #panda.to_excel(path+'Results/12 Time Slices Sorted (Annual).xlsx')

    #panda = pd.DataFrame(solar_and_wind_duration_curve_annual.T)
    #panda.to_excel(path+'Results/Duration Curve (Annual).xlsx')
  
    region = region + 1 
#%%

