# -*- coding: utf-8 -*-

# def DEMO_local_devices() :
#
#     ''' This is just a function that emulates the loading of the local devices config '''
#
#     local_devices = {}
#     local_devices['my_tunics'] = {'driver':'yenista_TUNICS','connection':'VISA','address':'ASRL6::INSTR'}
#     local_devices['my_power_meter'] = {'driver':'exfo_PM1613','connection':'VISA','address':'GPIB0::2::INSTR'}
#     local_devices['my_remote_PC'] = {'driver':'autolab_SERVER','connection':'VISA','address':'192.192.192.192'}
#     return local_devices


# from .core.devices import StructureManager, ElementWrapper

from . import config

elements = {}

def list_elements(parent_address='',level=None, type=None):

    temp_list = list(elements.keys())
    if parent_address != '' :
        assert parent_address in temp_list, f"Parent element '{parent_address}' doesn't exist."
        temp_list =  [a for a in elements.keys() if a.startswith(parent_address+'.')]
    if level is not None :
        temp_list = [a for a in temp_list if len(a.split('.')) == len(parent_address.split('.')) + level]
    if type is not None :
        assert type in [Device,Module,Variable,Action], f"Type '{type}' is not valid."
        temp_list = [a for a in temp_list if isinstance(a,type)]

    return temp_list

def add_element(address,element):
    assert address not in list_elements(), f"Element '{address}' already exists."
    elements[address] = element

def get_element(address) :
    assert address in list_elements(), f"Element '{address}' doesn't exist."
    return elements[address]

def remove_element(parent_address):
    for address in list_elements(parent_address=parent_address) :
        del elements[address]

def refresh_devices():

    # Load devices config
    config_file = config.load_config('DEVICES')

    # Updated devices config
    for device_name in [a for a in config_file.sections() if a in list_elements(level=0)]:
        if get_element(device_name).config != dict(config_file[device_name]):
            remove_device(device_name)
            create_device(device_name,config_file)

    # New devices config
    for device_name in [a for a in config_file.sections() if a not in list_elements(level=0)]:
        create_device(device_name,dict(config_file[device_name]))

    # Deleted devices config
    for device_name in [a for a in list_elements(level=0) if a not in config_file.sections()]:
        remove_device(device_name)

def remove_device(device_name) :
    get_element(device_name).disconnect()
    remove_element(device_name)

def create_device(device_name,config_file):
    device = Device(dict(config_file[device_name]))
    add_element(device_name, device)

class Device :

    def __init__(self,config):
        self.config = config
        self.driver_instance = None

    def connect(self, force_reconnect=False):

        """ Instantiate the associated Driver class with current configuration
        and load Device structure information """

        # Disconnect if required
        if self.driver_instance not None:
            if force_reconnect is True:
                self.disconnect()
            else:
                print(
                    "Device '{self.address}' already connected. Use option force_reconnect=True to reset the connection.")

        # Connection
        if self.is_connected() is False :
            self.driver_instance = 1

        # Loading of the elements
        pass

    def is_connected(self):
        return self.driver_instance is not None

    def disconnect(self):
        """ Try to close properly the connection to the instrument """
        try:
            self.driver_instance.close()
        except:
            pass
        self.driver_instance = None


class Module :

    def __init__(self,config):
        self.config = config


class Variable :

    def __init__(self,config):
        self.config = config

    def read(self):

        assert self.config['read_function'] is not None, \
            f"The Variable '{self._address}' of Device '{self._device._name}' is not writable"
        assert self.writable, f"The variable {self.name} is not writable"
        value = self.type(value)
        self.write_function(value)
        if self._write_signal is not None: self._write_signal.emit()

    def write(self, value):

        assert self._config['read_function'] is not None, \
            f"The Variable '{self._address}' of Device '{self._device._name}' is not readable"
        answer = self._config['read_function']()
        if self._config['read_signal'] is not None:
            self._config['read_signal'].emit(answer)
        return answer

    def __call__(self, value=None):

        """ Measure or set the value of the variable """
        if value None: return self.read()
        else: self.write(value)


class Action :

    def __init__(self,config):
        self.config = config

# Device class should have a status and a configurator function (that acts only if not connected)



# element[<device>::<module>::<variable>] = {'type':'variable', ...}


class DeviceManager():
    ''' This is the main class of the Devices part.
    It represents the top level device of the device structure,
    and as this, it inherits from the ElementWrapper class.
    The only difference is that its here that the StructureManager class
    of the session is instantiated, and that this "top level Device" is
    connected automatically '''

    def __init__(self):
        # For the top level device, instantiate the StructureManager class
        self._sm = StructureManager()

    def summary(self):
        self._sm.print_summary(None)

    # Routines to access sub elements
    def get(self, attr):
        return ElementWrapper(self._sm, attr)

    def __getattr__(self, attr):
        return self.get(attr)

    def __getitem__(self, attr):
        return self.get(attr)

    # Routines for autocompletion
    def __dir__(self):
        pass





