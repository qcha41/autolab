# -*- coding: utf-8 -*-

import os
import csv
import configparser

        
def build_dict_from_parser(config_ini):
    
    ''' Returns a 2D dictionnary from a configparser '''
    
    config_dict = {}
    for config_ini_section in config_ini.sections() :
        config_dict[config_ini_section] = {}
        for config_ini_key in config_ini[config_ini_section].keys():
            config_dict[config_ini_section][config_ini_key] = config_ini[config_ini_section][config_ini_key]
    return config_dict

def build_parser_from_dict(config_dict):
    
    ''' Returns a configparser from a dictionnary '''
    
    config_ini = configparser.ConfigParser()
    for device in config_dict.keys():
        config_ini.add_section(device)
        for key in config_dict[device].keys():
            #if not pd.isna(config_dict[device][key]):
                config_ini[device][key] = str(config_dict[device][key])
    
    return config_ini


def write_dict_to_csv(input_dict,filename):
    
    ''' Take a dict as argument and write a it to a csv file '''
        
    assert isinstance(input_dict,dict)
    
    # Create another dict to add a first column with section/device names (key is '')
    dict_to_save = {}
    for i,k in input_dict.items():
        dict_to_save[i] = {}
        dict_to_save[i].update({'':i})
        dict_to_save[i].update(input_dict[i])
    
    # List all the nested keys (e.g. address, connection) => necessary to csv DictWriter
    list_inner_keys = []                  
    for key in dict_to_save.keys():               
        for key_in in dict_to_save[key].keys():                   
            if key_in not in list_inner_keys:                    
                list_inner_keys.append(key_in)
    
    # Write the 
    with open(filename, 'w') as csvfile:
        fieldnames = list_inner_keys
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in dict_to_save.keys():
            writer.writerow(dict_to_save[key])


def read_dict_from_csv(file_path):
    
    ''' Take the file_path to read csv from and returns a 2D dict '''
        
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        output_dict = {}
        for row in reader:
            for key,value in row.items():
                if key == '': # means section/device name
                    device = value.strip(' ') # space present at begining
                    output_dict[device] = {}
                else:
                    if value!= '': output_dict[device][key] = value
    
    return output_dict


def load_config_dict(config_path):
    
    ''' Load config ini file by default and returns 2D dict with keys for the different section names and values as dicts of all the sections found '''
    
    if config_path.endswith('.ini') and os.path.exists(config_path):   # if .ini
        # Load config parser
        config_ini = configparser.ConfigParser()
        config_ini.read(config_path)
        
        # Place config parser into a 2D dict
        config_dict = build_dict_from_parser(config_ini)
        
        return config_dict
        
    elif config_path.endswith('.csv') and os.path.exists(config_path):  # if .csv
        # Load csv file to dict
        config_dict = read_dict_from_csv(config_path)
        
        return config_dict
        
    else:
        # No config loaded
        pass
    
    

def convert_ini_to_csv(config_ini_path):
    
    ''' Take a path to the ini file as input argument and write at same location a xlsx file using pandas '''
    
    import csv
    import configparser
    
    assert os.path.exists(config_ini_path), f"File {os.path.basename(config_ini_path)} not found at path {os.path.dirname(config_ini_path)}"
    assert '.ini' in os.path.basename(config_ini_path), f'Formating error with file {os.path.dirname(config_ini_path)}, ".ini" must be the extension'
    
    # Load config parser
    config_ini = configparser.ConfigParser()
    config_ini.read(config_ini_path)

    # Place config parser into a 2D dict
    config_dict = build_dict_from_parser(config_ini)
    
    # Save dict to csv file
    new_filename = config_ini_path.strip('.ini')+'.csv'
    write_dict_to_csv(config_dict,new_filename)


def convert_csv_to_ini(config_csv_path):
    
    ''' Take a path to the ini file as input argument and write at same location a xlsx file using pandas '''
    
    import csv
    import configparser
    
    assert os.path.exists(config_csv_path), f"File {os.path.basename(config_csv_path)} not found at path {os.path.dirname(config_csv_path)}"
    assert '.csv' in os.path.basename(config_csv_path), f'Formating error with file {os.path.dirname(config_csv_path)}, ".csv" must be the extension'
    
    # Load config csv into 2D dict
    config_dict = read_dict_from_csv(config_csv_path)
    
    # Convert 2D dict to configparser
    config_ini  = build_parser_from_dict(config_dict)
    
    # Save configparser
    new_filename = config_csv_path.strip('.csv')+'.ini'
    with open(new_filename, 'w') as f:
        config_ini.write(f)


## xlsx files below

#def build_dict_from_dataframe(config_dataframe):
    
    #''' Returns a 2D dictionnary from a dataframe '''
    
    #config_dict = {}
    #dataframe_line_length = len(config_dataframe.T)
    #for index,config_dataframe_line in enumerate(config_dataframe.iloc[:,0]):  # all of first the column => devices
        #config_dict[config_dataframe_line] = {}
        #for dataframe_column in range(1,dataframe_line_length):
            #config_dict[config_dataframe_line][config_dataframe.keys()[dataframe_column]] = config_dataframe.iloc[index,dataframe_column]
    
    #return config_dict
    
#def convert_ini_to_xlsx(config_ini_path):
    
    #''' Take a path to the ini file as input argument and write at same location a xlsx file using pandas '''
    
    #import pandas as pd
    #import configparser
    
    #assert os.path.exists(config_ini_path), f"File {os.path.basename(config_ini_path)} not found at path {os.path.dirname(config_ini_path)}"
    #assert '.ini' in os.path.basename(config_ini_path), f'Formating error with file {os.path.dirname(config_ini_path)}, ".ini" must be the extension'
    
    ## Load config parser
    #config_ini = configparser.ConfigParser()
    #config_ini.read(config_ini_path)

    ## Place config parser into a 2D dict
    #config_dict = build_dict_from_parser(config_ini)
    
    ## Convert 2D dict to pd.Dataframe
    #config_data_frame = pd.DataFrame(config_dict).T
    
    ## Save pd.Dataframe
    #new_filename = config_ini_path.strip('.ini')+'.xlsx'
    #config_data_frame.to_excel(new_filename)

#def convert_xlsx_to_ini(config_dataframe_path):
    
    #''' Take a path to the xlsx file as input argument and write at same location a ini file using configparser '''
    
    #import pandas as pd
    #import configparser
    
    #assert os.path.exists(config_dataframe_path), f"File {os.path.basename(config_dataframe_path)} not found at path {os.path.dirname(config_dataframe_path)}"
    #assert '.xlsx' in os.path.basename(config_dataframe_path), f'Formating error with file {os.path.dirname(config_dataframe_path)}, ".xlsx" must be the extension'
    
    ## Load DataFrame
    #config_dataframe = pd.read_excel('/home/bruno/autolab/devices_config.xlsx')

    ## Place dataframe into a 2D dict
    #config_dict = build_dict_from_dataframe(config_dataframe)
    
    ## Convert 2D dict to configparser
    #config_ini  = build_parser_from_dict(config_dict)
    
    ## Save configparser
    #new_filename = config_dataframe_path.strip('.xlsx')+'.ini'
    #with open(new_filename, 'w') as f:
        #config_ini.write(f)



