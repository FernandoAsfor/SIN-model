 # -*- coding: utf-8 -*-
"""
This script does the following (includes modes of operation for storage):
    1. initializes sets and parameters needed for the modeling of storage
    2. adds storage representation (pumped hydro or reservoir hydro, etc.) to
    an existing model (clones into a new model)

The input data should be provided through an Excel file (no hardcoded data
here in python)

"""
import pandas as pd
from itertools import product


# Initializing storage sets and parameters if needed
def init_storage(sc):
    sc.check_out()
    # 1) Adding sets
    idx = ['node', 'technology', 'mode', 'level', 'commodity', 'year', 'time']
    dict_set = {'storage_tec': None,
                'level_storage': None,
                'map_tec_storage': ['node', 'technology', 'mode',
                                    'storage_tec', 'mode',
                                    'level', 'commodity', 'lvl_temporal'],
                'is_relation_lower_time': ['relation', 'node', 'year', 'time'],
                'is_relation_upper_time': ['relation', 'node', 'year', 'time'],
                 }
    for item, idxs in dict_set.items():
        try:
            sc.init_set(item, idx_sets=idxs)
        except:
            if item == 'map_tec_storage':
                sc.remove_set(item)
                sc.init_set(item, idx_sets=idxs,
                            idx_names=['node', 'technology', 'mode',
                                       'storage_tec', 'mode_storage',
                                       'level', 'commodity', 'lvl_temporal'])
            else:
                pass
    # 2) Adding parameters
    
    dict_par = {'time_order':['lvl_temporal','time'],
                'storage_self_discharge': idx,
                'storage_initial': idx,
                 }

    for item, idxs in dict_par.items():
        try:
            sc.init_par(item, idx_sets=idxs)
        except:
            if "storage" in item:
                sc.remove_par(item)
                sc.init_par(item, idx_sets=idxs)
            else:
                pass

    sc.commit('')


