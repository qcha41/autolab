
from .core import devices as _devices

def list_devices() :
    return _devices.list_elements(level=0)

def refresh() :
    return _devices.refresh_devices()


class ElementWrapper :

    def __init__(self, address):
        # The element wrapper receive the current StructureManager instance
        # from its parent element, plus the address of the represented Element
        self.address = address
        self._get_core_element()

    def _get_core_element(self):
        core_element = _devices.get_element(self.address)
        assert isinstance(core_element, _devices.Action)
        return core_element

    def get_sub_element(self, sub_address):
        """ Returns sub-element using its relative address """

        full_address = '.'.join([self.address, sub_address])
        sub_element_class = type(_devices.get_element(full_address)).__name__
        return globals()[sub_element_class](full_address)

    def __getattr__(self, attr):
        """ Returns sub-element using classes attributes """
        element = self._get_core_element()
        if hasattr(element,attr) : return element.attr
        else : return self.get(attr)

    def __getitem__(self, key):
        """ Returns sub-element using dictionary key access """
        return self.get(key)


class Device(ElementWrapper):
    """ User interface for Modules """

    def __init__(self, address):
        Element.__init__(self, address, _devices.Device)


class Module(ElementWrapper):
    """ User interface for Modules """

    def __init__(self, address):
        Element.__init__(self, address, _devices.Module)


class Variable(ElementWrapper):
    """ User interface for Variables """

    ddef __init__(self, address):
        Element.__init__(self, address, _devices.Variable)


class Action(ElementWrapper):
    """ User interface for Actions """

    def __init__(self, address):
        Element.__init__(self, address, _devices.Action)

