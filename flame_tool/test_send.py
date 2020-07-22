from system_hotkey import SystemHotkey
hk = SystemHotkey()
hk.register(('control',  'h'), callback=lambda x: print("Easy!"))

while True:
    pass