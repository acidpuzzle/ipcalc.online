import re
import logging
from ipaddress import *


logger = logging.getLogger(__name__)


regex = re.compile(r"[\s\/%\\]+")


def _normalise_input(user_input: str) -> tuple:
    return tuple(regex.split(user_input))


def get_doted_binary(address: bytes) -> str:
    return '{:08b}.{:08b}.{:08b}.{:08b}'.format(*list(address))


def _fill_network_type(target_address) -> str:
    if target_address.is_loopback:
        return "(Loopback)"
    elif target_address.is_unspecified:
        return "(Unspecified)"
    elif target_address.is_reserved:
        return "(Reserved)"
    elif target_address.is_multicast:
        return "(Multicast)"
    elif target_address.version == 6:
        if target_address.is_site_local:
            return "(Site local)"
    elif target_address.is_link_local:
        return "(Link local)"
    elif target_address.is_private:
        return "(Private)"
    elif target_address.is_global:
        return "(Global)"
    else:
        return " "


def _fill_v4net_info(sourse_address: str, sourse_network_obj: IPv4Network) -> dict:

    if sourse_network_obj.prefixlen == 31 or sourse_network_obj.prefixlen == 32:
        host_min = sourse_network_obj.network_address
        host_max = sourse_network_obj.broadcast_address
        addresses_hosts = f"{sourse_network_obj.num_addresses}/0"
    else:
        host_min = sourse_network_obj.network_address + 1
        host_max = sourse_network_obj.broadcast_address - 1
        addresses_hosts = f"{sourse_network_obj.num_addresses}/{sourse_network_obj.num_addresses - 2}"
    return {
        'Version': f"IPv{sourse_network_obj.version}",
        'Address_DD': sourse_address,
        'Address_DB': get_doted_binary(IPv4Address(sourse_address).packed),
        'Address_type': _fill_network_type(IPv4Address(sourse_address)),
        'Netmask_DD': f"{sourse_network_obj.netmask.__str__()} = {sourse_network_obj.prefixlen}",
        'Netmask_DB': get_doted_binary(sourse_network_obj.netmask.packed),
        'Wildcard_DD': sourse_network_obj.hostmask.__str__(),
        'Wildcard_DB': get_doted_binary(sourse_network_obj.hostmask.packed),
        'Network_DD': sourse_network_obj.__str__(),
        'Network_DB': get_doted_binary(sourse_network_obj.network_address.packed),
        'Broadcast_DD': sourse_network_obj.broadcast_address.__str__(),
        'Broadcast_DB': get_doted_binary(sourse_network_obj.broadcast_address.packed),
        'HostMin_DD': host_min.__str__(),
        'HostMin_DB': get_doted_binary(host_min.packed),
        'HostMax_DD': host_max.__str__(),
        'HostMax_DB': get_doted_binary(host_max.packed),
        'Addresses_Hosts': addresses_hosts,
        'Type': _fill_network_type(sourse_network_obj),
        'Class': "None",
    }


def _fill_subnet_info(sourse_network_obj: IPv4Network | IPv6Network, new_prefix: str):
    try:
        if sourse_network_obj.version == 4:
            logger.debug(f"{sourse_network_obj}")
            return (
                _fill_v4net_info(str(subnet.network_address), subnet)
                for subnet in sourse_network_obj.subnets(new_prefix=int(new_prefix))
            )
        else:
            return (
                _fill_v6net_info(str(subnet.network_address), subnet)
                for subnet in sourse_network_obj.subnets(new_prefix=int(new_prefix))
            )
    except ValueError as error:
        logging.error(error)


def _fill_v6net_info(sourse_address: str, sourse_network_obj: IPv6Network) -> dict[str]:
    if sourse_network_obj.prefixlen == 127 or sourse_network_obj.prefixlen == 128:
        host_min = str(sourse_network_obj.network_address.exploded)
        host_max = str(sourse_network_obj.broadcast_address.exploded)
        addresses_hosts = f"{sourse_network_obj.num_addresses}/0"
    else:
        host_min = str((sourse_network_obj.network_address + 1).exploded)
        host_max = str((sourse_network_obj.broadcast_address - 1).exploded)
        addresses_hosts = f"{sourse_network_obj.num_addresses}/{sourse_network_obj.num_addresses - 2}"
    return {
        'Version': f"IPv{sourse_network_obj.version}",
        'Address_hex': str(IPv6Address(sourse_address).exploded),
        'Address_type': _fill_network_type(IPv6Address(sourse_address)),
        'Netmask_hex': str(sourse_network_obj.netmask.exploded),
        'Wildcard_hex': str(sourse_network_obj.netmask.exploded),
        'Network_hex': str(sourse_network_obj.exploded),
        'Broadcast_hex': str(sourse_network_obj.broadcast_address.exploded),
        'HostMin_hex': host_min,
        'HostMax_hex': host_max,
        'Addresses_Hosts': addresses_hosts,
        'Type': _fill_network_type(sourse_network_obj),
    }


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
            return {'calc_error': '3 and more args'}

        ip_network_obj = ip_network(network_string, strict=False)
        if ip_network_obj.version == 4:
            network_info = _fill_v4net_info(network_list[0], ip_network_obj)
            if subnets_mask:
                subnet_list = _fill_subnet_info(ip_network_obj, subnets_mask)
            return {**network_info, 'subnet_list': subnet_list}
        else:
            network_info = _fill_v6net_info(network_list[0], ip_network_obj)
            if subnets_mask:
                subnet_list = _fill_subnet_info(ip_network_obj, subnets_mask)
            return {**network_info, 'subnet_list': subnet_list}
    except ValueError as err:
        logger.info(err)
        return {'calc_error': err}

