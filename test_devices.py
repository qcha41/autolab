from autolab.core import devices
devices.refresh_devices()
print(devices.list_devices())

my_device = devices.get_device('myDummy')
print(my_device.is_connected())
print(my_device._config)

my_device.wavelength