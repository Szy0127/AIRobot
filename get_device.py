import pyaudio

def getDeviceIndexByName(name):
    p = pyaudio.PyAudio()       
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device.get('name') == name:
            p.terminate()
            return i
    return -1

if __name__ == '__main__':
    indexi = getDeviceIndexByName('ac108')
    indexo = getDeviceIndexByName('sysdefault')
    print('input_index:',indexi,'output_index:',indexo)
