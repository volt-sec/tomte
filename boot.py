''' 
tomte boot code

start wifi manager to allow connection to available wifi
'''
import sys

sys.path.append('extern/wifimanager')
print(sys.path)

import wifi_manager

wifi_mgr = wifi_manager.WifiManager("Tomte", "tomte1234")
wlan = wifi_mgr.get_connection()

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("tomte: connected")
