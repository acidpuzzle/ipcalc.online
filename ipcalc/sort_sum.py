from ipaddress import ip_network
from calculator import _parse_input


def get_sorted_nets(raw_input_from_web: str) -> tuple:
    user_nets = []
    errors = []
    raw_addrs = (_parse_input(line.strip()) for line in raw_input_from_web.splitlines() if line)
    for raw_addr in raw_addrs:
        try:
            if len(raw_addr) >= 2:
                user_nets.append(ip_network(f"{raw_addr[0]}/{raw_addr[1]}", strict=False))
            else:
                user_nets.append(ip_network(f"{raw_addr[0]}", strict=False))
        except ValueError as error:
            errors.append(error)

    user_nets = set(user_nets)  # remove duplicates
    user_nets = list(user_nets)
    user_nets.sort()

    return user_nets, errors


def get_out_form(nets: list, form) -> list:
    if form == "address":
        return [str(net.network_address) for net in nets]
    elif form == "address_prefix":
        return [str(net) for net in nets]
    elif form == "address_mask":
        return [f"{net.network_address} {net.netmask}" for net in nets]
    elif form == "address_wildcard":
        return [f"{net.network_address} {net.hostmask}" for net in nets]
    else:
        return [str(net) for net in nets]


def sum_nets(raw_input_from_web: str, dirty=0):
    sorted_nets, errors = get_sorted_nets(raw_input_from_web)

    current_index = 0
    while current_index < (len(sorted_nets) - 1):
        one = sorted_nets[current_index]
        two = sorted_nets[current_index + 1]

        if one.prefixlen != two.prefixlen:
            if one.supernet_of(two):
                sorted_nets.remove(two)
            elif two.supernet_of(one):
                sorted_nets.remove(one)
            else:
                current_index += 1
        else:
            if one.supernet().supernet_of(two):
                sorted_nets.remove(one)
                sorted_nets.remove(two)
                sorted_nets.append(one.supernet())
                sorted_nets.sort()
                if current_index != 0:
                    current_index -= 1
            else:
                current_index += 1

    return sorted_nets, errors
