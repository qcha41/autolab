



def list() :
    return list(devices.keys())

def get(device_name) :
    assert device_name in devices.keys(), "Device '{device_name}' doesn't exist."
    return