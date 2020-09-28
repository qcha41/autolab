# -*- coding: utf-8 -*-

import configparser
import os
import importlib
import inspect

from . import paths,utilities

drivers_infos = {}

def get_driver(driver_name,**conn_infos) :

    ''' Returns directly the instance of a driver '''

    driver_infos = DriverManager().get_driver_infos(driver_name)
    if 'version' in conn_infos.keys() : version = conn_infos['version']
    else : version = driver_infos.last_version()
    return driver_infos.get_release(version).connect(**conn_infos)




class DriverManager() :

    ''' User class interface to deal with drivers '''

    def __init__(self):
        if len(drivers_infos) == 0 : self.load_drivers_infos()


    def update_drivers(self):

        ''' Clone/Sync the official drivers repository locally and refresh drivers'''

        from . import repository
        repository.sync()
        self.load_drivers_infos()


    def load_drivers_infos(self):

        ''' Resets of the 'drivers' global variable.
        Loads the full structure of drivers folders. '''

        global drivers_infos
        drivers_infos = {}
        for source_path in [paths.DRIVERS_OFFICIAL,paths.DRIVERS_LOCAL]:
            for item in os.listdir(source_path) :
                try : infos = DriverInfos(os.path.join(source_path,item))
                except : infos = None
                if infos is not None and len(infos.list_versions())>0 :
                    assert infos.name not in drivers_infos.keys(), f'At least two drivers found with the same name {infos.name}.'
                    drivers_infos[infos.name] = infos


    def list_drivers(self):

        ''' Returns the list of all the drivers names '''

        return list(drivers_infos.keys())


    def list_categories(self):

        ''' Returns the list of unique drivers categories '''

        return list(set([drivers_infos[d].category for d in drivers_infos.keys()]))


    def help(self):

        ''' Displays in a pretty way the different available drivers and their information '''

        if len(self.list_drivers()) > 0 :
            
            content = [[drivers_infos[driver_name].category,driver_name,
                        drivers_infos[driver_name].last_version()] 
                        for driver_name in drivers_infos.keys()]
            content = sorted(content, key=lambda x: (x[0], x[1]))
            tab_content = [['Category','Driver name','Last version'],None]
            for i in range(len(content)) :
                if tab_content[-1] is None or tab_content[-1][0] != content[i][0] : 
                    tab_content.append(content[i])
                else : 
                    tab_content.append([''] + content[i][1:])
            utilities.print_tab(tab_content+[None])
                
        else : 
            print('No drivers yet, download them using the update_drivers() function.')



    def get_driver_infos(self,driver_name):

        ''' Returns the Driver object associated to the given driver_name '''

        assert driver_name in drivers_infos.keys(), f'Driver {driver_name} does not exist'
        return drivers_infos[driver_name]


    def __getattr__(self,attr):

        ''' Returns the Driver object associated to the given driver_name, using attribute access '''

        return self.get_driver_infos(attr)


    def __getitem__(self,attr):

        ''' Returns the Driver object associated to the given driver_name, using dictionnary access '''

        return self.get_driver_infos(attr)


    def __dir__(self):

        ''' Returns list of entry for the autocompletion '''

        return ['update_drivers','load_drivers_infos','help','get_driver_infos'] + self.list_drivers()




class DriverInfos():

    ''' This class represents a given driver, and its associated releases '''

    def __init__(self,path) :

        ''' At init, loads all the release informations about this Driver '''

        # Init
        self.name = ''
        self.category = ''
        self.manufacturer = ''
        self.model = ''
        self.docs_url = ''
        self.releases = {}

        # Path and name
        assert os.path.isdir(path)
        self._path = path
        self.name = os.path.basename(path)

        # Load driver infos
        driver_infos_path = os.path.join(path,'driver_infos.ini')
        if os.path.exists(driver_infos_path) :
            driver_infos = configparser.ConfigParser()
            driver_infos.read(driver_infos_path)
            if 'general' in driver_infos.sections() :
                driver_infos = driver_infos['general']
                for key in ['name','category','manufacturer','model','docs_url'] :
                    if key in driver_infos.keys() : 
                        setattr(self,key,driver_infos[key])

        # No versionning (only one version at root)
        if all(x in os.listdir(self._path) for x in ['driver.py', 'autolab_config.ini']) :
            release = Release(self,self._path)
            self.releases[release.version] = release

        # Load releases
        else :
            for item in os.listdir(self._path) :
                try : release = Release(self,os.path.join(self._path,item))
                except : release = None
                if release is not None :
                    assert release.version not in self.releases.keys()
                    self.releases[release.version] = release
       


    def list_versions(self):

        ''' Returns the list of all versions numbers available for this driver '''

        return list(self.releases.keys())


    def last_version(self):

        ''' Returns the last version number available for this driver '''

        return max(self.list_versions())


    def get_last_release(self):

        ''' Returns the instance of class Release associated with the last version available for this driver '''

        return self.get_release(self.last_version())


    def help(self):

        ''' Displays in a pretty way the available releases of this driver '''

        print(f" Driver {self.name}")
        if self.manufacturer != '' : print(f" Manufacturer: {self.manufacturer}")
        if self.model != '' : print(f" Instrument model(s): {self.model}")
        print('')
        tab_content = [['Releases versions (date)','Releases notes'],None]
        for version in sorted(self.releases.keys()) :
            tab_content.append([f'{version} ({self.releases[version].date})',self.releases[version].comments])
        tab_content.append(None)
        utilities.print_tab(tab_content)


    def get_release(self,version):

        ''' Returns the Release class instance associated with the given version '''

        assert version in self.releases.keys(), f"Version {version} of driver {self.name} does not exist"
        return self.releases[version]


    def __getitem__(self,attr):

        ''' Returns the Release class instance associated with the given version, through dictionnary access '''

        return self.get_release(attr)


    def __dir__(self):

        ''' Returns list of entry for the autocompletion '''

        return ['list_versions','last_version','last_release','get_release','get_last_release','help']