class StructureManager():
    ''' This class is the internal interface used to interact with instruments.
    All communications of the current session pass through this class '''

    def __init__(self):
        # Init structure dictionnary
        self.structure = {}

        # Fill it by loading local devices params
        local_devices = DEMO_local_devices()
        for element_name in local_devices.keys():
            element_params = {}
            element_params['type'] = 'Device'
            element_params['connection_params'] = local_devices[element_name]
            self.set_element(None, element_name, element_params)

    def set_element(self, parent_element_address, child_element_name, child_element_params):
        # Here, an element is represented by a dictionnary containing
        # all its useful paramter (may be different parameters regarding the
        # type of the element). They are identified by their address 
        # (key of the dictionnary)
        if parent_element_address is not None:
            assert parent_element_address in self.structure.keys(), "Parent element {parent_element_address} doesn't exist."
            child_element_address = parent_element_address + '::' + child_element_name
        else:
            child_element_address = child_element_name
        assert child_element_address not in self.structure.keys(), "Element {child_element_address} already exists."
        self.structure[child_element_address] = child_element_params

    def get_child_element_address(self, parent_element_address, child_element_name):
        if parent_element_address is None:
            return child_element_name
        else:
            return parent_element_address + '::' + child_element_name

    def get_element(self, element_address):
        ''' Returns the parameters of the given Element '''
        assert element_address in self.structure.keys(), f"Element {element_address} doesn't exist"
        return self.structure[element_address]

    def get_child_elements(self, element_address):
        ''' Returns a dictionnary of all sub Elements of the given address '''
        if element_address is None:
            return dict(sorted(self.structure.items()))
        else:
            prefix = self.get_child_element_address(element_address, '')
            child_elements = {a: e for a, e in self.structure.items()
                              if a.startswith(prefix)}
            return dict(sorted(child_elements.items()))

    def print_summary(self, element_address):
        ''' Print the sub structure of the given element '''
        if element_address is None:
            self.print_sub_structure(element_address)
        else:
            element = self.get_element(element_address)
            first_line = f'{element["type"]} {element_address}'

            if element["type"] == 'Device':
                driver_name = element["connection_params"]["driver"]
                connection_status = self.get_connection_status(element_address)
                first_line += f' ({driver_name} - {connection_status})'
                print(first_line)
                self.print_sub_structure(element_address)
            elif element['type'] == 'Variable':
                print(first_line)
                if 'description' in element.keys(): print(f' - Description: {element["description"]}')
                if 'unit' in element.keys(): print(f' - Unit: {element["unit"]}')
                if 'get_method' in element.keys():
                    print(f' - Readable: YES ({element["get_method"]}')
                else:
                    print(' - Readable: NO')
                if 'set_method' in element.keys():
                    print(f' - Writable: YES ({element["set_method"]}')
                else:
                    print(' - Writable: NO')

    def print_sub_structure(self, element_address):
        child_elements = self.get_child_elements(element_address)
        prefix = self.get_child_element_address(element_address, '')
        if len(child_elements) > 0:
            tab_content = [['Sub-structure', 'Element type'], None]
            for (e, c) in child_elements.items():
                if prefix != '':
                    e = e.split(prefix)[1]
                if '::' in e:
                    e_split = e.split('::')
                    tab_content.append(['  ' * (len(e_split) - 1) + "|-- " + e_split[-1], c['type']])
                else:
                    tab_content.append([e, c['type']])
            tab_content.append(None)
            autolab.core.utilities.print_tab(tab_content)
        else:
            print('No sub-structure')

    def remove_child_elements(self, element_address):
        ''' Remove from the structure all sub element of the given one (not him) '''
        assert element_address is not None, 'You were about to remove all elements'
        child_elements = self.get_child_elements(element_address)
        for child_element in child_elements:
            sub_element_address = self.get_child_element_address(element_address, key)
            if self.structure[sub_element_address]['type'] == 'Device':
                try:
                    self.structure[sub_element_address]['instance'].disconnect()
                except:
                    pass
            del self.structure[sub_element_address]

    def connect_element(self, element_address, force_reconnect=False):
        ''' Try to connect this element, provided it's a Device '''
        element = self.get_element(element_address)
        if self.is_element_connected(element_address) and force_reconnect is False:
            print(
                f'Device {element_address} already connected.\nTo reset the connection, use the option force_reconnect=True.')
        else:
            assert element['type'] == 'Device', "Only Device elements elements of type Device can be connected"

            if 'connector' in element.keys():
                instance, device_structure = element['connector']()
            else:
                instance = autolab.drivers.get_driver_instance(element['connection_params'])
                device_structure = instance.get_device_structure()

            element['instance'] = instance
            # Mapping functions and elements
            for child_element in device_structure:
                self.set_element(element_address, child_element['name'], child_element)

    def is_element_connected(self, element_address):
        ''' Returns the connection status of an Element, provided it's a Device '''
        element = self.get_element(element_address)
        assert element['type'] == 'Device', "Only Device elements can be connected"
        return 'instance' in element.keys()

    def get_connection_status(self, element_address):
        ''' Returns the str version of the function is_element_connected '''
        if self.is_element_connected(element_address) is True:
            return 'Connected'
        else:
            return 'Not connected'

    def disconnect(self, element_address):
        ''' Try to disconnect this element, provided it's a Device '''
        element = self.get_element(element_address)
        assert element['type'] == 'Device', "Only Device elements can be disconnected"
        try:
            del element['instance']
        except:
            pass
        self._sm.remove_sub_elements(self.element_address)

    def is_valid_element_address(self, address):
        return address in self.structure.keys()

    def call(self, element_address, value):
        element = self.get_element(element_address)
        if element['type'] == 'Variable':
            if value is None:
                return element['get_method']()
            else:
                return element['set_method'](value)

