import logging
import re
from ipaddress import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from ipcalc.ip_calc_app import application


# regex to split arguments
# regex = re.compile(r"[^\d.]+")
regex = re.compile(r"[\s\/%\\_]+")


def _parse_input(user_string: str) -> tuple:
    """
    Splits a string using a regular expression and returns a tuple with arguments
    :param user_string: user request
    :return: tuple with arguments
    """
    parsed_input = regex.split(user_string.strip().lower())
    if "mask" in parsed_input:
        parsed_input.remove("mask")
    return tuple(parsed_input)


def _normalise_subnet_prefix(prefix: str) -> int:
    """
    string with mask or prefix length
    :param prefix:
    :return: integer prefix length
    """
    return int(prefix) if prefix.isdigit() else ip_network(f"0.0.0.0/{prefix}").prefixlen


def _get_doted_binary(packed_address: bytes) -> str:
    """
    Converts the 4bit string of an ip address to a string with a binary representation of the address
    :param packed_address: bytes
    :return: str, example "10101100.00010000.00101100.00000001"
    """
    return '{:08b}.{:08b}.{:08b}.{:08b}'.format(*list(packed_address))


def _find_subnets(netw: IPv4Network, sub_pfx: int | str) -> dict[str, [str, list]]:
    """
    Creates a list with subnets and returns a dictionary
    :param netw: Supernet
    :param sub_pfx: prefix of subnets
    :return: dictionary with subnets
    """
    if sub_pfx - netw.prefixlen > 12:
        return {"sub_error": "Sorry, too many subnets, prefix difference cannot be more than 12 bit"}
    else:
        subnets = [_get_net_info(sub) for sub in netw.subnets(new_prefix=sub_pfx)]
        return {"num_subnets": len(subnets), "subnets": subnets}


def _fill_network_type(target_address: IPv4Network | IPv6Network | IPv4Address | IPv6Address) -> str:
    """
    Specifies the type of the passed address
    :param target_address: IPv4Network, IPv6Network, IPv4Address, IPv6Address object
    :return: Type of address
    """
    if target_address.is_loopback:
        return "Loopback"
    elif target_address.is_unspecified:
        return "Unspecified"
    elif target_address.is_reserved:
        return "Reserved"
    elif target_address.is_multicast:
        return "Multicast"
    elif target_address.version == 6 and target_address.is_site_local:
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
    """
    Specifies the class of the passed address
    :param packed_address: bytes
    :return: Class of address
    """
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
    """
    Create dictionary with address parameters to pass to the template
    :param netw: IPv4Network or IPv6Network object
    :param addr: string address
    :return: dictionary with address parameters
    """
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
            'address': addr if addr else "",
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
            'address': IPv6Address(addr).exploded.__str__() if addr else "",
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


def calc_dispatcher(user_string: str) -> dict[str, str]:
    """
    Main function dispatcher, processes arguments and returns dictionaries
    :param user_string: raw string from user request
    :return: Ready-made dictionary for substitution into a template
    """
    try:
        parsed_args = _parse_input(user_string)
        parsed_args_len = len(parsed_args)
        addr = parsed_args[0]
        network = ip_network(f"{addr}/{parsed_args[1]}", strict=False) if parsed_args_len > 1 else ip_network(f"{addr}")
        sub_info = {}
        if parsed_args_len >= 3:
            if int(parsed_args[1]) > int(parsed_args[2]):
                network = ip_network(f"{addr}/{parsed_args[2]}", strict=False)
                sub_pfx = _normalise_subnet_prefix(parsed_args[1])
            else:
                sub_pfx = _normalise_subnet_prefix(parsed_args[2])
            sub_info = _find_subnets(network, sub_pfx)
        net_info = _get_net_info(network, addr)
        return {**net_info, **sub_info}
    except (ValueError, TypeError) as error:
        return {"net_error": str(error)}