class Release():

    ''' This class represents a given release of a driver '''

    def __init__(self,driver_infos,path):

        ''' At init, loads release info '''

        # Init
        self.version = '0'
        self.date = '<no_date>'
        self.comments = ''
        
        self._driver_infos = driver_infos

        # Check required paths
        self._paths = {'main':path}
        self._paths['driver'] = os.path.join(self._paths['main'],'driver.py')
        self._paths['autolab_config'] = os.path.join(self._paths['main'],'autolab_config.ini')
        for p in self._paths.values() : assert os.path.exists(p)

        # Version
        if self._paths['main'] != self._driver_infos._path : 
            self.version = os.path.basename(self._paths['main'])

        # Load release infos
        release_infos_path = os.path.join(self._paths['main'],'release_infos.ini')
        if os.path.exists(release_infos_path) :
            release_infos = configparser.ConfigParser()
            release_infos.read(release_infos_path)
            if 'general' in release_infos.sections() :
                release_infos = release_infos['general']
                for key in ['comments','date'] :
                    if key in release_infos.keys() : setattr(self,key,release_infos[key])


    def connect(self,**connection_infos):

        ''' Returns an instance of the Driver_CONN class instantiated using connection_infos. '''

        connection_name = connection_infos.pop('connection')
        connection_class = DriverLibraryLoader(self._paths['driver']).get_connection_class(connection_name)
        return connection_class(connection_infos)


    def help(self, _print=True, _parser=False):

        ''' Displays in a pretty way informations about this release '''

        library = DriverLibraryLoader(self._paths['driver'])

        # Load list of all parameters
        params = {}
        params['driver'] = self._driver_infos.name
        params['connection'] = {}
        for connnection_name in library.get_connection_names() :
            params['connection'][connnection_name] = library.get_class_args('Driver_'+connnection_name)
        params['other'] = library.get_class_args('Driver')
        if hasattr(library.get_driver_class(),'slot_config') :
            params['other']['slot1'] = f'{library.get_driver_class().slot_config}'
            params['other']['slot1_name'] = 'my_<MODULE_NAME>'

        mess = '\n'

        # Name and category if available
        submess = [f'Driver "{self._driver_infos.name}" ({self._driver_infos.category})',
                   f'Release version: {self.version} ({self.date})']
        if self.comments != '' : submess.append(f'Release notes: {self.comments}')
        mess += utilities.emphasize(submess,sign='=') + '\n'

        # Connections types
        c_option=''
        if _parser: c_option='(-C option)'
        mess += f'\nAvailable connections types {c_option}:\n'
        for connection_name in params['connection'].keys() :
            mess += f' - {connection_name}\n'
        mess += '\n'

        # Modules
        if hasattr(library.get_driver_class(),'slot_config') :
            mess += 'Available modules:\n'
            for module_name in self.get_module_names() :
                mess += f' - {module_name}\n'
            mess += '\n'

        # Example of get_driver
        mess += '\n' + utilities.underline('Loading a Device manually (with arguments):') + '\n\n'
        for connection_name in params['connection'].keys() :
            if _parser is False :
                args_str = f"'{params['driver']}', connection='{connection_name}'"
                for arg,value in params['connection'][connection_name].items():
                    args_str += f", {arg}='{value}'"
                for arg,value in params['other'].items():
                    args_str += f", {arg}='{value}'"
                mess += f"   a = autolab.get_device({args_str})\n"
            else :
                args_str = f"-D {params['driver']} -C {connection_name} "
                for arg,value in params['connection'][connection_name].items():
                    if arg == 'address' : args_str += f"-A {value} "
                    if arg == 'port' : args_str += f"-P {value} "
                if len(params['other'])>0 : args_str += '-O '
                for arg,value in params['other'].items():
                    args_str += f"{arg}={value} "
                mess += f"   autolab device {args_str} \n"

        # Example of a devices_config.ini section
        mess += '\n\n' + utilities.underline('Saving a Device configuration in devices_config.ini:') + '\n'
        for connection_name in params['connection'].keys() :
            mess += f"\n   [my_{params['driver']}]\n"
            mess += f"   driver = {params['driver']}\n"
            mess += f"   connection = {connection_name}\n"
            for arg,value in params['connection'][connection_name].items():
                mess += f"   {arg} = {value}\n"
            for arg,value in params['other'].items():
                mess += f"   {arg} = {value}\n"

        # Example of get_driver_by_config
        mess += '\n\n' + utilities.underline('Loading a Device using a configuration in devices_config.ini:') + '\n\n'
        if _parser is False :
            mess += f"   a = autolab.get_device('my_{params['driver']}')"
        else :
            mess += f"   autolab device -D my_{params['driver']}\n"

        mess += "\n\nNote: provided arguments overwrite those found in devices_config.ini"

        if _print is True : print(mess)
        else : return mess




