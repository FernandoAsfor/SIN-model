# -*- coding: utf-8 -*-
"""
Created on Thrus Jan 19 09:13 2023

@authors: Natalia & Fernando
"""
# load required packages 
#import itertools
import pandas as pd

import matplotlib.pyplot as plt
plt.style.use('ggplot')

import ixmp
import message_ix

from message_ix.utils import make_df

mp = ixmp.Platform("default", jvmargs=["-Xmx8G"])

# %% start
model = "SIN Brasil expandido"
scen = "base"
scenario = message_ix.Scenario(mp, model, scen, version = 'new')

history = [2020]
horizon = [2030, 2040, 2050]
scenario.add_horizon(
    year= history + horizon,
    firstmodelyear=horizon[0]
)

country = 'Brazil'
scenario.add_spatial_sets({'country': country})

# visualizing the set
scenario.set('map_spatial_hierarchy')

nodes = ['South', 'North', 'Northeast', 'Southeast']
space_level = 'province'
scenario.add_set('lvl_spatial', space_level)
for node in nodes:
    scenario.add_set('node', node)
    scenario.add_set('map_spatial_hierarchy', [space_level, node, country])

scenario.set('map_spatial_hierarchy')

scenario.add_set("commodity", ["electricity", "water_1", "water_2", "water_3", "water_4", "water_5", "water_6",
                              "water_7", "water_8", "water_9", "water_10", "water_11", "water_12"])#ion commodities are storage especifications for batteries
scenario.add_set("level", ["primary" , "secondary", "final"])
scenario.add_set('mode', ['n-to-ne', 'ne-to-n', 'n-to-se', 'se-to-n', 
                          'ne-to-se', 'se-to-ne', 'se-to-s', 's-to-se', 'M1','M2'])
scenario.set("mode")

scenario.add_par("interestrate", horizon, value=0.08, unit='-') #EPE

# centralized demand
elec_growth = pd.Series([1.31, 1.69, 2.11], 
                        index=pd.Index(horizon, name='Time'))

plants = [
    "bio_ppl",
    "gas_ppl",
    "gas_ppl_1",
    "gas_ppl_2",
    "gas_ppl_ccs",
    "gas_ppl_ccs_1",
    "gas_ppl_ccs_2",
    "coal_ppl",
    "nuc_ppl",
    "oil_ppl",
    "solar_pv_ppl"
]

north_hydro = ["hydro_4", "hydro_8", "hydro_9"]
northeast_hydro = ["hydro_3"]
southeast_hydro = ["hydro_1", "hydro_5", "hydro_6", "hydro_7", "hydro_10", "hydro_12"]
south_hydro = ["hydro_2", "hydro_11"]

north_pump = ["sphs_4", "sphs_8", "sphs_9"]
northeast_pump = ["sphs_3"]
southeast_pump = ["sphs_1", "sphs_6", "sphs_7", "sphs_10", "sphs_12"]
south_pump = ["sphs_2", "sphs_11"]

north_res = [ "river4", "river8", "river9"]
northeast_res = ["river3"]
southeast_res = ["river1", "river5", "river6", "river7", "river10", "river12" ]
south_res = ["river2", "river11"]

north_wat = [ "water_supply_4", "water_supply_8", "water_supply_9"]
northeast_wat = ["water_supply_3"]
southeast_wat = ["water_supply_1", "water_supply_5", "water_supply_6", "water_supply_7", "water_supply_10", "water_supply_12" ]
south_wat = ["water_supply_2", "water_supply_11"]

brazil_wind = ["wind_ppl"]
northeast_wind = ["wind_ppl_cos", "wind_ppl_int"]
south_wind = ["wind_ppl_rs"]
#wind_ppl_cos means wind_ppl on the coast of northeast of Brazil. To obtain it's parameters, it was considered data from RN and CE states.
#wind_ppl_int means wind_ppl on inlands of northeast of Brazil. To obtain it's parameters, it was considered data from BA and PI states.
#wind_ppl_rs means wind_ppl on Rio Grande do Sul state. To obtain it's parameters, it was considered data from RS state.

battery_n = ['batt_n']
battery_ne = ['batt_ne']
battery_se = ['batt_se']
battery_s = ['batt_s']

final_energy_techs = ["grid1", "grid2", "grid3", "grid4", "grid_n", "grid_ne", "grid_se", "grid_s"]

technologies = plants + north_hydro + northeast_hydro + southeast_hydro + south_hydro + north_pump + northeast_pump + southeast_pump + south_pump +north_res + northeast_res + southeast_res + south_res + northeast_wind + south_wind + brazil_wind + final_energy_techs + north_wat + northeast_wat + southeast_wat + south_wat + battery_n + battery_ne + battery_se + battery_s
scenario.add_set("technology", technologies)

# %% Adding electricity demand

demand_per_year = {
        'South': 11.67, # electricity demand GWa BEN year 2019
        'North': 5.57,
        'Northeast': 11.05,
        'Southeast': 39.55,
        }

#elec_demand = sum(demand_per_year.values())
#elec_growth = elec_demand * elec_growth
#elec_growth.plot(title='Demand')


# Loop over nodes
for node, dem in demand_per_year.items():
    demand_data = pd.DataFrame({
            'node': node,
            'commodity': 'electricity',
            'level': 'final',
            'year': horizon,
            'time': 'year',
            'value': dem * elec_growth, #retirada a multiplicação por demanda regional por esta ser incluída posteriormente. Caso se deseje voltar para o estágio anterior, é só colocar dem * na parte do value.
            'unit': 'GWa',
        })
    scenario.add_par("demand", demand_data)


year_df = scenario.vintage_and_active_years()
vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

[x for x in scenario.par_list() if 'mode' in scenario.idx_sets(x)]

# %% 1) North
lifetimes = {
    "hydro_4": 60, "hydro_8": 60, "hydro_9": 60, "sphs_4": 60, "sphs_8": 60, "sphs_9": 60,
    "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1":20, "gas_ppl_2":20, "wind_ppl": 20,  "coal_ppl": 25, "batt_n": 15, "gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20,
    "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "grid1": 25, "grid_n": 25,"river4":1000, "river8":1000, "river9":1000,
    "water_supply_4":1000, "water_supply_8":1000, "water_supply_9":1000,
}
# considering NREL COST utility scale for batteries
# Adding technical lifetime
base_technical_lifetime_n = {
    'node_loc': 'North',
    'year_vtg': horizon,
    'unit': 'y',
}

# Adding a new unit to the library
mp.add_unit('m^3/s')  

for tec, val in lifetimes.items():
    df_n = make_df(base_technical_lifetime_n, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_n)

