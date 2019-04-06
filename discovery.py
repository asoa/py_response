#!/usr/bin/env python

from tkinter import *
import tkinter as tk
import netifaces
from functools import partial
from ipaddress import IPv4Network, ip_address, ip_network
from netaddr import IPAddress, IPNetwork
import concurrent.futures
import threading
import subprocess

# https://stackoverflow.com/questions/33677788/tkinter-grid-spacing-problems
# https://tkdocs.com/tutorial/grid.html#colsrows

# TODO: consider collapsing PingBar methods into the Discovery class
class Discovery:
    def __init__(self, root_window):
        self.root = root_window
        p = PingBar(self.root)
        p.get_networks()
        p.init_widgets()

class PingBar:
    def __init__(self, root_window):
        self.root_window = root_window
        self.ip_address = []
        self.ip = None
        self.mask = None

    def init_widgets(self):
        # ping bar frame
        frame = tk.Frame(self.root_window)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.grid_rowconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=2)
        network_label = tk.Label(frame, text='Network:')
        network_label.grid(row=0, column=0)

        # network option menu
        self.network_value = tk.StringVar()  # value holder for option menu
        self.network_value.trace_add('write', partial(self.set_start_end))
        network_option_menu = tk.OptionMenu(frame, self.network_value, *self.ip_address)
        network_option_menu.grid(row=0, column=1, sticky='w')

        ip_start_label = tk.Label(frame, text='IP Range Start:')
        ip_start_label.grid(row=0, column=2, sticky='w')

        self.ip_start_text_value = tk.StringVar()
        self.ip_start_text = tk.Entry(frame, textvariable=self.ip_start_text_value)
        self.ip_start_text.grid(row=0, column=3, sticky='w')


        ip_end_label = tk.Label(frame, text='IP Range End:')
        ip_end_label.grid(row=0, column=4, sticky='w')

        self.ip_end_text_value = tk.StringVar()
        self.ip_end_text = tk.Entry(frame, textvariable=self.ip_end_text_value)
        self.ip_end_text.grid(row=0, column=5, sticky='w')

        # button
        # self.scan_button = tk.Button(frame, text='Scan', command=self.Ping(self.ip, self.mask).theaded_ping)
        self.scan_button = tk.Button(frame, text='Scan', command=self.theaded_ping)
        self.scan_button.grid(row=0, column=6, sticky='w')

        # ping console
        self.console_text = Text(frame, fg="green", bg="black", state=NORMAL)
        self.console_text.grid(row=2, column=1, sticky='we', columnspan=5)

    def set_start_end(self, *args):
        """ initiated from partial function in network_value to set the start and end entry widgets """
        if len(self.network_value.get()) == 0:
            self.ip_start_text_value.set('')
            self.ip_end_text_value.set('')
            return
        (start, end) = IpInfo(self.ip, self.mask).get_first_last_ip()
        self.ip_start_text_value.set(start)
        self.ip_end_text_value.set(end)

    def get_networks(self):
        """ get the ips for each interface and instantiate a GetIpInfo object for each ip """
        interfaces = netifaces.interfaces()
        ips_objs = [netifaces.ifaddresses(interface) for interface in interfaces if
                    len(netifaces.ifaddresses(interface)) > 0]
        # iterates over each ip obj (ips_obj) and all of its addresses to get the ones with key '2'--routable ip--
        # and extracts the addr and netmask values
        self.ip_address = [IpInfo(v[0]['addr'],v[0]['netmask']).get_network_and_mask() for d in ips_objs for k, v in d.items() if
                           k == 2 and v[0]['addr'] != '127.0.0.1']
        # TODO: doesn't handle the case where there are more than one 'routable' interface
        self.ip = self.ip_address[0][0]
        self.mask = self.ip_address[0][1]
        self.ip_address.append('')

    def ping(self, ip):
        cmd = ['ping', '-c', '1', '-W', '1', ip]
        result = subprocess.call(cmd, stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        if result == 0:
            print(ip)
            return ip  # ping succeeded
        else:
            return False

    def theaded_ping(self):
        #TODO: create separate process for ping logic
        hosts = [str(x) for x in IpInfo(self.ip, self.mask).get_hosts()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.ping, hosts)
        live_hosts = [x for x in results if x is not False]
        # self.console_text.insert(END, live_hosts)
        # write to console
        [self.write_console(ip) for ip in live_hosts if ip is not False]
        # self.console_text.config(state=DISABLED)
        print('Done')

        # self.write_console('192.168.3.1')

    def write_console(self, ip):
        # self.console_text.config(state=NORMAL)
        self.console_text.insert(END, ip + '\n')


class IpInfo:
    """ gets network information (network, broadcast, cidr) for given ip and network mask """
    def __init__(self, ip, netmask):
        self.ip = ip
        self.netmask = netmask
        self.cidr = self.get_cidr()
        self.network = self.get_network()
        self.ip_obj = self.get_network()
        (self.first_ip, self.last_ip) = self.get_first_last_ip()

    def get_cidr(self):
        """ retunrs cidr i.e. /24 for a 255.255.255.0 mask """
        cidr = str(IPv4Network((0, self.netmask))).split('/')[1]
        return cidr

    def get_first_last_ip(self):
        """ returns the first and last useable ip of the range """
        ip = IPNetwork(str(self.ip) + '/' + self.cidr)
        first = str(ip.network + 1)
        last = str(ip.broadcast - 1)
        return (first, last)

    def get_network(self):
        """ returns the network and cidr (i.e 192.168.3.0/24) """
        ip = IPNetwork(str(self.ip) + '/' + self.cidr)
        return ip.network

    def get_network_and_mask(self):
        return (self.network,self.netmask)

    def get_ip_cidr(self):
        return IPNetwork(str(self.ip) + '/' + self.cidr)

    def get_hosts(self):
        return ip_network(str(self.ip) + '/' + self.cidr).hosts()


def main():
    ip = IpInfo('192.168.2.1', '255.255.255.0')
    print(ip.network)
    print(ip.cidr)
    print(ip.first_ip, ip.last_ip)


if __name__ == "__main__":
    main()