class DriverLibraryLoader() :

    ''' This class allow to load a driver library and inspect it / instantiate the driver '''

    def __init__(self,path):

        # Save current working directory path and go to driver's directory
        curr_dir = os.getcwd()
        os.chdir(os.path.dirname(path))

        # Load the module
        spec = importlib.util.spec_from_file_location('driver.py', path)
        self.driver_lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.driver_lib)

        # Come back to previous working directory
        os.chdir(curr_dir)


    def list_classes(self):

        ''' Returns the list of the all driver's library class '''

        return [name for name, obj in inspect.getmembers(self.driver_lib, inspect.isclass)
                     if obj.__module__ is self.driver_lib.__name__]


    def get_class_args(self,class_name):

        ''' Returns the dictionary of the optional arguments required by a class
        with their default values '''

        assert class_name in self.list_classes(), f'Class {class_name} does not exist'
        _class = getattr(self.driver_lib,class_name)
        signature = inspect.signature(_class)
        return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}


    def get_connection_names(self):

        ''' Returns the list of the driver's connection types (classes Driver_XXX) '''

        return [class_name.split('_')[1] for class_name in self.list_classes() if class_name.startswith('Driver_')]


    def get_module_names(self):

        ''' Returns the list of the driver's Module(s) name(s) (classes Module_XXX) '''

        return [class_name.split('_')[1] for class_name in self.list_classes() if class_name.startswith('Module_')]


    def get_driver_class(self):

        ''' Returns the class Driver of the provided driver library '''

        assert hasattr(self.driver_lib,'Driver'), f"Class Driver missing in driver {self.driver_lib.__name__}"
        assert inspect.isclass(self.driver_lib.Driver), f"Class Driver missing in driver {self.driver_lib.__name__}"
        return self.driver_lib.Driver


    def get_connection_class(self,connection_name):

        ''' Returns the class Driver_XXX of the provided driver library and connection type '''

        assert connection_name in self.get_connection_names(),f"Invalid connection type {connection_name} for driver {self.driver_lib.__name__}"
        return getattr(self.driver_lib,f'Driver_{connection_name}')


    def get_module_class(self,module_name):

        ''' Returns the class Module_XXX of the provided driver library and module_name'''

        assert module_name in self.get_module_names()
        return getattr(self.driver_lib,f'Module_{module_name}')




def explore_driver(instance,_print=True):

    ''' Displays the list of the methods available in this instance '''

    methods = get_instance_methods(instance)
    s = 'This instance contains the following functions:\n'
    for method in methods :
        s += f' - {method[0]}({",".join(method[1])})\n'

    if _print is True : print(s)
    else : return s

def get_instance_methods(instance):

    ''' Returns the list of all the methods (and their args) in that class '''

    methods = []

    # LEVEL 1
    for name,obj in inspect.getmembers(instance,inspect.ismethod) :
        if name != '__init__' :
            attr = getattr(instance,name)
            args = list(inspect.signature(attr).parameters.keys())
            methods.append([name,args])

    # LEVEL 2
    instance_vars = vars(instance)
    for key in instance_vars.keys():
        try :    # explicit to avoid visa and inspect.getmembers issue
            for name,obj in inspect.getmembers(instance_vars[key],inspect.ismethod):
                if inspect.getmembers(instance_vars[key],inspect.ismethod) != '__init__' and inspect.getmembers(instance_vars[key],inspect.ismethod) and name!='__init__':
                    attr = getattr(getattr(instance,key),name)
                    args = list(inspect.signature(attr).parameters.keys())
                    methods.append([f'{key}.{name}',args])
        except : pass

    return methods