# A function for adding storage technologies to an existing scenario
def add_storage(sc, setup_file, init_items=False, remove_ref=False):

    # 1) Initialization if needed
    if init_items:
        init_storage(sc)

    # 2) Adding required sets and parameters for storage technologies
    d1 = pd.ExcelFile(setup_file, engine="openpyxl").parse('storage')
    d1 = d1.loc[d1['active'] == 'yes']

    sc.check_out()

    # 2.1) Adding storage technologies and modes
    all_tecs = d1['technology'].dropna().tolist()
    sc.add_set('technology', all_tecs)
    sc.add_set('mode', list(set(d1['mode'].dropna())))
    df = d1.set_index(['technology', 'mode']).sort_index()
    d2 = d1.set_index(['technology', 'mode', 'lvl_temporal']).sort_index()

    # 2.2) Adding missing commodities and levels
    for par, column in product(['input', 'output'], ['commodity', 'level']):
        item_list = df[par + '_' + column].dropna().tolist()
        for item in item_list:
            sc.add_set(column, item.split('/'))

    # 2.3) Adding storage to set technology and level_storage
    d_stor = df.loc[df['storage_tec'] == 'yes']
    storage_tecs = [x[0] for x in d_stor.index]
    sc.add_set('storage_tec', storage_tecs)

    storage_lvls = d_stor['input_level'].tolist()
    sc.add_set('level_storage', storage_lvls)

    # 2.4) Adding mapping of charger-discharger technologies to their storage
    for i in d_stor.index:
        if d_stor['node_loc'][i] != 'all':
            nodes = d_stor['node_loc'][i].split('/')
        else:
            node_exclude = d_stor['node_exclude'][i].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
                    
        # Código ativo para colocar tecnologias de armazenamento sazonais

            #tec = i[0]
            #mode = i[1]
            #stor_tech = df.loc[df['storage_tec'] == tec + "," + mode].index
            
            #for (t, mode_t), node in product(stor_tech, nodes):
                #sc.add_set('map_tec_storage', [node, tec, mode, t, mode_t,
                                              #df.loc[(t, mode_t), "input_level"],
                                              #df.loc[(t, mode_t), "input_commodity"],
                                              #df.loc[(t, mode_t), 'lvl_temporal'],
                                                  #])
    
        # 3) Parameter "time_order" for the order of time slices in each level
        parname = 'time_order'
        df2 = pd.DataFrame(index=[0], columns=['lvl_temporal', 'time',
                                              'value', 'unit'])
        ti_map = sc.set('map_temporal_hierarchy')
        times = ti_map.loc[ti_map['lvl_temporal'] == d_stor['lvl_temporal'][i],
                          'time'].tolist()
        # Adding order of times
        for ti in range(len(times)):
            d = df2.copy()
            d['time'] = times[ti]
            d['value'] = ti + 1
            d['lvl_temporal'] = d_stor['lvl_temporal'][i]
            d['unit'] = '-'
            sc.add_par(parname, d)

    print('- Storage sets and mappings added.')

    # 4) Parametrization of storage technologies
    try:
        model_yrs = [int(x) for x in sc.set('year') if int(x) >= sc.firstmodelyear]
    except:
        model_yrs = sc.set('year').to_list()
    
    removal = []
    d2 = d2[~d2.index.duplicated(keep='first')].copy()
    for i in d2.index:
        # Reference technology
        tec_ref = d2.loc[i, 'tec_from']
        
        # Time slices (relevant to this technology)
        times = ti_map.loc[ti_map['lvl_temporal'] == i[2],
                          'time'].tolist()
        
        # Nodes
        if d2.loc[i, 'node_loc'] == 'all':
            node_exclude = d2.loc[i, 'node_exclude'].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
            nodes_ref = nodes
        else:
            nodes = d2.loc[i, 'node_loc'].split('/')
            nodes_ref = d2.loc[i, 'node_from'].split('/')

        # 2.4) Adding mapping of charger-discharger technologies to their storage
        # Código ativo para colocar tecnologias de armazenamento anuais
        if not d2.loc[i, "storage_tec"] == "yes":    
            
            tec = i[0]
            mode = i[1]
            stor_tech = [x.split(",") for x in d2.loc[i, "storage_tec_2"].split("/")]
            
            for (t, mode_t, lvl_t), node in product(stor_tech, nodes):
                sc.add_set('map_tec_storage', [node, tec, mode, t, mode_t,
                                              d2.loc[(t, mode_t, lvl_t), "input_level"],
                                              d2.loc[(t, mode_t, lvl_t), "input_commodity"],
                                              lvl_t
                                                  ])
        
        # 4.1) Adding input and output of storage reservoir technology
        for par in ['input', 'output']:
            df_ref = sc.par(par, {'technology': tec_ref, 'node_loc': nodes})

            # if empty finds another technology with the same lifetime
            n = 0
            while df_ref.empty:
                df_lt = sc.par('technical_lifetime', {'node_loc': nodes})
                lt = float(df_lt.loc[df_lt['technology'] == tec_ref
                                     ]['value'].mode())
                tec_lt = list(set(df_lt.loc[df_lt['value'] == lt
                                           ]['technology']))[n]
                n = n + 1
                df_ref = sc.par(par, {'technology': tec_lt, 'node_loc': nodes})
            
            # Slicing for timeslices relevant to this technology
            df_new = df_ref.loc[df_ref["time"].isin(times)].copy()
            
            # Updating technology and mode
            df_new['technology'] = i[0]
            df_new['mode'] = i[1]
            
            # Ensuring "time" and "time_origin"/"time_dest" match
            time_col = [x for x in sc.idx_names(par) if "time_" in x][0]
            df_new[time_col] = df_new["time"]
            
            # Making sure node_dest/node_origin are the same as node_loc
            node_col = [x for x in sc.idx_names(par) if
                        'node' in x and x != 'node_loc'][0]
            df_new[node_col] = df_new['node_loc']
            
            com_list = d2.loc[i, par + '_commodity']
            if not pd.isna(com_list):
                for num, com in enumerate(com_list.split('/')):
                    lvl = d2.loc[i, par + '_level'].split('/')[num]
                    df_new['commodity'] = com
                    df_new['level'] = lvl
                    df_new['value'] = float(str(d2.loc[i, par + '_value']
                                                ).split('/')[num])
                    sc.add_par(par, df_new)
        print('- Storage "input" and "output" parameters',
              'configured for "{}".'.format(i))

        # 4.2) Adding storage reservoir parameters
        if i[0] in storage_tecs:
            par_list = ['storage_self_discharge', 'storage_initial']
            
            for parname in par_list:
                cols = sc.idx_names(parname) + ['unit', 'value']
                d = pd.DataFrame(index=product(model_yrs, times),
                                 columns=cols)
                d['technology'] = i[0]
                d['year'] = [y[0] for y in d.index]
                d['time'] = [y[1] for y in d.index]
                d['mode'] = i[1]
                d['level'] = d2.loc[i, 'input_level']
                d['commodity'] = d2.loc[i, 'input_commodity']

                if parname == 'storage_initial':
                    slicer = [x for x in d.index if x[1] == times[0]]
                    d = d.loc[slicer, :]
                    d['value'] = d2.loc[i, parname]
                    d['unit'] = 'GWa'
                else:
                    d['value'] = d2.loc[i, parname]
                    d['unit'] = '-'

                for node in nodes:
                    d['node'] = node
                    d = d.reset_index(drop=True)
                    sc.add_par(parname, d)
            print('- Storage reservoir parameters added for {}'.format(i))

        # 4.3.1) Transferring historical data if needed
        if not pd.isna(d2.loc[i, 'historical']):
            tec_hist = d2.loc[i, 'historical']
            for parname in ['historical_activity', 'historical_new_capacity']:
                if "activity" in parname:
                    filters = {'technology': tec_hist,
                               'node_loc': nodes, "time": times}
                else:
                    filters = {'technology': tec_hist, 'node_loc': nodes}
                hist = sc.par(parname, filters)
                
                # Adding new data
                hist['technology'] = i[0]
                if "activity" in parname:
                    hist["mode"] = i[1]
                sc.add_par(parname, hist)
                removal = removal + [(parname, tec_hist, nodes)]

        # 4.3.2) Transferring relation activity and capacity
        if not pd.isna(d2.loc[i, 'tec_relation_from']):
            tec_rel = d2.loc[i, 'tec_relation_from']
            for parname in ["relation_total_capacity", 'relation_activity_time']:
                if not pd.isna(d2.loc[i, parname]):
                    relations = d2.loc[i, parname].split("/")
                    for r in relations:
                        rel = sc.par(parname, {'technology': tec_rel, 'node_rel': nodes,
                                           "relation": r.split(":")[0]})
                        if "activity" in parname:
                            rel = rel.loc[rel["time"].isin(times)].copy()
                            rel["mode"] = i[1]
                            #Multiplying value in the multiplier
                            rel["value"] *= float(r.split(":")[1])
            
                        #Adding new data
                        rel['technology'] = i[0]
                        sc.add_par(parname, rel)

        # 4.3) Adding all other parameters and changes in values specified in Excel
        # Excluding bound and relations
        par_excl = [x for x in sc.par_list() if any(y in x for y in [
            'bound_', 'historical_', 'relation_', 'ref_'])]
        par_excl = par_excl + ['input', 'output', 'emission_factor',
                               'storage_self_discharge', 'storage_initial']
         
        par_list = [x for x in sc.par_list() if "technology" in sc.idx_sets(x)
                    and x not in par_excl]
        
        for parname in par_list:
            # Loading existing data
            node_col = [x for x in sc.idx_names(parname) if 'node' in x][0]
            d = sc.par(parname, {node_col: nodes_ref, 'technology': tec_ref})
            
            # Checking if the value is directly from Excel or as a multiplier
            if parname in d2.columns:
                excl = d2.loc[i, parname]
                if excl.split(':')[0] == 'value':
                    d['value'] = float(excl.split(':')[1])
                elif excl.split(':')[0] == 'multiply':
                    d['value'] *= float(excl.split(':')[1])
                
            # Renaming technology, mode, and node names
            d['technology'] = i[0]
            if "mode" in sc.idx_sets(parname):
                d["mode"] = i[1]
            for node_r, node_n in zip(nodes_ref, nodes):
                d = d.replace({node_r: node_n})
            
            # Slicing correct timeslices
            if "time" in d.columns:
                d = d.loc[d["time"].isin(times)]
            
            # Adding the data back to the scenario
            sc.add_par(parname, d)
            
        print('- Data of "{}" copied to "{}"'.format(tec_ref, i[0]),
              'with possible updated values from Excel.')
    
    # Removing extra information after creating new storage technologies
    if remove_ref:
        for (parname, t, region) in removal:
            old = sc.par(parname, {'technology': t, 'node_loc': region})
            if not old.empty:
                sc.remove_par(parname, old)
                print('- Data of "{}" in parameter "{}"'.format(t, parname),
                      'was removed for {}'.format(region),
                      ', after introducing new storage technologies.')
    sc.commit('')
    print('- Storage parameterization done successfully for all technologies.')
    return d2.index.unique().to_list()


