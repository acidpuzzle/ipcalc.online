import re
from ipaddress import *

regex = re.compile(r"[\s\/%\\]+")


def _parse_input(user_string: str) -> tuple:
    return tuple(regex.split(user_string.strip()))


def _normalise_subnet_prefix(prefix: str) -> int:
    return int(prefix) if prefix.isdigit() else ip_network(f"0.0.0.0/{prefix}").prefixlen


def _get_doted_binary(address: bytes) -> str:
    return '{:08b}.{:08b}.{:08b}.{:08b}'.format(*list(address))


def _fill_network_type(target_address: IPv4Network | IPv6Network) -> str:
    if target_address.is_loopback:
        return "Loopback"
    elif target_address.is_unspecified:
        return "Unspecified"
    elif target_address.is_reserved:
        return "Reserved"
    elif target_address.is_multicast:
        return "Multicast"
    elif target_address.version == 6:
        if target_address.is_site_local:
            return "Site local"
    elif target_address.is_link_local:
        return "Link local"
    elif target_address.is_private:
        return "Private"
    elif target_address.is_global:
        return "Global"
    else:
        return " "


def _fill_v4_class(packed_address: bytes) -> str:
    bin_addr = _get_doted_binary(packed_address)
    if bin_addr.startswith('0'):
        return "Class A"
    elif bin_addr.startswith('10'):
        return "Class B"
    elif bin_addr.startswith('110'):
        return "Class C"
    elif bin_addr.startswith('1110'):
        return "Class D"
    elif bin_addr.startswith('1111'):
        return "Class E"


def _get_net_info(netw: IPv4Network | IPv6Network, addr: str = None) -> dict[str, str]:
    if netw.version == 4:
        # return dict for IPv4 prefixes
        if netw.prefixlen == 31 or netw.prefixlen == 32:
            host_min = netw.network_address
            host_max = netw.broadcast_address
            hosts = 0
        else:
            host_min = netw.network_address + 1
            host_max = netw.broadcast_address - 1
            hosts = netw.num_addresses - 2
        return {
            'version': f"IPv{netw.version}",
            'address_dd': addr if addr else "",
            'address_db': _get_doted_binary(IPv4Address(addr).packed) if addr else "",
            'address_type': _fill_network_type(IPv4Address(addr)) if addr else "",
            'network_dd': netw.__str__(),
            'network_db': _get_doted_binary(netw.network_address.packed),
            'preflen': netw.prefixlen,
            'netmask_dd': netw.netmask.__str__(),
            'netmask_db': _get_doted_binary(netw.netmask.packed),
            'wildcard_dd': netw.hostmask.__str__(),
            'wildcard_db': _get_doted_binary(netw.hostmask.packed),
            'hostmin_dd': host_min.__str__(),
            'hostmin_db': _get_doted_binary(host_min.packed),
            'hostmax_dd': host_max.__str__(),
            'hostmax_db': _get_doted_binary(host_max.packed),
            'broadcast_dd': netw.broadcast_address.__str__(),
            'broadcast_db': _get_doted_binary(netw.broadcast_address.packed),
            'hosts': hosts,
            'type': _fill_network_type(netw),
            'class': _fill_v4_class(netw.network_address.packed),
        }
    else:
        # return dict for IPv6 prefixes
        if netw.prefixlen == 127 or netw.prefixlen == 128:
            host_min = str(netw.network_address.exploded)
            host_max = str(netw.broadcast_address.exploded)
            hosts = 0
        else:
            host_min = str((netw.network_address + 1).exploded)
            host_max = str((netw.broadcast_address - 1).exploded)
            hosts = netw.num_addresses - 2
        return {
            'version': f"IPv{netw.version}",
            'address_hex': IPv6Address(addr).exploded.__str__() if addr else "",
            'address_type': _fill_network_type(IPv6Address(addr)) if addr else "",
            'netmask_hex': netw.netmask.exploded.__str__(),
            'preflen': netw.prefixlen,
            'wildcard_hex': netw.hostmask.exploded.__str__(),
            'network_hex': netw.exploded.__str__(),
            'broadcast_hex': netw.broadcast_address.exploded.__str__(),
            'hostmin_hex': host_min,
            'hostmax_hex': host_max,
            'hosts': hosts,
            'type': _fill_network_type(netw),
        }


def _find_subnets(netw: IPv4Network, sub_pfx: int | str) -> dict[str, [str, list]]:
    if sub_pfx - netw.prefixlen > 12:
        return {"sub_error": "Sorry, too many subnets, prefix difference cannot be more than 12"}
    else:
        return {"subnets": [_get_net_info(sub) for sub in netw.subnets(new_prefix=sub_pfx)]}


def calc_dispatcher(user_string: str) -> dict[str, str]:
    try:
        parsed_args = _parse_input(user_string)
        parsed_args_len = len(parsed_args)
        addr = parsed_args[0]
        mask = parsed_args[1] if parsed_args_len > 1 else "32"
        network = ip_network(f"{addr}/{mask}", strict=False)
        net_info = _get_net_info(network, addr)
        sub_info = {}
        if parsed_args_len >= 3:
            try:
                sub_pfx = _normalise_subnet_prefix(parsed_args[2])
                sub_info = _find_subnets(network, sub_pfx)
            except (ValueError, TypeError) as error:
                sub_info = {"sub_error": str(error)}
        return {**net_info, **sub_info}
    except (ValueError, TypeError) as error:
        return {"net_error": str(error)}
