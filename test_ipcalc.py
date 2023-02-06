"""
=================================================================================
192.168.0.1/24
Address:   192.168.0.1           11000000.10101000.00000000 .00000001
Netmask:   255.255.255.0 = 24    11111111.11111111.11111111 .00000000
Wildcard:  0.0.0.255             00000000.00000000.00000000 .11111111
=>
Network:   192.168.0.0/24        11000000.10101000.00000000 .00000000 (Class C)
Broadcast: 192.168.0.255         11000000.10101000.00000000 .11111111
HostMin:   192.168.0.1           11000000.10101000.00000000 .00000001
HostMax:   192.168.0.254         11000000.10101000.00000000 .11111110
Hosts/Net: 254                   (Private Internet)
=================================================================================
192.168.0.1/24 /25
Address:   192.168.0.1           11000000.10101000.00000000 .00000001
Netmask:   255.255.255.0 = 24    11111111.11111111.11111111 .00000000
Wildcard:  0.0.0.255             00000000.00000000.00000000 .11111111
=>
Network:   192.168.0.0/24        11000000.10101000.00000000 .00000000 (Class C)
Broadcast: 192.168.0.255         11000000.10101000.00000000 .11111111
HostMin:   192.168.0.1           11000000.10101000.00000000 .00000001
HostMax:   192.168.0.254         11000000.10101000.00000000 .11111110
Hosts/Net: 254                   (Private Internet)


Subnets

Netmask:   255.255.255.128 = 25  11111111.11111111.11111111.1 0000000
Wildcard:  0.0.0.127             00000000.00000000.00000000.0 1111111

Network:   192.168.0.0/25        11000000.10101000.00000000.0 0000000 (Class C)
Broadcast: 192.168.0.127         11000000.10101000.00000000.0 1111111
HostMin:   192.168.0.1           11000000.10101000.00000000.0 0000001
HostMax:   192.168.0.126         11000000.10101000.00000000.0 1111110
Hosts/Net: 126                   (Private Internet)


Network:   192.168.0.128/25      11000000.10101000.00000000.1 0000000 (Class C)
Broadcast: 192.168.0.255         11000000.10101000.00000000.1 1111111
HostMin:   192.168.0.129         11000000.10101000.00000000.1 0000001
HostMax:   192.168.0.254         11000000.10101000.00000000.1 1111110
Hosts/Net: 126                   (Private Internet)



Subnets:   2
Hosts:     252
=================================================================================
"""
import re
from ipaddress import *


def get_doted_binary(address: bytes) -> str:
    return '{:08b}.{:08b}.{:08b}.{:08b}'.format(*list(address))


class CalcIPv4Address(IPv4Address):
    def __init__(self, address):
        super().__init__(address)

    @property
    def doted_binary(self):
        return get_doted_binary(self.packed)


class CalcIPv4Network(IPv4Network):


    def __init__(self, address):
        regex = re.compile(r"[\s\/%\\]+")
        address_list = regex.split(address)
        self._address_class = CalcIPv4Address
        self.input_addr = CalcIPv4Address(address_list[0])
        self.input_net = f"{address_list[0]}/{address_list[1]}"
        super().__init__(self.input_net, strict=False)
        if self.prefixlen == 31 or self.prefixlen == 32:
            self.host_min = self.network_address
            self.host_max = self.broadcast_address
            self.addresses_hosts = f"{self.num_addresses}/0"
        else:
            self.host_min = self.network_address + 1
            self.host_max = self.broadcast_address - 1
            self.addresses_hosts = f"{self.num_addresses}/{self.num_addresses - 2}"

    @property
    def _address_class(self):
        return CalcIPv4Address

    #     self.calc_dict = self.gen_calc_dict()
    #
    # def gen_calc_dict(self):
    #     return {
    #         'Version': f"IPv{self.version}",
    #         'Address_DD': self.input_addr.__str__(),
    #         'Address_DB': self.input_addr.doted_binary,
    #         'Address_type': None,
    #         'Netmask_DD': f"{str(self.netmask)} = {self.prefixlen}",
    #         'Netmask_DB': self.netmask.doted_binary,
    #         'Wildcard_DD': self.hostmask.__str__(),
    #         'Wildcard_DB': self.hostmask.doted_binary,
    #         'Network_DD': self.network_address.__str__(),
    #         'Network_DB': self.network_address.doted_binary,
    #         'Broadcast_DD': self.broadcast_address.__str__(),
    #         'Broadcast_DB': self.broadcast_address.doted_binary,
    #         'HostMin_DD': self.host_min.__str__(),
    #         'HostMin_DB': self.host_min.doted_binary,
    #         'HostMax_DD': self.host_max.__str__(),
    #         'HostMax_DB': self.host_max.doted_binary,
    #         'Addresses_Hosts': self.addresses_hosts,
    #         'Type': None,
    #         'Class': "None",
    #     }


if __name__ == "__main__":
    net = CalcIPv4Network("192.168.0.1/22")
    print(net.network_address.doted_binary)


    addr = CalcIPv4Address("192.168.0.1")
    print(addr.doted_binary)