# Adding mapping sets of new parameters
def mapping_sets(sc, par_list=['relation_lower_time', 'relation_upper_time']):
    sc.check_out()
    for parname in par_list:
        setname = 'is_' + parname

        # initiating the sets
        idx_s = sc.idx_sets(parname)
        idx_n = sc.idx_names(parname)
        try:
            sc.set(setname)
        except:
            sc.init_set(setname, idx_sets=idx_s, idx_names=idx_n)
            print('- Set {} was initiated.'.format(setname))

        # emptying old data in sets
        df = sc.set(setname)
        sc.remove_set(setname, df)

        # adding data to the mapping sets
        df = sc.par(parname)
        if not df.empty:
            for i in df.index:
                d = df.loc[i, :].copy().drop(['value', 'unit'])
                sc.add_set(setname, d)

            print('- Mapping sets updated for "{}"'.format(setname))
    sc.commit('')


# %% Sample input data
if __name__ == "__main__":
    import message_ix
    import ixmp as ix
    import os
    from timeit import default_timer as timer
    from datetime import datetime
    from message_ix.utils import make_df

    
    # Use correct number of storages as in Excel
    num_storage = 12

    # Fill dict with the other dam's base capacities
    base_cap_dic = {
        "dam_hydro_1": 1738.9,
        "dam_hydro_2": 270.1,
        "dam_hydro_3": 925.0,
        "dam_hydro_4": 1236.1,
        "dam_hydro_5": 0,
        "dam_hydro_6": 89.9,
        "dam_hydro_7": 65.3,
        "dam_hydro_8": 12.7,
        "dam_hydro_9": 328.7,
        "dam_hydro_10": 3535.5,
        "dam_hydro_11": 273.4,
        "dam_hydro_12": 378.3,
    }
    
    #base_cap_grow = {
        #"dam_hydro_1": 0,
        #"dam_hydro_2": 0,
        #"dam_hydro_3": 0,
        #"dam_hydro_4": 0,
        #"dam_hydro_5": 0,
        #"dam_hydro_6": 0,
        #"dam_hydro_7": 0,
        #"dam_hydro_8": 0,
        #"dam_hydro_9": 0,
        #"dam_hydro_10": 0,
        #"dam_hydro_11": 0,
        #"dam_hydro_12": 0,
    #}
    # Dam's base capacities for historical_new_capacity
    base_cap_hist = {
        "dam_hydro_1": 173.89,
        "dam_hydro_2": 27.01,
        "dam_hydro_3": 92.50,
        "dam_hydro_4": 123.61,
        "dam_hydro_5": 0,
        "dam_hydro_6": 8.99,
        "dam_hydro_7": 6.53,
        "dam_hydro_8": 1.27,
        "dam_hydro_9": 32.87,
        "dam_hydro_10": 353.55,
        "dam_hydro_11": 27.34,
        "dam_hydro_12": 37.83,
    }

    # Capacidade dos resevetórios das reversíveis é 10% da capacidade dos reservatórios dos REEs
    # Fill dict with the other dam's base capacities
    sphs_dam_cap = {
        "dam_sphs_1": 173.9,
        "dam_sphs_2": 27.0,
        "dam_sphs_3": 92.5,
        "dam_sphs_4": 123.6,
        "dam_sphs_6": 9.0,
        "dam_sphs_7": 6.5,
        "dam_sphs_8": 1.3,
        "dam_sphs_9": 32.9,
        "dam_sphs_10": 353.6,
        "dam_sphs_11": 27.3,
        "dam_sphs_12": 37.8,
    }
    
    #sphs_dam_grow = {
        #"dam_sphs_1": 0,
        #"dam_sphs_2": 0,
        #"dam_sphs_3": 0,
        #"dam_sphs_4": 0,
        #"dam_sphs_6": 0,
        #"dam_sphs_7": 0,
        #"dam_sphs_8": 0,
        #"dam_sphs_9": 0,
        #"dam_sphs_10": 0,
        #"dam_sphs_11": 0,
        #"dam_sphs_12": 0,
    #}
    
    # the other dam's base capacities for historical_new_capacity
    sphs_dam_hist = {
        "dam_sphs_1": 17.39,
        "dam_sphs_2": 2.70,
        "dam_sphs_3": 9.25,
        "dam_sphs_4": 12.36,
        "dam_sphs_6": 0.90,
        "dam_sphs_7": 0.65,
        "dam_sphs_8": 0.13,
        "dam_sphs_9": 3.29,
        "dam_sphs_10": 35.36,
        "dam_sphs_11": 2.73,
        "dam_sphs_12": 3.78,
    }

    # Fill dict with the others
    water_com_dic = {"water_1": 313.43, 
                     "water_2": 215.40, 
                     "water_3": 150.70,
                     "water_4": 808.66,
                     #"water_5": 264.33,
                     "water_5": 1090.07,#somados os valores de demanda anual dos REEs 5, 10 e 12
                     "water_6": 182.67,
                     "water_7": 213.37,
                     "water_8": 636.48,
                     "water_9": 102.30,
                     "water_10": 0.0,
                     "water_11": 102.44,
                     "water_12": 0.0,
                     }

    # Add node_loc for other dams
    node_loc = {
        "node_loc_1": "Southeast",
        "node_loc_2": "South",
        "node_loc_3": "Northeast",
        "node_loc_4": "North",
        "node_loc_5": "Southeast",
        "node_loc_6": "Southeast",
        "node_loc_7": "Southeast",
        "node_loc_8": "North",
        "node_loc_9": "North",
        "node_loc_10": "Southeast",
        "node_loc_11": "South",
        "node_loc_12": "Southeast",
    }

    #sphs_cap_dic = {
        #"sphs_1": 0,
        #"sphs_2": 0,
        #"sphs_3": 0,
        #"sphs_4": 0,
        #"sphs_6": 0,
        #"sphs_7": 0,
        #"sphs_8": 0,
        #"sphs_9": 0,
        #"sphs_10": 0,
        #"sphs_11": 0,
        #"sphs_12": 0,
    #}
    
    pump_cap_dic = {
        "pump_sphs_1": 5,
        "pump_sphs_2": 5,
        "pump_sphs_3": 5,
        "pump_sphs_4": 5,
        "pump_sphs_6": 5,
        "pump_sphs_7": 5,
        "pump_sphs_8": 5,
        "pump_sphs_9": 5,
        "pump_sphs_10": 5,
        "pump_sphs_11": 5,
        "pump_sphs_12": 5,
    }
    
    # Testing storage setup
    path_files = (r'C:\Users\Fernando\Desktop\Modelo\finalmente\4. Storage technologies')
    os.chdir(path_files)

    mp = ix.Platform("default", jvmargs=['-Xms800m', '-Xmx8g'])
    
    # Reference scenario to clone from
    model = 'SIN Brasil expandido'
    scen_ref = 'water v.2'
    version_ref = 1
    
    # File name for the Excel file of input data
    filename = 'setup_storage_techs_teste v.12.xlsx'
    xls_files = path_files
    setup_file = xls_files + '\\' + filename
    
    solve = True         # if True, solving scenario at the end

    sc_ref = message_ix.Scenario(mp, model, scen_ref, version_ref)

    start = timer()
    sc = sc_ref.clone(model, 'storage v.2', keep_solution=False)

    # Add vintage and active years
    year_df = sc.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    # Parameterization of storage
    lvl_temporal = [x for x in sc.set('lvl_temporal') if x not in ['year']][0]
    # sc.discard_changes()
    tecs = add_storage(sc, setup_file, init_items=True)
    
    # Adding an unlimited source of water (this can be revisited or renamed)
    # For example, in the global model, there is water extraction level
    # This part can be specified later in Excel too.
    sc.check_out()
    #sc.add_set('technology', water_supply_tec)
    
    xls = pd.ExcelFile(setup_file, engine="openpyxl").parse()
    tec_charger = xls.loc[xls['section'] == 'charger', 'technology'].to_list()
    tec_discharger = xls.loc[xls['section'] == 'discharger',
                             'technology'].to_list()
    
    # Loop over the storages
    # Like the storage names, the loop should start with 1 and not with 0
    for storage in range(1, num_storage + 1):

        water_com = f"water_{storage}"
        water_supply_tec = f"river{storage}"

        # Add each water supply technology / river as set
        sc.add_set("technology", water_supply_tec)

        tec_water = [
             x
             for x in tec_charger
             if water_com in set(sc.par("input", {"technology": x})["commodity"])
        ]

        for tec in tec_water:
            df = sc.par("output", {"technology": tec})
            df["technology"] = f"water_supply_{storage}"
            df["level"] = list(
                set(
                    sc.par("input", {"technology": tec, "commodity": water_com})[
                        "level"
                        ]
                    )
            )[0]
            sc.add_par("output", df)
        
        # Adding a new unit to the library
        #mp.add_unit('m^3/s')
        
        discharge_time = 4
        
        num_subsistems = 4    

        while discharge_time < 5:
        
            for subsistems in range(1, num_subsistems + 1):

                base_cap_bat = {
                    f"stor_battery_{discharge_time}_1": 5,
                    f"stor_battery_{discharge_time}_2": 10,
                    f"stor_battery_{discharge_time}_3": 20,
                    f"stor_battery_{discharge_time}_4": 10,
                    }        

                node_loc_bat = {
                    "node_loc_1": "North",
                    "node_loc_2": "Northeast",
                    "node_loc_3": "Southeast",
                    "node_loc_4": "South",
                    }
                base_cap_battery = {
                    f"stor_battery_{discharge_time}_{subsistems}": base_cap_bat[f"stor_battery_{discharge_time}_{subsistems}"],
                    }

                base_bat_total_capacity_up = {
                    'year_act': [2030, 2040, 2050],
                    "time": "year",
                    "node_loc": node_loc_bat[f"node_loc_{subsistems}"],
                    "unit": "GW",
                    }
                             
                for tec, val in base_cap_battery.items():
                    df = make_df(base_bat_total_capacity_up, technology=tec, value=val)
                    sc.add_par("bound_total_capacity_up", df)
                
                stor_list = [f"stor_battery_{discharge_time}_{subsistems}"]
                stor_par = ["fix_cost"]
                for parname in stor_par:
                    df = sc.par(parname, {"technology": stor_list})
                    sc.remove_par(parname, df)
        
            discharge_time = discharge_time + 4 
        
        base_capacity = {
            "year_vtg": [2020],
            "time": "year",
            "node_loc": node_loc[f"node_loc_{storage}"],
            "unit": "m^3/s",
            }
        #base_capacity_growth = {
             #"year_vtg": [2020],
             #"time": "year",
             #"node_loc": node_loc[f"node_loc_{storage}"],
             #"unit": "-",
             #}

        base_cap = {
            f"dam_hydro_{storage}": base_cap_dic[f"dam_hydro_{storage}"],
            }
        
        base_hist = {
            f"dam_hydro_{storage}": base_cap_hist[f"dam_hydro_{storage}"],
            }
        
        #base_grow = {
             #f"dam_hydro_{storage}": base_cap_grow[f"dam_hydro_{storage}"],
             #}
        
        for tec, val in base_hist.items():
            df = make_df(base_capacity, technology=tec, value=val)
            sc.add_par("historical_new_capacity", df)


        base_total_capacity_up = {
            'year_act': [2030, 2040, 2050],
            "time": "year",
            "node_loc": node_loc[f"node_loc_{storage}"],
            "unit": "m^3/s",
            }
        
        base_ele_total_capacity_up = {
            'year_act': [2030, 2040, 2050],
            "time": "year",
            "node_loc": node_loc[f"node_loc_{storage}"],
            "unit": "GW",
            }                
                        
        for tec, val in base_cap.items():
            df = make_df(base_total_capacity_up, technology=tec, value=val)
            sc.add_par("bound_total_capacity_up", df)

        #for tec, val in base_grow.items():
             #df = make_df(base_capacity_growth, technology=tec, value=val)
             #sc.add_par("growth_new_capacity_up", df)

        if not storage == 5:
            #sphs_cap = {
                 #f"sphs_{storage}": sphs_cap_dic[f"sphs_{storage}"],
                 #}
            
            #dam_sphs_grow = {
                 #f"dam_sphs_{storage}": sphs_dam_grow[f"dam_sphs_{storage}"],
                 #}
            
            pump_cap = {
                 f"pump_sphs_{storage}": pump_cap_dic[f"pump_sphs_{storage}"],
                 }
            
            dam_sphs_cap = {
                 f"dam_sphs_{storage}": sphs_dam_cap[f"dam_sphs_{storage}"],
                 }
            
            dam_sphs_hist = {
                 f"dam_sphs_{storage}": sphs_dam_hist[f"dam_sphs_{storage}"],
                 }
            
            dam_act = [f"dam_sphs_{storage}"]
            dam_list = ['fix_cost']
            
            for parname in dam_list:
                 df = sc.par(parname, {"technology": dam_act})
                 df_new = df.copy()
                 df_new['value'] = float(0.001)
                 sc.remove_par(parname, df)
                 sc.add_par(parname, df_new)
            
            gas_act = ['gas_ppl','gas_ppl_ccs']
            gas_list = ['bound_total_capacity_up']
            
            for parname in gas_list:
                df = sc.par(parname, {"technology": gas_act})
                df_new = df.copy()
                df_new['value'] *= float(1.0)
                sc.remove_par(parname, df)
                sc.add_par(parname, df_new)
                
            gas_ccs_act = ['gas_ppl_ccs','gas_ppl_ccs_1','gas_ppl_ccs_2']
            gas_ccs_list = ['bound_total_capacity_up']
                
            for parname in gas_ccs_list:
                df = sc.par(parname, {"technology": gas_ccs_act})
                df_new = df.copy()
                df_new['value'] *= float(0.0)
                sc.remove_par(parname, df)
                sc.add_par(parname, df_new)
                 
            #for tec, val in sphs_cap.items():
                #df = make_df(base_ele_total_capacity_up, technology=tec, value=val)
                #sc.add_par("bound_total_capacity_up", df)
            
            for tec, val in pump_cap.items():
                df = make_df(base_ele_total_capacity_up, technology=tec, value=val)
                sc.add_par("bound_total_capacity_up", df)
            
            #for tec, val in dam_sphs_cap.items():
                #df = make_df(base_total_capacity_up, technology=tec, value=val)
                #sc.add_par("bound_total_capacity_up", df)
                
            for tec, val in dam_sphs_hist.items():
                df = make_df(base_capacity, technology=tec, value=val)
                sc.add_par("historical_new_capacity", df)

            #for tec, val in dam_sphs_grow.items():
                #df = make_df(base_capacity_growth, technology=tec, value=val)
                #sc.add_par("growth_new_capacity_up", df)
                
        # Add set balance equality
        sc.add_set("balance_equality", [f"water_{storage}", "primary"])

        # Modify list of technologies of non-necessary parameters from technologies
        tec_list = [
            f"river_dist_{storage}",
            f"river{storage}",
            f"water_supply_{storage}",
            ]
        # Modify list of non-necessary parameters from above technologies
        par_list = [
            "inv_cost",
            "fix_cost",
            #"capacity_factor",
            #"technical_lifetime",
            "historical_new_capacity",
            ]
        # Removing non-necessary parameters from technologies
        for parname in par_list:
            df = sc.par(parname, {"technology": tec_list})
            #df_new = df.copy()
            #df_new['value'] = float(0.001)
            sc.remove_par(parname, df)
            #sc.add_par(parname, df_new)
             
        tec_list_1 = [f"sphs_{storage}"]
        par_list_1 = ["inv_cost", "fix_cost", "capacity_factor", "technical_lifetime", 
                  "historical_new_capacity", "input", "output"]
         
        for parname in par_list_1:
            df = sc.par(parname, {"technology": tec_list_1})
            sc.remove_par(parname, df)

        # Remove fix cost of hydro storage
        #df = sc.par("inv_cost", {"technology": f"hydro_{storage}"})
        #sc.remove_par("inv_cost", df)
        
        # Remove fix and invest cost of hydro dam and dam sphs
        tec_list_hydro = [f"spill_hydro_{storage}"]
        tec_list_dam_hydro = [f"dam_hydro_{storage}"]
        
        par_list_hydro = ["fix_cost", "inv_cost"]
        par_list_dam_hydro = ["fix_cost"]
        for parname in par_list_hydro:
            df = sc.par(parname, {"technology": tec_list_hydro})
            #df_new = df.copy()
            #df_new['value'] = float(0.001)
            sc.remove_par(parname, df)
            #sc.add_par(parname, df_new)
        
        for parname in par_list_dam_hydro:
            df = sc.par(parname, {"technology": tec_list_dam_hydro})
            #df_new = df.copy()
            #df_new['value'] = float(0.001)
            sc.remove_par(parname, df)
            #sc.add_par(parname, df_new)
             
        # Remove data from old technologies
        tec_list_bat = ["batt_n", "batt_ne", "batt_se", "batt_s"]
        par_list_bat = ["inv_cost", "fix_cost", "capacity_factor", "technical_lifetime", 
                    "historical_new_capacity", "input", "output"]
        for parname in par_list_bat:
            df = sc.par(parname, {"technology": tec_list_bat})
            sc.remove_par(parname, df)
             
        # Add annual water demand
        # Annual demand is the sum of all seasonal demand
        water_com = {f"water_{storage}": water_com_dic[f"water_{storage}"]}

        # Loop over nodes
        for wat, val in water_com.items():
            demand_water = pd.DataFrame(
                {
                    "node": node_loc[f"node_loc_{storage}"],
                    "level": "final",
                    "year": [2030, 2040, 2050],
                    "time": "year",
                    "value": val,
                    "unit": "m^3/s",
                    }
                )

            demand_data = make_df(demand_water, commodity=wat)
            sc.add_par("demand", demand_data)
     
        #remove output
        water_tec = [f"water_supply_{storage}"]
        df = sc.par("output", {"technology": water_tec})
        # Remove old data
        sc.remove_par("output", df)
     
        # Change to year and add to the model
        df["time_dest"] = "year"
        sc.add_par("output", df)
     
        #remove output water supply
                 
        df = sc.par("output", {"technology": water_tec, "level": "primary"})
        # Remove old data
        sc.remove_par("output", df)
     
        #water_tec = [f"water_supply_{storage}"]
        #df = sc.par("demand", {"technology": water_tec, "level": "storage_hydro"})
        # Remove old data
        #sc.remove_par("demand", df)
        
        #df = sc.par("output", {"technology": water_tec, "level": "storage_sphs"})
        # Remove old data
        #sc.remove_par("output", df)

        # Remove input hydro
     
        df = sc.par("input", {"technology": f"hydro_{storage}", "level": "primary"})
        # Remove old data
        sc.remove_par("input", df)
        
        # Remove data from some commodities
        com_list_wat = ["water_10", "water_12"]
        par_list_wat = ["demand"]
        for parname in par_list_wat:
            df = sc.par(parname, {"commodity": com_list_wat})
            sc.remove_par(parname, df)
    
    # bound activities on solar technology at night
    
    time_bound = {'winter_1':0.,
                  'winter_6':0.,
                  'summer_1':0.,
                  'summer_6':0.}
    
    num_cont = 4
    
    for cont in range(1, num_cont + 1):
        
        for sea, val in time_bound.items():
            time_bound_data = pd.DataFrame(
                {
                        "node_loc": node_loc[f"node_loc_{cont}"],
                        "year_act": [2030, 2040, 2050],
                        "time": sea,
                        "mode":"M1",
                        "value": val,
                        "unit": "GWa",
                        }
                )
         
            solar_bound_act = make_df(time_bound_data, technology='solar_pv_ppl')
            sc.add_par("bound_activity_up", solar_bound_act)

    sc.commit('')

    # Updating mapping sets of relations
    mapping_sets(sc)

    end = timer()
    print('Elapsed time for adding storage setup:',
          int((end - start)/60),
          'min and', round((end - start) % 60, 2), 'sec.')

    # 5) Solving the model
    if solve:
        case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
        print('Solving scenario "{}" in "{}" mode, started at {}, please wait.'
              '..!'.format(case, 'MESSAGE', datetime.now().strftime('%H:%M:%S')))

        start = timer()
        sc.solve(model='MESSAGE', case=case, solve_options={'lpmethod': '4'})
        end = timer()
        print('Elapsed time for solving scenario:', int((end - start)/60),
              'min and', round((end - start) % 60, 2), 'sec.')
        sc.set_as_default()

    sc.to_excel('SIN expandido storage atualizado.xlsx')       