# Adding input and output
base_input_n1 = {
    'node_loc': 'North',
    'node_origin': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-ne',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_n1 = {
    'node_loc': 'North',
    'node_dest': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-ne',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_n2 = {
    'node_loc': 'North',
    'node_origin': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-n',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_n2 = {
    'node_loc': 'North',
    'node_dest': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-n',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

#grids

grid_efficiency = 1/0.85
grid_out_n1 = make_df(base_output_n1, technology='grid1', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_n1)

grid_in_n1 = make_df(base_input_n1, technology='grid1', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_n1)

grid_out_n2 = make_df(base_output_n2, technology='grid1', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_n2)

grid_in_n2 = make_df(base_input_n2, technology='grid1', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_n2)

input_n = {
    'node_loc': 'North',
    'node_origin': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_n = {
    'node_loc': 'North',
    'node_dest': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# regional grid

grid_eff = 1/0.9
grid_out_n = make_df(output_n, technology='grid_n', commodity='electricity', 
                   level='final', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_n)

grid_in_n = make_df(input_n, technology='grid_n', commodity='electricity',
                  level='secondary', value=grid_eff, unit="GWa")
scenario.add_par('input', grid_in_n)

#primary to secondary for hydro_ppl

n_hydro_out = {"hydro_4": 1,
           "hydro_8": 1,
           "hydro_9": 1}

for h_plant, val in n_hydro_out.items():
    h_plant_out_n = make_df(output_n, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_n['year_act'] < h_plant_out_n['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n = h_plant_out_n.loc[condition] 

    scenario.add_par('output', h_plant_out_n)
    
n_hydro_out_2 =  {"hydro_4": 1558.6,
              "hydro_8": 1317.0,
              "hydro_9": 4898.5}
    
for h_plant, val in n_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_n_2 = make_df(output_n, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_n_2['year_act'] < h_plant_out_n_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n_2 = h_plant_out_n_2.loc[condition]
    
    scenario.add_par('output', h_plant_out_n_2)
    
n_hydro_in = {"hydro_4": 1558.6,
              "hydro_8": 1317.0,
              "hydro_9": 4898.5}
    
for h_plant, val in n_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_n = make_df(input_n, technology= h_plant, commodity= wat, 
                   level='primary', value= val, unit="m^3/s")

    # Removing extra years based on lifetime 
    condition = h_plant_in_n['year_act'] < h_plant_in_n['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_n = h_plant_in_n.loc[condition]
    scenario.add_par('input', h_plant_in_n)
    
for river in north_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_n = make_df(output_n, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/s")
    scenario.add_par('output', river_out_n)

#secondary to secondary for sphs_ppl

n_sphs_out = {"sphs_4": 1,
           "sphs_8": 1,
           "sphs_9": 1}

for h_plant, val in n_sphs_out.items():
    h_plant_out_n_3 = make_df(output_n, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_n_3['year_act'] < h_plant_out_n_3['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n_3 = h_plant_out_n_3.loc[condition] 

    scenario.add_par('output', h_plant_out_n_3)
    
n_sphs_out_2 =  {"sphs_4": 73.,
              "sphs_8": 86.,
              "sphs_9": 23.}
    
for h_plant, val in n_sphs_out_2.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_out_n_4 = make_df(output_n, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_n_4['year_act'] < h_plant_out_n_4['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n_4 = h_plant_out_n_4.loc[condition]
    
    scenario.add_par('output', h_plant_out_n_4)
    
n_sphs_in = {"sphs_4": 73.,
              "sphs_8": 86.,
              "sphs_9": 23.}
    
for h_plant, val in n_sphs_in.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_in_n_2 = make_df(input_n, technology= h_plant, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")

    # Removing extra years based on lifetime 
    condition = h_plant_in_n_2['year_act'] < h_plant_in_n_2['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_n_2 = h_plant_in_n_2.loc[condition]
    scenario.add_par('input', h_plant_in_n_2)
    
n_sphs_in_2 = {"sphs_4": 1.2,
             "sphs_8": 1.2,
             "sphs_9": 1.2}
        
for h_plant, val in n_sphs_in_2.items():
    h_plant_in_n_3 = make_df(input_n, technology= h_plant, commodity= 'electricity', 
                      level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_in_n_3['year_act'] < h_plant_in_n_3['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_n_3 = h_plant_in_n_3.loc[condition]
    scenario.add_par('input', h_plant_in_n_3)

# secondary to final to water_supply

n_water_out = {"water_supply_4": 1558.6,
              "water_supply_8": 1317.0,
              "water_supply_9": 4898.5}

for w_supply, val in n_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_n = make_df(output_n, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/s")
    scenario.add_par('output', w_supply_out_n)

n_water_in = {"water_supply_4": 1558.6,
              "water_supply_8": 1317.0,
              "water_supply_9": 4898.5}
    
for w_supply, val in n_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_n = make_df(input_n, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")

    scenario.add_par('input', w_supply_in_n)
    
#secondary to useful e_tecs

for tech in brazil_wind:
     tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")

     # Removing extra years based on lifetime 
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + lifetimes[tech] 
     tech_out_n = tech_out_n.loc[condition]
     
     scenario.add_par('output', tech_out_n)
     
for tech in plants:
     tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")

     # Removing extra years based on lifetime 
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + lifetimes[tech] 
     tech_out_n = tech_out_n.loc[condition] 
     scenario.add_par('output', tech_out_n)
     
#secondary to final for batteries

for tech in battery_n:
    tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                  level='secondary', value=1., unit="GWa")

    # Removing extra years based on lifetime 
    condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + lifetimes[tech] 
    tech_out_n = tech_out_n.loc[condition] 
    scenario.add_par('output', tech_out_n)
    
for tech in battery_n:
    tech_in_n = make_df(input_n, technology=tech, commodity='electricity', 
                  level='secondary', value=1.2, unit="GWa")
    # Removing extra years based on lifetime 
    condition = tech_in_n['year_act'] < tech_in_n['year_vtg'] + lifetimes[tech] 
    tech_in_n = tech_in_n.loc[condition] 
    scenario.add_par('input', tech_in_n)

base_capacity_factor_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_4": 0.9, #EPE
    "hydro_8": 0.9, #EPE
    "hydro_9": 0.9, #EPE
    "sphs_4": 0.7, #EPE
    "sphs_8": 0.7, #EPE
    "sphs_9": 0.7, #EPE
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "coal_ppl": 0.69,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75,
    "grid1": 0.8,
    "batt_n": 0.85,
    "grid_n": 0.8,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_n, technology=tec, value=val)
    # Removing extra years based on lifetime
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec]
    df = df.loc[condition]
    scenario.add_par('capacity_factor', df)
  
base_capacity_n = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'North',
    'unit': 'GWa',
}

#base capacity [GW] in 07/2019 according to CCEE historical operation for each subsystem [North, Northeast, SE/MW, South]
thermal_capacity = 3.87 
hydro_capacity= 22.12
transmission_capacity = 5.02
transmission_internal_capacity = 6.59
times = 10. 

base_cap = {
    "hydro_4": 9.6/times, 
    "hydro_8": 11.03/times, 
    "hydro_9": 1.2/times, 
    "sphs_4": 0./times, 
    "sphs_8": 0./times, 
    "sphs_9": 0./times, 
    "bio_ppl": thermal_capacity*0.111/times,  
    "gas_ppl": thermal_capacity*0.623/times,
    "gas_ppl_1": thermal_capacity*0./times,
    "gas_ppl_2": thermal_capacity*0./times,
    "gas_ppl_ccs": 0./times,
    "gas_ppl_ccs_1": 0./times,
    "gas_ppl_ccs_2": 0./times,
    "wind_ppl": 0.33/times, 
    "coal_ppl": thermal_capacity*0.093/times, 
    "nuc_ppl": 0./times, 
    "solar_pv_ppl": 0.05/times,
    "oil_ppl": thermal_capacity*0.173/times,
    "grid1": transmission_capacity/times,
    "batt_n": 0./times,
    "grid_n": transmission_internal_capacity/times,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_n, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?


# %% Adding costs

base_inv_cost_n = {
    'node_loc': 'North',
    'year_vtg': horizon,
    'unit': 'MMUSD/GWa',
}

# Adding a new unit to the library
mp.add_unit('MMUSD/GWa')    

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_4": 1352, #EPE mean value for UHE
    "hydro_8": 1352, #EPE mean value for UHE
    "hydro_9": 1352,#EPE mean value for UHE
    "sphs_4": 1500,#EPE
    "sphs_8": 1500,#EPE
    "sphs_9": 1500,#EPE
    "bio_ppl": 1200,#EPE 
    "gas_ppl": 900, #EPE mean value
    "gas_ppl_1": 1000, #EPE mean value
    "gas_ppl_2": 1000, #EPE mean value
    "gas_ppl_ccs": 1.8*900, #PNE value
    "gas_ppl_ccs_1": 1.8*1000, #PNE value
    "gas_ppl_ccs_2": 1.8*1000, #PNE value
    "wind_ppl": 1200,#EPE mean value
    "coal_ppl": 2500, #EPE
    "nuc_ppl": 5000,#EPE
    "solar_pv_ppl":1100, #min value in EPE, max value is 1350
    "oil_ppl": 1100,
    'grid1': 359,
    "batt_n": 1271,#NREL study
    'grid_n': 205,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_n, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'MMUSD/GWa',
}


# in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M costs
# based on the size of the plant, e.g. lightening, labor, scheduled maintenance, etc.)

costs = {
    "hydro_4": 12.8, #EPE
    "hydro_8": 12.8, #EPE 
    "hydro_9": 12.8,#EPE 
    "sphs_4": 20.5, #EPE
    "sphs_8": 20.5, #EPE 
    "sphs_9": 20.5,#EPE 
    "bio_ppl": 30.8, #EPE
    "gas_ppl": 43.6,#EPE
    "gas_ppl_1": 43.6,#EPE
    "gas_ppl_2": 43.6,#EPE
    "gas_ppl_ccs": 43.6,#PNE
    "gas_ppl_ccs_1": 43.6,#PNE
    "gas_ppl_ccs_2": 43.6,#PNE
    "wind_ppl": 25.6,#EPE
    "coal_ppl": 89.7,#EPE
    "nuc_ppl": 83.3, #EPE
    "solar_pv_ppl":16.7, #EPE
    "oil_ppl": 56.4,
    "batt_n": 31.8, #NREL
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_n, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants

var_cost_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'MMUSD/GWa',
}

costs = {
    "gas_ppl": 219.8, #Considering Gas cost of 4 US$/MMBtu
    "gas_ppl_1": 329.8, #Considering Gas cost of 6 US$/MMBtu
    "gas_ppl_2": 439.7, #Considering Gas cost of 8 US$/MMBtu
    "gas_ppl_ccs": 219.8, #Considering Gas cost of 4 US$/MMBtu
    "gas_ppl_ccs_1": 329.8, #Considering Gas cost of 6 US$/MMBtu
    "gas_ppl_ccs_2": 439.7, #Considering Gas cost of 8 US$/MMBtu
    "coal_ppl": 298.7, #EPE
    "oil_ppl": 898,
    "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
}

for tec, val in costs.items():
    df = make_df(var_cost_n, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity

### 1.1) North baseline and growth parameters
base_activity_n = {
    'node_loc': 'North',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_n1 = {
    'node_loc': 'North',
    'year_act': history,
    'mode': 'n-to-ne',
    'time': 'year',
    'unit': 'GWa',
}
base_activity_n2 = {
    'node_loc': 'North',
    'year_act': history,
    'mode': 'ne-to-n',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 1.82
hydro_act = 7.53
transmission_act_1 = 0.43*transmission_capacity
transmission_act_2 = 0.40*transmission_capacity
transmission_internal_act = 0.41*transmission_internal_capacity

#old activity basen on 2019 BEN
old_activity = {
    "hydro_4": 0.35*9.6, 
    "hydro_8": 0.35*11.03, 
    "hydro_9": 0.35*1.2, 
    'bio_ppl': thermal_act *0.09,
    'gas_ppl': thermal_act *0.81,
    'gas_ppl_1': 0., 
    'gas_ppl_2': 0.,
    'gas_ppl_ccs': 0.,
    'gas_ppl_ccs_1': 0.,
    'gas_ppl_ccs_2': 0.,
    'wind_ppl': 0.13,
    'coal_ppl': thermal_act *0.09, 
    'nuc_ppl': 0.,
    'solar_pv_ppl': 0.001,
    'oil_ppl': thermal_act *0.01,
    'grid_n': transmission_internal_act,
    }

# Adding the old activity of transmission sistem in both modes
old_activity_1 = {
    'grid1': transmission_act_1,
    }

old_activity_2 = {
    'grid1': transmission_act_2,
    }

for tec, val in old_activity.items():
    df = make_df(base_activity_n, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    
for tec, val in old_activity_1.items():    
    df = make_df(base_activity_n1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

for tec, val in old_activity_2.items(): 
    df = make_df(base_activity_n2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    

base_growth_n = {
    'node_loc': 'North',
    'year_act': horizon,
    'time': 'year',
    'mode':'M1',
    'unit': 'GWa',
}

# Bound activities of hydros based on this source peak generation between 2018-2020 for the subsistem in order to keep the historical production from this source
bound_technologies = {
    "hydro_4": 3.41,
    "hydro_8": 3.91,
    "hydro_9": 0.43,
}

for tec, val in bound_technologies.items():
    df = make_df(base_growth_n, technology=tec, value=val) 
    scenario.add_par('bound_activity_up', df)
    
## Bound capacity up
       
total_cap_n = {'hydro_4': 9.6,
                  'hydro_8': 11.03,
                  'hydro_9': 1.2,
                  #'sphs_4': 1.,
                  #'sphs_8': 1.,
                  #'sphs_9': 1.,
                  'wind_ppl': 0.18,
                  'nuc_ppl':0.,
                  'gas_ppl':1.5*thermal_capacity*0.623,
                  'gas_ppl_1':2*thermal_capacity*0.623,
                  'gas_ppl_ccs':1.5*thermal_capacity*0.623,
                  'gas_ppl_ccs_1':2*thermal_capacity*0.623,
                  "bio_ppl": 3.,
                  'solar_pv_ppl': 5.,
                  'coal_ppl': 2.9,
                  'oil_ppl': 0.6, #oil ppl won't be able to raise up it's capacity on the country, considering the environmental restrictions related to this resource.
                  #"batt_n": 10.,
                 }

base_capa = {
    'node_loc': 'North',
    'year_act': horizon,
    #'time': 'year',
    'unit': 'GW',
}

for tec, val in total_cap_n.items():
    df = make_df(base_capa, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)

# %% 2) Northeast baseline

lifetimes = {
    "hydro_3": 60, "sphs_3": 60, "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1": 20, "gas_ppl_2": 20, "gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20, "wind_ppl_int": 20, "wind_ppl_cos": 20, 
    "coal_ppl": 25, "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20, "batt_ne": 15,
    "grid2": 25, "grid_ne": 25, "river3":1000,"water_supply_3":1000,
}

base_input_ne1 = {
    'node_loc': 'Northeast',
    'node_origin': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_ne1 = {
    'node_loc': 'Northeast',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_ne2 = {
    'node_loc': 'Northeast',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-ne',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_ne2 = {
    'node_loc': 'Northeast',
    'node_dest': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-ne',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

#grids

grid_efficiency = 1/0.85
grid_out_ne1 = make_df(base_output_ne1, technology='grid2', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_ne1)

grid_in_ne1 = make_df(base_input_ne1, technology='grid2', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_ne1)

grid_out_ne2 = make_df(base_output_ne2, technology='grid2', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_ne2)

grid_in_ne2 = make_df(base_input_ne2, technology='grid2', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_ne2)

input_ne = {
    'node_loc': 'Northeast',
    'node_origin': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_ne = {
    'node_loc': 'Northeast',
    'node_dest': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# regional grid

grid_eff = 1/0.9
grid_out_ne = make_df(output_ne, technology='grid_ne', commodity='electricity', 
                   level='final', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_ne)

grid_in_ne = make_df(input_ne, technology='grid_ne', commodity='electricity',
                  level='secondary', value=grid_eff, unit="GWa")
scenario.add_par('input', grid_in_ne)

#primary to secondary for hydro_ppl

ne_hydro_out = {"hydro_3": 1.,
            }
# REE 3

for h_plant, val in ne_hydro_out.items():
    h_plant_out_ne = make_df(output_ne, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_ne['year_act'] < h_plant_out_ne['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne = h_plant_out_ne.loc[condition] 
    scenario.add_par('output', h_plant_out_ne)

ne_hydro_out_2 =   {"hydro_3": 595.1,
            } 
    
for h_plant, val in ne_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_ne_2 = make_df(output_ne, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_ne_2['year_act'] < h_plant_out_ne_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne_2 = h_plant_out_ne_2.loc[condition]
    
    scenario.add_par('output', h_plant_out_ne_2)
    
ne_hydro_in = {"hydro_3": 595.1,
            }    

for h_plant, val in ne_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_ne = make_df(input_ne, technology= h_plant, commodity= wat, 
                   level='primary', value= val, unit="m^3/s")
    scenario.add_par('input', h_plant_in_ne)
    
for river in northeast_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_ne = make_df(output_ne, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/s")
    scenario.add_par('output', river_out_ne)
    
#secondary to secondary for sphs_ppl

ne_sphs_out = {"sphs_3": 1,
           }

for h_plant, val in ne_sphs_out.items():
    h_plant_out_ne_3 = make_df(output_ne, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_ne_3['year_act'] < h_plant_out_ne_3['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne_3 = h_plant_out_ne_3.loc[condition] 

    scenario.add_par('output', h_plant_out_ne_3)
    
ne_sphs_out_2 =  {"sphs_3": 190.,
              }
    
for h_plant, val in ne_sphs_out_2.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_out_ne_4 = make_df(output_ne, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_ne_4['year_act'] < h_plant_out_ne_4['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne_4 = h_plant_out_ne_4.loc[condition]
    
    scenario.add_par('output', h_plant_out_ne_4)
    
ne_sphs_in = {"sphs_3": 190.,
              }
    
for h_plant, val in ne_sphs_in.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_in_ne_2 = make_df(input_ne, technology= h_plant, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")

    # Removing extra years based on lifetime 
    condition = h_plant_in_ne_2['year_act'] < h_plant_in_ne_2['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_ne_2 = h_plant_in_ne_2.loc[condition]
    scenario.add_par('input', h_plant_in_ne_2)
    
ne_sphs_in_2 = {"sphs_3": 1.2,
             }
        
for h_plant, val in ne_sphs_in_2.items():
    h_plant_in_ne_3 = make_df(input_ne, technology= h_plant, commodity= 'electricity', 
                      level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_in_ne_3['year_act'] < h_plant_in_ne_3['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_ne_3 = h_plant_in_ne_3.loc[condition]
    scenario.add_par('input', h_plant_in_ne_3)

    
# secondary to final to water_supply

ne_water_out = {"water_supply_3": 595.1,
              }

for w_supply, val in ne_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_ne = make_df(output_ne, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/s")
    scenario.add_par('output', w_supply_out_ne)

ne_water_in = {"water_supply_3": 595.1,
              }
    
for w_supply, val in ne_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_ne = make_df(input_ne, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")
    scenario.add_par('input', w_supply_in_ne)

#secondary to useful e_tecs

for tech in plants:
     tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
      # Removing extra years based on lifetime 
     condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + lifetimes[tech] 
     tech_out_ne = tech_out_ne.loc[condition]
     scenario.add_par('output', tech_out_ne)

for tech in northeast_wind:
     tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
      # Removing extra years based on lifetime 
     condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + lifetimes[tech] 
     tech_out_ne = tech_out_ne.loc[condition]
     scenario.add_par('output', tech_out_ne)
     
#secondary to secondary for batteries

for tech in battery_ne:
    tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                  level='secondary', value=1., unit="GWa")

    # Removing extra years based on lifetime 
    condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + lifetimes[tech] 
    tech_out_ne = tech_out_ne.loc[condition] 
    scenario.add_par('output', tech_out_ne)
    
for tech in battery_ne:
    tech_in_ne = make_df(input_ne, technology=tech, commodity='electricity', 
                  level='secondary', value=1.2, unit="GWa")
    # Removing extra years based on lifetime 
    condition = tech_in_ne['year_act'] < tech_in_ne['year_vtg'] + lifetimes[tech] 
    tech_in_ne = tech_in_ne.loc[condition] 
    scenario.add_par('input', tech_in_ne)


base_technical_lifetime_ne = {
    'node_loc': 'Northeast',
    'year_vtg': horizon,
    'unit': 'y',
}

for tec, val in lifetimes.items():
    df_ne = make_df(base_technical_lifetime_ne, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_ne)

base_capacity_factor_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_3": 0.9,#EPE 
    "sphs_3": 0.7,#EPE 
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_cos": 0.47,#For now, the EPE data of 0.47 in North and Northeast is maintained.
    "wind_ppl_int": 0.47,#For now, the EPE data of 0.47 in North and Northeast is maintained.
    "coal_ppl": 0.69,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75, #EPE
    "grid2": 0.8,
    "batt_ne": 0.85,
    "grid_ne": 0.8,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_ne, technology=tec, value=val)
    # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)

base_capacity_ne = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'Northeast',
    'unit': 'GWa',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
thermal_capacity = 8.40
hydro_capacity = 11.0
transmission_capacity = 2.51
transmission_internal_capacity = 13.23
base_cap = {
    "hydro_3": 8.3/times, 
    "sphs_3": 0./times, 
    "bio_ppl": thermal_capacity*0.164/times,  
    "gas_ppl": thermal_capacity*0.359/times,
    "gas_ppl_1": thermal_capacity*0./times,
    "gas_ppl_2": thermal_capacity*0./times,
    "gas_ppl_ccs": 0./times,
    "gas_ppl_ccs_1": 0./times,
    "gas_ppl_ccs_2": 0./times,
    "wind_ppl_cos": 6.2/times, 
    "wind_ppl_int": 5.94/times, 
    "coal_ppl": thermal_capacity*0.129/times, 
    "nuc_ppl": 0./times, 
    "solar_pv_ppl": 1.4/times,
    "oil_ppl": thermal_capacity*0.348/times,
    "grid2": transmission_capacity/times,
    "batt_ne": 0./times,
    "grid_ne": transmission_internal_capacity/times,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_ne, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

    
# %% Adding costs

base_inv_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': horizon,
    'unit': 'MMUSD/GWa',
}

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_3": 1352,#EPE mean value for UHE
    "sphs_3": 1500,#EPE
    "bio_ppl": 1200,#EPE 
    "gas_ppl": 900, #EPE mean value
    "gas_ppl_1": 1000, #EPE mean value
    "gas_ppl_2": 1000, #EPE mean value
    "gas_ppl_ccs": 1.8*900, #PNE
    "gas_ppl_ccs_1": 1.8*1000, #PNE
    "gas_ppl_ccs_2": 1.8*1000, #PNE
    "wind_ppl_cos": 1200,#It will be considered same values. The only difference will be capacity factor
    "wind_ppl_int": 1200,#It will be considered same values. The only difference will be capacity factor
    "coal_ppl": 2500, #EPE
    "nuc_ppl": 5000,#EPE
    "solar_pv_ppl":1100, #min value in EPE, max value is 1350
    "oil_ppl": 1100,
    'grid2': 359,
    "batt_ne": 1271, #NREL study
    'grid_ne': 205,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_ne, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'MMUSD/GWa',
}

# in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M costs
# based on the size of the plant, e.g. lightning, labor, scheduled maintenance, etc.)

costs = {
    "hydro_3": 12.8,#EPE
    "sphs_3": 20.5,#EPE
    "bio_ppl": 30.8, #EPE
    "gas_ppl": 43.6,#EPE
    "gas_ppl_1": 43.6,#EPE
    "gas_ppl_2": 43.6,#EPE
    "gas_ppl_ccs": 43.6,#EPE
    "gas_ppl_ccs_1": 43.6,#EPE
    "gas_ppl_ccs_2": 43.6,#EPE
    "wind_ppl_cos": 25.6,#EPE
    "wind_ppl_int": 25.6,#EPE
    "coal_ppl": 89.7,#EPE
    "nuc_ppl": 83.3, #EPE
    "solar_pv_ppl":16.7, #EPE
    "oil_ppl": 56.4,
    "batt_ne": 31.8,#NREL
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_ne, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants
var_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'MMUSD/GWa',
}

costs = {
    "gas_ppl": 219.8, #EPE mean value
    "gas_ppl_1": 329.8, #EPE mean value
    "gas_ppl_2": 439.7, #EPE mean value
    "gas_ppl_ccs": 219.8, #EPE mean value
    "gas_ppl_ccs_1": 329.8, #EPE mean value
    "gas_ppl_ccs_2": 439.7, #EPE mean value
    "coal_ppl": 298.7, #EPE
    "oil_ppl": 898,
    "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
}

for tec, val in costs.items():
    df = make_df(var_cost_ne, technology=tec, value=val)
    scenario.add_par('var_cost', df)
    

# %% Acitvity and Capacity

### 2.2) Northeast base and growth

base_activity_ne = {
    'node_loc': 'Northeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_ne1 = {
    'node_loc': 'Northeast',
    'year_act': history,
    'mode': 'ne-to-se',
    'time': 'year',
    'unit': 'GWa',
}
base_activity_ne2 = {
    'node_loc': 'Northeast',
    'year_act': history,
    'mode': 'se-to-ne',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 1.98
hydro_act = 2.47
transmission_act_1 = 0.49*transmission_capacity
transmission_act_2 = 0.24*transmission_capacity
transmission_internal_act = 0.42*transmission_internal_capacity

#old activity basen on 2019 BEN
old_activity = {
    "hydro_3": 0.3*8.3, 
    'bio_ppl': thermal_act*0.102,
    'gas_ppl': thermal_act*0.493,
    'gas_ppl_1': thermal_act*0.,
    'gas_ppl_2': thermal_act*0.,
    'gas_ppl_ccs': 0.,
    'gas_ppl_ccs_1': 0.,
    'gas_ppl_ccs_2': 0.,    
    'wind_ppl_cos': 2.86,#Based on 2019 BEN 5.54 GWa informed, using percentages of generation from 2018 in RN and CE compared to the total amount of Northeast region. 
    'wind_ppl_int': 2.68,#Based on 2019 BEN 5.54 GWa informed, using percentages of generation from 2018 in BA and PI compared to the total amount of Northeast region. 
    'coal_ppl': thermal_act*0.335, 
    'nuc_ppl': 0. ,
    'solar_pv_ppl': 0.37,
    'oil_ppl': thermal_act *0.071,
    'grid_ne': transmission_internal_act,
}

# Adding the old activity of transmission sistem in both modes
old_activity_1 = {
    'grid2': transmission_act_1,
    }

old_activity_2 = {
    'grid2': transmission_act_2,
    }

for tec, val in old_activity.items():
    df = make_df(base_activity_ne, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

for tec, val in old_activity_1.items():
    df = make_df(base_activity_ne1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    
for tec, val in old_activity_2.items():
    df = make_df(base_activity_ne2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

base_growth_ne = {
    'node_loc': 'Northeast',
    'year_act': horizon,
    'time': 'year',
    'mode':'M1',
    'unit':'GWa',
}

# Bound activities of hydros based on this source peak generation between 2018-2020 for the subsistem in order to keep the historical production from this source
bound_technologies = {
    "hydro_3": 4.33, 
}


for tec, val in bound_technologies.items():
    df = make_df(base_growth_ne, technology=tec, value=val) 
    scenario.add_par('bound_activity_up', df)

## Bound capacity

total_cap_ne = {'hydro_3': 8.3,
                   #'sphs_3': 1.,
                   'wind_ppl_cos': 80,
                   'wind_ppl_int': 80,
                   'solar_pv_ppl': 10,
                   "gas_ppl": 4.71,
                   "gas_ppl_1": 16,                   
                   "gas_ppl_ccs": 4.71,
                   "gas_ppl_ccs_1": 16,
                   'nuc_ppl': 0.,
                   "bio_ppl": 5.,
                   'coal_ppl': 7.0, 
                   'oil_ppl': 2.9,#oil ppl won't be able to raise up it's capacity on the country, considering the environmental restrictions related to this resource
                   #"batt_ne": 20,
}

base_capa = {
    'node_loc': 'Northeast',
    'year_act': horizon,
    #'time': 'year',
    'unit': 'GW',
}

for tec, val in total_cap_ne.items():
    df = make_df(base_capa, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)
    
# %% 3) Southeast baseline

lifetimes = {
    "hydro_1": 60, "hydro_5": 60, "hydro_6": 60, "hydro_7": 60, "hydro_10": 60, "hydro_12": 60,
    "sphs_1": 60, "sphs_6": 60, "sphs_7": 60, "sphs_10": 60, "sphs_12": 60,
    "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1": 20, "gas_ppl_2": 20, "gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20,"wind_ppl": 20,  "coal_ppl": 25, "batt_se": 15,
    "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "grid3": 25, "grid_se": 25, "river1":1000, "river5":1000, "river6":1000, "river7":1000, "river10":1000, "river12":1000,
    "water_supply_1":1000, "water_supply_5":1000, "water_supply_6":1000, "water_supply_7":1000, "water_supply_10":1000, "water_supply_12":1000
}

base_input_se1 = {
    'node_loc': 'Southeast',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-n',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_se1 = {
    'node_loc': 'Southeast',
    'node_dest': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-n',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_se2 = {
    'node_loc': 'Southeast',
    'node_origin': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_se2 = {
    'node_loc': 'Southeast',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

#grids

grid_efficiency = 1/0.85
grid_out_se1 = make_df(base_output_se1, technology='grid3', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_se1)

grid_in_se1 = make_df(base_input_se1, technology='grid3', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_se1)

grid_out_se2 = make_df(base_output_se2, technology='grid3', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_se2)

grid_in_se2 = make_df(base_input_se2, technology='grid3', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_se2)

input_se = {
    'node_loc': 'Southeast',
    'node_origin': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_se = {
    'node_loc': 'Southeast',
    'node_dest': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# regional grid

grid_eff = 1/0.9
grid_out_se = make_df(output_se, technology='grid_se', commodity='electricity', 
                   level='final', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_se)

grid_in_se = make_df(input_se, technology='grid_se', commodity='electricity',
                  level='secondary', value=grid_eff, unit="GWa")
scenario.add_par('input', grid_in_se)


se_hydro_out = {"hydro_1": 1,
"hydro_5": 1.,
"hydro_6": 1., 
"hydro_7": 1.,
"hydro_10": 1., 
"hydro_12": 1.,
}

for h_plant, val in se_hydro_out.items():
    h_plant_out_se = make_df(output_se, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_se['year_act'] < h_plant_out_se['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se = h_plant_out_se.loc[condition]
    scenario.add_par('output', h_plant_out_se)
    
se_hydro_out_2 = {"hydro_1": 456.0,
"hydro_5": 968.0,
"hydro_6": 3793.4, 
"hydro_7": 1205.3,
"hydro_10": 560.6, 
"hydro_12": 1004.9,
}
    
for h_plant, val in se_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_se_2 = make_df(output_se, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_se_2['year_act'] < h_plant_out_se_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se_2 = h_plant_out_se_2.loc[condition]
    scenario.add_par('output', h_plant_out_se_2)
    
se_hydro_in = {"hydro_1": 456.0,
"hydro_5": 968.0,
"hydro_6": 3793.4, 
"hydro_7": 1205.3,
"hydro_10": 560.6, 
"hydro_12": 1004.9,
}

for h_plant, val in se_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_se = make_df(input_se, technology= h_plant, commodity= wat, 
                   level='primary', value= val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_in_se['year_act'] < h_plant_in_se['year_vtg'] + lifetimes[h_plant] 
    h_plant_in_se = h_plant_in_se.loc[condition]
    scenario.add_par('input', h_plant_in_se)
    
for river in southeast_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_se = make_df(output_se, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/s") 
    scenario.add_par('output', river_out_se)

#secondary to secondary for sphs_ppl

se_sphs_out = {"sphs_1": 1,
               "sphs_6": 1,
               "sphs_7": 1,
               "sphs_10": 1,
               "sphs_12": 1
           }

for h_plant, val in se_sphs_out.items():
    h_plant_out_se_3 = make_df(output_se, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_se_3['year_act'] < h_plant_out_se_3['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se_3 = h_plant_out_se_3.loc[condition] 

    scenario.add_par('output', h_plant_out_se_3)
    
se_sphs_out_2 =  {"sphs_1": 248,
               "sphs_6": 30,
               "sphs_7": 94,
               "sphs_10": 202,
               "sphs_12": 112
              }
    
for h_plant, val in se_sphs_out_2.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_out_se_4 = make_df(output_se, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_se_4['year_act'] < h_plant_out_se_4['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se_4 = h_plant_out_se_4.loc[condition]
    
    scenario.add_par('output', h_plant_out_se_4)
    
se_sphs_in = {"sphs_1": 248,
               "sphs_6": 30,
               "sphs_7": 94,
               "sphs_10": 202,
               "sphs_12": 112
              }
    
for h_plant, val in se_sphs_in.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_in_se_2 = make_df(input_se, technology= h_plant, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")

    # Removing extra years based on lifetime 
    condition = h_plant_in_se_2['year_act'] < h_plant_in_se_2['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_se_2 = h_plant_in_se_2.loc[condition]
    scenario.add_par('input', h_plant_in_se_2)
    
se_sphs_in_2 = {"sphs_1": 1.2,
               "sphs_6": 1.2,
               "sphs_7": 1.2,
               "sphs_10": 1.2,
               "sphs_12": 1.2
             }
        
for h_plant, val in se_sphs_in_2.items():
    h_plant_in_se_3 = make_df(input_se, technology= h_plant, commodity= 'electricity', 
                      level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_in_se_3['year_act'] < h_plant_in_se_3['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_se_3 = h_plant_in_se_3.loc[condition]
    scenario.add_par('input', h_plant_in_se_3)

# secondary to final to water_supply

se_water_out = {"water_supply_1": 456.0,
                "water_supply_5": 968.0,
                "water_supply_6": 3793.4, 
                "water_supply_7": 1205.3,
                "water_supply_10": 560.6, 
                "water_supply_12": 1004.9,
                 }

for w_supply, val in se_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_se = make_df(output_se, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/s") 
    scenario.add_par('output', w_supply_out_se)

se_water_in = {"water_supply_1": 456.0,
               "water_supply_5": 968.0,
               "water_supply_6": 3793.4, 
               "water_supply_7": 1205.3,
               "water_supply_10": 560.6, 
               "water_supply_12": 1004.9,
              }
    
for w_supply, val in se_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_se = make_df(input_se, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")
    scenario.add_par('input', w_supply_in_se)

#secondary to useful e_tecs

for tech in brazil_wind:
     tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + lifetimes[tech] 
     tech_out_se = tech_out_se.loc[condition]
     scenario.add_par('output', tech_out_se)

for tech in plants:
     tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + lifetimes[tech] 
     tech_out_se = tech_out_se.loc[condition]
     scenario.add_par('output', tech_out_se)

#secondary to secondary for batteries

for tech in battery_se:
    tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                  level='secondary', value=1., unit="GWa")

    # Removing extra years based on lifetime 
    condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + lifetimes[tech] 
    tech_out_se = tech_out_se.loc[condition] 
    scenario.add_par('output', tech_out_se)
    
for tech in battery_se:
    tech_in_se = make_df(input_se, technology=tech, commodity='electricity', 
                  level='secondary', value=1.2, unit="GWa")
    # Removing extra years based on lifetime 
    condition = tech_in_se['year_act'] < tech_in_se['year_vtg'] + lifetimes[tech] 
    tech_in_se = tech_in_se.loc[condition] 
    scenario.add_par('input', tech_in_se)

base_technical_lifetime_se = {
    'node_loc': 'Southeast',
    'year_vtg': horizon,
    'unit': 'y',
}

for tec, val in lifetimes.items():
    df_se = make_df(base_technical_lifetime_se, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_se)

base_capacity_factor_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_1": 0.9, #EPE
    "hydro_5": 0.9,#EPE
    "hydro_6": 0.9,#EPE
    "hydro_7": 0.9,#EPE
    "hydro_10": 0.9,#EPE
    "hydro_12": 0.9,#EPE
    "sphs_1": 0.7, #EPE
    "sphs_6": 0.7,#EPE
    "sphs_7": 0.7,#EPE
    "sphs_10": 0.7,#EPE
    "sphs_12": 0.7,#EPE    
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "coal_ppl": 0.69,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.29,
    "oil_ppl": 0.75, #EPE
    "grid3": 0.8,
    "batt_se": 0.85,
    "grid_se": 0.8,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_se, technology=tec, value=val)
     # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)

base_capacity_se = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'Southeast',
    'unit': 'GWa',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
thermal_capacity = 18.69 
hydro_capacity = 65.2
transmission_capacity = 9.46
transmission_internal_capacity = 51.2
base_cap = {
    "hydro_1": 6.4/times, 
    "hydro_5": 14./times, 
    "hydro_6": 7.3/times, 
    "hydro_7": 3.2/times,
    "hydro_10": 27.6/times,
    "hydro_12": 2.4/times,
    "sphs_1": 0./times, 
    "sphs_6": 0./times, 
    "sphs_7": 0./times,
    "sphs_10": 0./times,
    "sphs_12": 0./times,
    "bio_ppl": thermal_capacity*0.552/times,  
    "gas_ppl": thermal_capacity*0.364/times,
    "gas_ppl_1": thermal_capacity*0./times,
    "gas_ppl_2": thermal_capacity*0./times,
    "gas_ppl_ccs": 0./times,
    "gas_ppl_ccs_1": 0./times,
    "gas_ppl_ccs_2": 0./times,
    "wind_ppl": 0.03/times, 
    "coal_ppl": thermal_capacity*0.0/times, 
    "nuc_ppl": 2.0/times, 
    "solar_pv_ppl": 0.74/times,
    "oil_ppl": thermal_capacity*0.084/times,
    "grid3": transmission_capacity/times,
    "batt_se": 0./times,
    "grid_se": transmission_internal_capacity/times,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_se, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?
    
    
# %% Adding costs

base_inv_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': horizon,
    'unit': 'MMUSD/GWa',
}

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_1": 1352,#EPE mean value for UHE
    "hydro_5": 1352,#EPE mean value for UHE
    "hydro_6": 1352,#EPE mean value for UHE
    "hydro_7": 1352,#EPE mean value for UHE
    "hydro_10": 1352,#EPE mean value for UHE
    "hydro_12": 1352,#EPE mean value for UHE
    "sphs_1": 1500,#EPE
    "sphs_6": 1500,#EPE
    "sphs_7": 1500,#EPE
    "sphs_10": 1500,#EPE
    "sphs_12": 1500,#EPE
    "bio_ppl": 1200,#EPE 
    "gas_ppl": 900, #EPE mean value
    "gas_ppl_1": 1000, #EPE mean value
    "gas_ppl_2": 1000, #EPE mean value
    "gas_ppl_ccs": 1.8*900, #EPE mean value
    "gas_ppl_ccs_1": 1.8*1000, #EPE mean value
    "gas_ppl_ccs_2": 1.8*1000, #EPE mean value
    "wind_ppl": 1200,#EPE mean value
    "coal_ppl": 2500, #EPE
    "nuc_ppl": 5000,#EPE
    "solar_pv_ppl":1100, #min value in EPE, max value is 1350
    "oil_ppl": 1100,
    'grid3': 462,
    "batt_se": 1271, #NREL study
    'grid_se': 205,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_se, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'MMUSD/GWa',
}

costs = {
    "hydro_1": 12.8,
    "hydro_5": 12.8,
    "hydro_6": 12.8,
    "hydro_7": 12.8,
    "hydro_10": 12.8,
    "hydro_12": 12.8,
    "sphs_1": 20.5,#EPE
    "sphs_6": 20.5,#EPE
    "sphs_7": 20.5,#EPE
    "sphs_10": 20.5,#EPE
    "sphs_12": 20.5,#EPE   
    "bio_ppl": 30.8, #EPE
    "gas_ppl": 43.6,#EPE
    "gas_ppl_1": 43.6,#EPE
    "gas_ppl_2": 43.6,#EPE
    "gas_ppl_ccs": 43.6,#EPE
    "gas_ppl_ccs_1": 43.6,#EPE
    "gas_ppl_ccs_2": 43.6,#EPE
    "wind_ppl": 25.6,#EPE
    "coal_ppl": 89.7,#EPE
    "nuc_ppl": 83.3, #EPE
    "solar_pv_ppl":16.7, #EPE
    "oil_ppl": 56.4,
    "batt_se": 31.8, #NREL
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_se, technology=tec, value=val)
    scenario.add_par('fix_cost', df)
    
### Adding variable cost = fuel cost to thermal power plants

var_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'MMUSD/GWa',
}

costs = {
    "gas_ppl": 219.8, #EPE mean value
    "gas_ppl_1": 329.8, #EPE mean value
    "gas_ppl_2": 439.7, #EPE mean value
    "gas_ppl_ccs": 219.8, #EPE mean value
    "gas_ppl_ccs_1": 329.8, #EPE mean value
    "gas_ppl_ccs_2": 439.7, #EPE mean value
    "coal_ppl": 298.7, #EPE
    "oil_ppl": 898,
    "nuc_ppl": 53.3,
    "bio_ppl":0.000001, #Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
}

for tec, val in costs.items():
    df = make_df(var_cost_se, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity

### 3.1) Southeast base and growth

base_activity_se = {
    'node_loc': 'Southeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_se1 = {
    'node_loc': 'Southeast',
    'year_act': history,
    'mode': 'n-to-se',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_se2 = {
    'node_loc': 'Southeast',
    'year_act': history,
    'mode': 'se-to-n',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 5.11
hydro_act = 28.93
transmission_act_1 = 0.48*transmission_capacity
transmission_act_2 = 0.05*transmission_capacity
transmission_internal_act = 0.48*transmission_internal_capacity
#old activity basen on 2019 BEN
old_activity = {
    "hydro_1": 0.48*6.4, 
    "hydro_5": 0.48*14, 
    "hydro_6": 0.48*7.3, 
    "hydro_7": 0.48*3.2,
    "hydro_10": 0.48*27.6,
    "hydro_12": 0.48*2.4,
    'bio_ppl': thermal_act*0.445,
    'gas_ppl': thermal_act*0.522,
    'gas_ppl_1': thermal_act*0.,
    'gas_ppl_2': thermal_act*0.,
    'gas_ppl_ccs': 0., 
    'gas_ppl_ccs_1': 0.,
    'gas_ppl_ccs_2': 0.,
    'wind_ppl': 0.007,
    'coal_ppl': thermal_act*0.0, 
    'nuc_ppl': 1.841,
    'solar_pv_ppl': 0.19,
    'oil_ppl': thermal_act *0.033,
    'grid_se': transmission_internal_act,
}

# Adding the old activity of transmission sistem in both modes
old_activity_1 = {
    'grid3': transmission_act_1,
    }

old_activity_2 = {
    'grid3': transmission_act_2,
    }

for tec, val in old_activity.items():
    df = make_df(base_activity_se, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    
for tec, val in old_activity_1.items():
    df = make_df(base_activity_se1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

for tec, val in old_activity_2.items():
    df = make_df(base_activity_se2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

base_growth_se = {
    'node_loc': 'Southeast',
    'year_act': horizon,
    'time': 'year',
    'mode':'M1',
    'unit': 'GWa',
}

# Bound activities of hydros based on this source peak generation between 2018-2020 for the subsistem in order to keep the historical production from this source
bound_technologies = {
    "hydro_1": 3.15, 
    "hydro_5": 6.89,
    "hydro_6": 3.59,
    "hydro_7": 1.58,
    "hydro_10": 13.58,
    "hydro_12": 1.18, 
}

for tec, val in bound_technologies.items():
    df = make_df(base_growth_se, technology=tec, value=val) 
    scenario.add_par('bound_activity_up', df)
    
## Bound capacity

total_cap_se = { "hydro_1": 6.4,
    "hydro_5": 14.,
    "hydro_6": 7.3,
    "hydro_7": 3.2,
    "hydro_10": 27.6,
    "hydro_12": 2.4,
    #"sphs_1": 1.,
    #"sphs_6": 1.,
    #"sphs_7": 1.,
    #"sphs_10": 1.,
    #"sphs_12": 1.,
    "coal_ppl": 7.0,
    "bio_ppl": 17.,
    "oil_ppl": 3,
    "gas_ppl": 12.24,
    "gas_ppl_1": 30,
    "gas_ppl_ccs": 12.24,
    "gas_ppl_ccs_1": 30,
    "nuc_ppl": 5.,
    "wind_ppl": 0.03,
    "solar_pv_ppl": 25.,
    #"batt_se": 50.,       
}

base_capa = {
    'node_loc': 'Southeast',
    'year_act': horizon,
    #'time': 'year',
    'unit': 'GW',
}

for tec, val in total_cap_se.items():
    df = make_df(base_capa, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)

# %% 4) South baseline

lifetimes = {
    "hydro_2": 60, "hydro_11": 60, "sphs_2": 60, "sphs_11": 60, "bio_ppl": 20, "gas_ppl": 20, "gas_ppl_1": 20, "gas_ppl_2": 20,"gas_ppl_ccs": 20, "gas_ppl_ccs_1": 20, "gas_ppl_ccs_2": 20, "wind_ppl_rs": 20,  
    "coal_ppl": 25, "nuc_ppl": 60, "solar_pv_ppl":20,  "oil_ppl": 20, "batt_s": 15,
    "grid4": 25, "grid_s": 25, "river2":1000, "river11":1000,"water_supply_2":1000, "water_supply_11":1000
}

base_input_s1 = {
    'node_loc': 'South',
    'node_origin': 'South',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 's-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_s1 = {
    'node_loc': 'South',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 's-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_s2 = {
    'node_loc': 'South',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-s',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_s2 = {
    'node_loc': 'South',
    'node_dest': 'South',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-s',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

#grids

grid_efficiency = 1/0.85
grid_out_s1 = make_df(base_output_s1, technology='grid4', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_s1)

grid_in_s1 = make_df(base_input_s1, technology='grid4', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_s1)

grid_out_s2 = make_df(base_output_s2, technology='grid4', commodity='electricity', 
                   level='secondary', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_s2)

grid_in_s2 = make_df(base_input_s2, technology='grid4', commodity='electricity',
                  level='secondary', value=grid_efficiency, unit="GWa")
scenario.add_par('input', grid_in_s2)

input_s = {
    'node_loc': 'South',
    'node_origin': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_s = {
    'node_loc': 'South',
    'node_dest': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# regional grid

grid_eff = 1/0.9
grid_out_s = make_df(output_s, technology='grid_s', commodity='electricity', 
                   level='final', value=1.0, unit="GWa")
scenario.add_par('output', grid_out_s)

grid_in_s = make_df(input_s, technology='grid_s', commodity='electricity',
                  level='secondary', value=grid_eff, unit="GWa")
scenario.add_par('input', grid_in_s)

#primary to secondary for hydro_ppl

s_hydro_out = {"hydro_2": 1.,
           "hydro_11": 1.,
}

for h_plant, val in s_hydro_out.items():
    h_plant_out_s = make_df(output_s, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_s['year_act'] < h_plant_out_s['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s = h_plant_out_s.loc[condition]
    scenario.add_par('output', h_plant_out_s)

s_hydro_out_2 = {"hydro_2": 431.4,
                  "hydro_11": 457.4,
                  }
    
for h_plant, val in s_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_s_2 = make_df(output_s, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_s_2['year_act'] < h_plant_out_s_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s_2 = h_plant_out_s_2.loc[condition]
    scenario.add_par('output', h_plant_out_s_2)
    
s_hydro_in = {"hydro_2": 431.4,
           "hydro_11": 457.4,
}

for h_plant, val in s_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_s = make_df(input_s, technology= h_plant, commodity= wat, 
                   level='primary', value= val, unit="m^3/s")
    # Removing extra years based on lifetime 
    condition = h_plant_in_s['year_act'] < h_plant_in_s['year_vtg'] + lifetimes[h_plant] 
    h_plant_in_s = h_plant_in_s.loc[condition]
    scenario.add_par('input', h_plant_in_s)
    
for river in south_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_s = make_df(output_s, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/s")
    scenario.add_par('output', river_out_s)

#secondary to secondary for sphs_ppl

s_sphs_out = {"sphs_2": 1,
              "sphs_11": 1,
               }

for h_plant, val in s_sphs_out.items():
    h_plant_out_s_3 = make_df(output_s, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_s_3['year_act'] < h_plant_out_s_3['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s_3 = h_plant_out_s_3.loc[condition] 

    scenario.add_par('output', h_plant_out_s_3)
    
s_sphs_out_2 =  {"sphs_2": 263,
              "sphs_11": 247,
              }
    
for h_plant, val in s_sphs_out_2.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_out_s_4 = make_df(output_s, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/s")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_s_4['year_act'] < h_plant_out_s_4['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s_4 = h_plant_out_s_4.loc[condition]
    
    scenario.add_par('output', h_plant_out_s_4)
    
s_sphs_in = {"sphs_2": 263,
              "sphs_11": 247,
              }
    
for h_plant, val in s_sphs_in.items():
    wat = 'water_' + h_plant.split('sphs_')[1]  
    h_plant_in_s_2 = make_df(input_s, technology= h_plant, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")

    # Removing extra years based on lifetime 
    condition = h_plant_in_s_2['year_act'] < h_plant_in_s_2['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_s_2 = h_plant_in_s_2.loc[condition]
    scenario.add_par('input', h_plant_in_s_2)
    
s_sphs_in_2 = {"sphs_2": 1.2,
              "sphs_11": 1.2,
             }
        
for h_plant, val in s_sphs_in_2.items():
    h_plant_in_s_3 = make_df(input_s, technology= h_plant, commodity= 'electricity', 
                      level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_in_s_3['year_act'] < h_plant_in_s_3['year_vtg'] + lifetimes[h_plant] 

    h_plant_in_s_3 = h_plant_in_s_3.loc[condition]
    scenario.add_par('input', h_plant_in_s_3)

# secondary to final to water_supply

s_water_out = {"water_supply_2": 431.4,
                "water_supply_11": 457.4,
              }

for w_supply, val in s_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_s = make_df(output_s, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/s")
    scenario.add_par('output', w_supply_out_s)

se_water_in = {"water_supply_2": 431.4,
                "water_supply_11": 457.4,
              }
    
for w_supply, val in se_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_s = make_df(input_s, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/s")
    scenario.add_par('input', w_supply_in_s)

#secondary to useful e_tecs

for tech in plants:
     tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + lifetimes[tech] 
     tech_out_s = tech_out_s.loc[condition]
     scenario.add_par('output', tech_out_s)

for tech in south_wind:
     tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + lifetimes[tech] 
     tech_out_s = tech_out_s.loc[condition]
     scenario.add_par('output', tech_out_s)
     
#secondary to secondary for batteries

for tech in battery_s:
    tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                  level='secondary', value=1., unit="GWa")

    # Removing extra years based on lifetime 
    condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + lifetimes[tech] 
    tech_out_s = tech_out_s.loc[condition] 
    scenario.add_par('output', tech_out_s)
    
for tech in battery_s:
    tech_in_s = make_df(input_s, technology=tech, commodity='electricity', 
                  level='secondary', value=1.2, unit="GWa")
    # Removing extra years based on lifetime 
    condition = tech_in_s['year_act'] < tech_in_s['year_vtg'] + lifetimes[tech] 
    tech_in_s = tech_in_s.loc[condition] 
    scenario.add_par('input', tech_in_s)
     
base_technical_lifetime_s = {
    'node_loc': 'South',
    'year_vtg': horizon,
    'unit': 'y',
}

for tec, val in lifetimes.items():
    df_s = make_df(base_technical_lifetime_s, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_s)

base_capacity_factor_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_2": 0.9,#EPE 
    "hydro_11": 0.9,#EPE 
    "sphs_2": 0.7,#EPE 
    "sphs_11": 0.7,#EPE 
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_1": 0.75,#EPE 56% of gas_ppl are combined cycle
    "gas_ppl_ccs_2": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_rs": 0.4,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "coal_ppl": 0.69,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.29,
    "oil_ppl": 0.75, #EPE
    "grid4": 0.8,
    "batt_s": 0.85,
    "grid_s": 0.8,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_s, technology=tec, value=val)
    # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)
  
base_capacity_s = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'South',
    'unit': 'GWa',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
thermal_capacity = 4.72
transmission_capacity = 11.22
transmission_internal_capacity = 18.0
hydro_capacity = 17.0
base_cap = {
    "hydro_2": 6.9/times,
    "hydro_11": 7.3/times,
    "sphs_2": 0./times,
    "sphs_11": 0./times,
    "bio_ppl": thermal_capacity*0.266/times,  
    "gas_ppl": thermal_capacity*0.291/times,
    "gas_ppl_1": thermal_capacity*0./times,
    "gas_ppl_2": thermal_capacity*0./times,
    "gas_ppl_ccs": 0./times,
    "gas_ppl_ccs_1": 0./times,
    "gas_ppl_ccs_2": 0./times,
    "wind_ppl_rs": 2.07/times,        
    "coal_ppl": thermal_capacity*0.438/times, 
    "nuc_ppl": 0./times, 
    "solar_pv_ppl": 0.004/times,
    "oil_ppl": thermal_capacity*0.005/times,
    "grid4": transmission_capacity/times,
    "batt_s": 0./times,
    "grid_s": transmission_internal_capacity/times,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_s, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?
       
# %% Adding costs

base_inv_cost_s = {
    'node_loc': 'South',
    'year_vtg': horizon,
    'unit': 'MMUSD/GWa',
}

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_2": 1352,#EPE mean value for UHE
    "hydro_11": 1352,
    "sphs_2": 1500,#EPE mean value for UHE
    "sphs_11": 1500,
    "bio_ppl": 1200,#EPE 
    "gas_ppl": 900, #EPE mean value
    "gas_ppl_1": 1000, #EPE mean value
    "gas_ppl_2": 1000, #EPE mean value
    "gas_ppl_ccs": 1.8*900, #PNE
    "gas_ppl_ccs_1": 1.8*1000, #PNE
    "gas_ppl_ccs_2": 1.8*1000, #PNE
    "wind_ppl_rs": 1200,#EPE mean value
    "coal_ppl": 2100, #EPE
    "nuc_ppl": 5000,#EPE
    "solar_pv_ppl":1100, #min value in EPE, max value is 1350
    "oil_ppl": 1100,
    'grid4': 205,#EPE NT pr 007/2018
    "batt_s": 1271,#NREL study
    'grid_s': 205,
  }

for tec, val in costs.items():
    df = make_df(base_inv_cost_s, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'MMUSD/GWa',
}

costs = {
    "hydro_2": 12.8,#EPE
    "hydro_11": 12.8,#EPE
    "sphs_2": 20.5,#EPE
    "sphs_11": 20.5,#EPE
    "bio_ppl": 30.8, #EPE
    "gas_ppl": 43.6,#EPE
    "gas_ppl_1": 43.6,#EPE
    "gas_ppl_2": 43.6,#EPE
    "gas_ppl_ccs": 43.6,#EPE
    "gas_ppl_ccs_1": 43.6,#EPE
    "gas_ppl_ccs_2": 43.6,#EPE
    "wind_ppl_rs": 25.6,#EPE
    "coal_ppl": 89.7,#EPE
    "nuc_ppl": 83.3, #EPE
    "solar_pv_ppl":16.7, #EPE
    "oil_ppl": 56.4,
    "batt_s": 31.8, #NREL
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_s, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants

var_cost_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'MMUSD/GWa',
}

costs = {
    "gas_ppl": 219.8, #EPE mean value
    "gas_ppl_1": 329.8, #EPE mean value
    "gas_ppl_2": 439.7, #EPE mean value
    "gas_ppl_ccs": 219.8, #EPE mean value
    "gas_ppl_ccs_1": 329.8, #EPE mean value
    "gas_ppl_ccs_2": 439.7, #EPE mean value
    "coal_ppl": 136.6, #EPE national coal
    "oil_ppl": 898,
    "bio_ppl":0.000001,#Considering an irrelevant cost to guarantee that the generation can be different from capacity factor
}

for tec, val in costs.items():
    df = make_df(var_cost_s, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity
### 4.1) South base and growth

base_activity_s = {
    'node_loc': 'South',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_s1 = {
    'node_loc': 'South',
    'year_act': history,
    'mode': 'se-to-s',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_s2 = {
    'node_loc': 'South',
    'year_act': history,
    'mode': 's-to-se',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 1.05
hydro_act = 7.45
transmission_act_1 = 0.47*transmission_capacity
transmission_act_2 = 0.11*transmission_capacity
transmission_internal_act = 0.42*transmission_internal_capacity
#old activity basen on 2019 BEN
old_activity = {
    "hydro_2": 0.52*6.9,
    "hydro_11": 0.52*7.3,
    "bio_ppl": 0.24*thermal_act,  
    "gas_ppl": 0.023*thermal_act,
    "gas_ppl_1": 0.0*thermal_act,
    "gas_ppl_2": 0.0*thermal_act,
    "gas_ppl_ccs": 0.,
    "gas_ppl_ccs_1": 0.,
    "gas_ppl_ccs_2": 0.,
    "wind_ppl_rs": 0.7, 
    "coal_ppl": 0.717*thermal_act, 
    "nuc_ppl": 0.0, 
    "solar_pv_ppl": 0.01,
    "oil_ppl": 0.019*thermal_act,
    'grid_s': transmission_internal_act,
}

# Adding the old activity of transmission sistem in both modes
old_activity_1 = {
    'grid4': transmission_act_1,
    }

old_activity_2 = {
    'grid4': transmission_act_2,
    }

for tec, val in old_activity.items():
    df = make_df(base_activity_s, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

for tec, val in old_activity_1.items():
    df = make_df(base_activity_s1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    
for tec, val in old_activity_2.items():
    df = make_df(base_activity_s2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

    
base_growth_s = {
    'node_loc': 'South',
    'year_act': horizon,
    'time': 'year',
    'mode':'M1',
    'unit': 'GWa',
}

# Bound activities of hydros based on this source peak generation between 2018-2020 for the subsistem in order to keep the historical production from this source
bound_technologies = {
    "hydro_2": 3.66,
    "hydro_11": 3.87,
}

for tec, val in bound_technologies.items():
    df = make_df(base_growth_s, technology=tec, value=val) 
    scenario.add_par('bound_activity_up', df)

## Bound capacity

total_cap_s = {"hydro_2": 6.9,
                  "hydro_11": 7.3,
                  #"sphs_2": 1.,
                  #"sphs_11": 1.,
                  "coal_ppl": 7.0,
                  "oil_ppl": 0.13,
                  "gas_ppl": 1.5*thermal_capacity*0.291,
                  "gas_ppl_1": 16,
                  "gas_ppl_ccs": 1.5*thermal_capacity*0.291,
                  "gas_ppl_ccs_1": 16,
                  'nuc_ppl':0.,
                  "bio_ppl": 5.,
                  "wind_ppl_rs": 70.0,
                  "solar_pv_ppl": 10.0,
                  #"batt_s": 20.,
                   }

base_capa = {
    'node_loc': 'South',
    'year_act': horizon,
    #'time': 'year',
    'unit': 'GW',
}

for tec, val in total_cap_s.items():
    df = make_df(base_capa, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)

# %% solving the model

## Commit the datastructure and solve the model

scenario.commit(comment='Brazilian_base')

scenario.solve()
scenario.var('OBJ')['lvl']
scenario.set_as_default()
scenario.version
scenario.to_excel('SIN expandido base.xlsx')

#mp.close_db()



      
