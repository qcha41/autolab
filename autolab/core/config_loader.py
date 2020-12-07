# -*- coding: utf-8 -*-

import os
import configparser



#suffix = '.ini'
        
def build_dict_from_parser(config_ini):
    
    ''' Returns a 2D dictionnary from a configparser '''
    
    config_dict = {}
    for config_ini_section in config_ini.sections() :
        config_dict[config_ini_section] = {}
        for config_ini_key in config_ini[config_ini_section].keys():
            config_dict[config_ini_section][config_ini_key] = config_ini[config_ini_section][config_ini_key]
    return config_dict


def build_dict_from_dataframe(config_dataframe):
    
    ''' Returns a 2D dictionnary from a dataframe '''
    
    config_dict = {}
    dataframe_line_length = len(config_dataframe.T)
    for index,config_dataframe_line in enumerate(config_dataframe.iloc[:,0]):  # all of first the column => devices
        config_dict[config_dataframe_line] = {}
        for dataframe_column in range(1,dataframe_line_length):
            config_dict[config_dataframe_line][config_dataframe.keys()[dataframe_column]] = config_dataframe.iloc[index,dataframe_column]
    
    return config_dict


def build_parser_from_dict(config_dict):
    
    ''' Returns a configparser from a dictionnary '''
    
    import pandas as pd
    import configparser
    
    config_ini = configparser.ConfigParser()
    for device in config_dict.keys():
        config_ini.add_section(device)
        for key in config_dict[device].keys():
            if not pd.isna(config_dict[device][key]):
                config_ini[device][key] = str(config_dict[device][key])
    
    return config_ini

    
def convert_ini_to_dataframe(config_ini_path):
    
    ''' Take a path to the ini file as input argument and write at same location a xlsx file using pandas '''
    
    import pandas as pd
    import configparser
    
    assert os.path.exists(config_ini_path), f"File {os.path.basename(config_ini_path)} not found at path {os.path.dirname(config_ini_path)}"
    assert '.ini' in os.path.basename(config_ini_path), f'Formating error with file {os.path.dirname(config_ini_path)}, ".ini" must be the extension'
    
    # Load config parser
    config_ini = configparser.ConfigParser()
    config_ini.read(config_ini_path)

    # Place config parser into a 2D dict
    config_dict = build_dict_from_ini(config_ini)
    
    # Convert 2D dict to pd.Dataframe
    config_data_frame = pd.DataFrame(config_dict).T
    
    # Save pd.Dataframe
    new_filename = config_ini_path.strip('.ini')+'.xlsx'
    config_data_frame.to_excel(new_filename)


def convert_dataframe_to_ini(config_dataframe_path):
    
    ''' Take a path to the xlsx file as input argument and write at same location a ini file using configparser '''
    
    import pandas as pd
    import configparser
    
    assert os.path.exists(config_dataframe_path), f"File {os.path.basename(config_dataframe_path)} not found at path {os.path.dirname(config_dataframe_path)}"
    assert '.xlsx' in os.path.basename(config_dataframe_path), f'Formating error with file {os.path.dirname(config_dataframe_path)}, ".xlsx" must be the extension'
    
    # Load DataFrame
    config_dataframe = pd.read_excel('/home/bruno/autolab/devices_config.xlsx')

    # Place dataframe into a 2D dict
    config_dict = build_dict_from_dataframe(config_dataframe)
    
    # Convert 2D dict to configparser
    config_ini  = build_parser_from_dict(config_dict)
    
    # Save configparser
    new_filename = config_dataframe_path.strip('.xlsx')+'.ini'
    with open(new_filename, 'w') as f:
        config_ini.write(f)



