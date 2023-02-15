import re
import logging
from ipaddress import *

logger = logging.getLogger(__name__)

regex = re.compile(r"[\s\/%\\]+")


def _normalise_input(user_input: str) -> tuple:
    return tuple(regex.split(user_input))


def _normalise_subnet_prefix(prefix: str) -> int:
    return int(prefix) if prefix.isdigit() else ip_network(f"0.0.0.0/{prefix}").prefixlen


def _get_doted_binary(address: bytes) -> str:
    return '{:08b}.{:08b}.{:08b}.{:08b}'.format(*list(address))
    # return [f'{val:08b}' for val in address]


def _fill_network_type(target_address) -> str:
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


def _fill_v4_class(packed_address: bytes):
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


def _fill_v4net_info(src_addr: str, src_net: IPv4Network) -> dict:
    try:
        if src_net.prefixlen == 31 or src_net.prefixlen == 32:
            host_min = src_net.network_address
            host_max = src_net.broadcast_address
            hosts = 0
        else:
            host_min = src_net.network_address + 1
            host_max = src_net.broadcast_address - 1
            hosts = src_net.num_addresses - 2
        return {
            'version': f"IPv{src_net.version}",
            'address_dd': src_addr,
            'address_db': _get_doted_binary(IPv4Address(src_addr).packed),
            'address_type': _fill_network_type(IPv4Address(src_addr)),
            'network_dd': src_net.__str__(),
            'network_db': _get_doted_binary(src_net.network_address.packed),
            'preflen': src_net.prefixlen,
            'netmask_dd': src_net.netmask.__str__(),
            'netmask_db': _get_doted_binary(src_net.netmask.packed),
            'wildcard_dd': src_net.hostmask.__str__(),
            'wildcard_db': _get_doted_binary(src_net.hostmask.packed),
            'hostmin_dd': host_min.__str__(),
            'hostmin_db': _get_doted_binary(host_min.packed),
            'hostmax_dd': host_max.__str__(),
            'hostmax_db': _get_doted_binary(host_max.packed),
            'broadcast_dd': src_net.broadcast_address.__str__(),
            'broadcast_db': _get_doted_binary(src_net.broadcast_address.packed),
            'hosts': hosts,
            'type': _fill_network_type(src_net),
            'class': _fill_v4_class(src_net.network_address.packed),
        }
    except ValueError as error:
        return {'Error': error}


def _fill_v6net_info(src_addr: str, src_net: IPv6Network) -> dict[str]:
    try:
        if src_net.prefixlen == 127 or src_net.prefixlen == 128:
            host_min = str(src_net.network_address.exploded)
            host_max = str(src_net.broadcast_address.exploded)
            hosts = 0
        else:
            host_min = str((src_net.network_address + 1).exploded)
            host_max = str((src_net.broadcast_address - 1).exploded)
            hosts = src_net.num_addresses - 2
        return {
            'version': f"IPv{src_net.version}",
            'address_hex': IPv6Address(src_addr).exploded.__str__(),
            'address_type': _fill_network_type(IPv6Address(src_addr)),
            'netmask_hex': src_net.netmask.exploded.__str__(),
            'preflen': src_net.prefixlen,
            'wildcard_hex': src_net.netmask.exploded.__str__(),
            'network_hex': src_net.exploded.__str__(),
            'broadcast_hex': src_net.broadcast_address.exploded.__str__(),
            'hostmin_hex': host_min,
            'hostmax_hex': host_max,
            'hosts': hosts,
            'type': _fill_network_type(src_net),
        }
    except ValueError as error:
        return {'Error': error}


def _fill_subnet_info(src_net: IPv4Network | IPv6Network, prfx: str):
    try:
        prfx = _normalise_subnet_prefix(prfx)
        if prfx - src_net.prefixlen > 12:
            return {'subnet_error': "Sorry, too many subnets, prefix difference cannot be more than 12."}
        if src_net.version == 4:
            try:
                logger.debug(f"{src_net}")
                subnet_list = (
                    _fill_v4net_info(str(subnet.network_address), subnet)
                    for subnet in src_net.subnets(new_prefix=int(prfx))
                )
                return {'subnet_list': subnet_list}
            except ValueError as error:
                return {'subnet_error': error}
        else:
            try:
                subnet_list = (
                    _fill_v6net_info(str(subnet.network_address), subnet)
                    for subnet in src_net.subnets(new_prefix=int(prfx))
                )
                return {'subnet_list': subnet_list}
            except ValueError as error:
                return {'subnet_error': error}
    except ValueError as error:
        logging.error(error)
        return {'subnet_error': error}


def calc_dispatcher(raw_request_string: str) -> dict[str]:
    try:
        network_string = ''
        subnets_mask = ''
        subnet_list = ''
        logger.debug(f"raw_request_string={raw_request_string}")
        network_list = _normalise_input(raw_request_string)
        logger.debug(f"network_list={network_list}")

        if len(network_list) == 1:
            network_string = f"{network_list[0]}/32"

        elif len(network_list) == 2:
            network_string = f"{network_list[0]}/{network_list[1]}"

        elif len(network_list) == 3:
            # if int(network_list[1]) >= int(network_list[2]):
            #     return {'calc_error': 'new prefix must be longer'}
            network_string = f"{network_list[0]}/{network_list[1]}"
            subnets_mask = network_list[2]

        elif len(network_list) > 3:
            return {'calc_error': 'more than 3 args'}

        ip_network_obj = ip_network(network_string, strict=False)
        if ip_network_obj.version == 4:
            network_info = _fill_v4net_info(network_list[0], ip_network_obj)
            if subnets_mask:
                subnet_list = _fill_subnet_info(ip_network_obj, subnets_mask)
                network_info = network_info | subnet_list
            return {**network_info}
        else:
            network_info = _fill_v6net_info(network_list[0], ip_network_obj)
            if subnets_mask:
                subnet_list = _fill_subnet_info(ip_network_obj, subnets_mask)
                network_info = network_info | subnet_list
            return {**network_info}
    except ValueError as err:
        logger.info(err)
        return {'calc_error': err}

