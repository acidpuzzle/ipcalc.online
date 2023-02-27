import os
import pytest
from pathlib import Path
from ipaddress import ip_address, ip_network

try:
    from ipcalc import *
except ImportError:
    ROOT_DIR = Path(__file__).resolve().parent.parent
    os.chdir(ROOT_DIR)
    from ipcalc import *


def test_parse_input():
    assert calculator._parse_input(' 192.168.0.0/12 ') == ("192.168.0.0", "12")
    assert calculator._parse_input(' 192.168.0.0 / 12 ') == ("192.168.0.0", "12")
    assert calculator._parse_input(' 192.168.0.0 12 ') == ("192.168.0.0", "12")
    assert calculator._parse_input(' 192.168.0.0_12 ') == ("192.168.0.0", "12")
    assert calculator._parse_input(' 192.168.0.0%12 ') == ("192.168.0.0", "12")


def test_normalise_subnet_prefix():
    assert calculator._normalise_subnet_prefix('24') == 24
    assert calculator._normalise_subnet_prefix('255.255.255.0') == 24


def test_get_doted_binary():
    assert calculator._get_doted_binary(ip_address("255.255.255.0").packed) == "11111111.11111111.11111111.00000000"
    assert calculator._get_doted_binary(ip_address("0.0.0.255").packed) == "00000000.00000000.00000000.11111111"


def test_fill_network_type():
    assert calculator._fill_network_type(ip_network("127.0.0.0/8")) == "Loopback"
    assert calculator._fill_network_type(ip_network("::1/128")) == "Loopback"
    assert calculator._fill_network_type(ip_address("0.0.0.0")) == "Unspecified"
    assert calculator._fill_network_type(ip_network("::0/128")) == "Unspecified"
    assert calculator._fill_network_type(ip_network("240.0.0.0/4")) == "Reserved"
    assert calculator._fill_network_type(ip_network("dead::/16")) == "Reserved"
    assert calculator._fill_network_type(ip_network("224.0.0.0/4")) == "Multicast"
    assert calculator._fill_network_type(ip_network("ff00::/8")) == "Multicast"
    assert calculator._fill_network_type(ip_network("169.254.0.0/16")) == "Link local"
    assert calculator._fill_network_type(ip_network("fe80::/64")) == "Link local"
    assert calculator._fill_network_type(ip_network("172.16.0.0/12")) == "Private"
    assert calculator._fill_network_type(ip_network("fc00::/7")) == "Private"
    assert calculator._fill_network_type(ip_address("8.8.8.8")) == "Global"
    assert calculator._fill_network_type(ip_network("2002::/16")) == "Global"
    assert calculator._fill_network_type(ip_network("FEC0::/10")) == "Site local"


def test_fill_v4_class():
    assert calculator._fill_v4_class(ip_address("10.0.0.0").packed) == "Class A"
    assert calculator._fill_v4_class(ip_address("172.16.0.0").packed) == "Class B"
    assert calculator._fill_v4_class(ip_address("192.168.0.0").packed) == "Class C"
    assert calculator._fill_v4_class(ip_address("224.0.0.0").packed) == "Class D"
    assert calculator._fill_v4_class(ip_address("240.0.0.0").packed) == "Class E"


@pytest.fixture
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    app.application.config['TESTING'] = True
    with app.application.test_client() as client:
        yield client


def test_hone(client):
    rv = client.get('/')
    assert (
               b'<!doctype html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <'
               b'meta name="viewport" content="width=device-width, initial-scale=1">\n    '
               b'<link href="/static/css/styles.css" rel="stylesheet">\n    <link rel="sho'
               b'rtcut icon" href="/static/img/favicon.svg" type="image/svg+xml">\n    <ti'
               b'tle> IP calculator</title>\n</head>\n<body>\n<section>\n    <div class="wrap'
               b'per">\n        <header class="page-header">\n            <ul>\n            '
               b'    <li class="inline"><a href="/">IP Calc</a></li>\n                <li '
               b'class="inline"><a href="/faq">FAQ</a></li>\n                <li class="in'
               b'line"><a href="/about">About</a></li>\n            </ul>\n            <hr>'
               b'\n        </header>\n        <main class="page-body">\n<h1>IP calculator</h'
               b'1>\n<form method="get">\n    <label for="network">\xd0\xa1opy and paste from'
               b' your network device config:</label>\n    <input id="network" type="text"'
               b' autofocus="autofocus" name="network" value="">\n    <input type="submit"'
               b' value="do it">\n</form></main>\n        <footer class="page-footer">\n    '
               b'        <hr>\n            <p>&copy; 2023 Pavlov Aleksey</p>\n            <'
               b'p>Powered by <a href="https://flask.palletsprojects.com/">Flask</a>\n    '
               b'        </p>\n        </footer>\n    </div>\n</section>\n</body>\n</html>'
           ) in rv.data


def test_faq(client):
    rv = client.get('/faq')
    assert (
               b'<!doctype html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <'
               b'meta name="viewport" content="width=device-width, initial-scale=1">\n    '
               b'<link href="/static/css/styles.css" rel="stylesheet">\n    <link rel="sho'
               b'rtcut icon" href="/static/img/favicon.svg" type="image/svg+xml">\n    <ti'
               b'tle>IP calculator FAQ</title>\n</head>\n<body>\n<section>\n    <div class="w'
               b'rapper">\n        <header class="page-header">\n            <ul>\n         '
               b'       <li class="inline"><a href="/">IP Calc</a></li>\n                <'
               b'li class="inline"><a href="/faq">FAQ</a></li>\n                <li class='
               b'"inline"><a href="/about">About</a></li>\n            </ul>\n            <'
               b'hr>\n        </header>\n        <main class="page-body">\n<h1>FAQ</h1>\n<p>I'
               b'P Calculator supports IPv4 and IPv6.\nJust copy the string with the addre'
               b'ss and mask from the network device config and paste it into the field.<'
               b'/p>\n<h2>Supported formats:</h2>\n<ul class="example">\n    <li><a href="/?'
               b'network=127.0.0.1">127.0.0.1</a></li>\n    <li><a href="/?network=192.168'
               b'.0.1%2F24">192.168.0.1/24</a></li>\n    <li><a href="/?network=172.16.44.'
               b'1+21">172.16.44.1 21</a></li>\n    <li><a href="/?network=192.168.0.1%2F2'
               b'55.255.255.252">192.168.0.1/255.255.255.252</a>\n    </li>\n    <li><a hre'
               b'f="/?network=10.0.0.0+%2F+12">10.0.0.0 / 12 </a></li>\n    <li><a href="/'
               b'?network=169.254.0.2+16">169.254.0.2 16</a></li>\n    <li><a href="/?netw'
               b'ork=192.168.24.0+0.0.1.255">192.168.24.0 0.0.1.255</a></li>\n    <li><a h'
               b'ref="/?network=192.168.255.1%2F24+%2F25">192.168.255.1/24 /25</a></li>\n '
               b'   <li><a href="/?network=fe80%3A%3Ae1b%3A4dc8%3Ac839%3Aa10%2520">fe80::e1b:'
               b'4dc8:c839:a10%20</a></li>\n    <li><a href="/?network=fe80%3A%3Ae1b%3A4dc'
               b'8%3Ac839%3Aa10%2F20">fe80::e1b:4dc8:c839:a10/20</a></li>\n    <li><a href'
               b'="/?network=fe80%3A%3Ae1b%3A4dc8%3Ac839%3Aa10%2F64+%2F66">fe80::e1b:4dc8:c83'
               b'9:a10/64 /66</a></li>\n    <li><a href="/?network=fffe%3A%3Ae1b%3A4dc8%3A'
               b'c839%3Aa10">fffe::e1b:4dc8:c839:a10</a></li>\n</ul>\n<h2>API:</h2>\n<ul cla'
               b'ss="example">\n    <li><a href="/api/192.168.0.1_24">https://ipcalc.onlin'
               b'e/api/192.168.0.1_24</a></li>\n    <li><a href="/api/192.168.0.1_24_25">h'
               b'ttps://ipcalc.online/api/192.168.0.1_24_25</a></li></ul>\n</ul>\n</main>\n '
               b'       <footer class="page-footer">\n            <hr>\n            <p>&cop'
               b'y; 2023 Pavlov Aleksey</p>\n            <p>Powered by <a href="https://fl'
               b'ask.palletsprojects.com/">Flask</a>\n            </p>\n        </footer>\n '
               b'   </div>\n</section>\n</body>\n</html>'
            ) in rv.data


def test_about(client):
    rv = client.get('/about')
    assert (
               b'<!doctype html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <'
               b'meta name="viewport" content="width=device-width, initial-scale=1">\n    '
               b'<link href="/static/css/styles.css" rel="stylesheet">\n    <link rel="sho'
               b'rtcut icon" href="/static/img/favicon.svg" type="image/svg+xml">\n    <ti'
               b'tle>About IP calculator</title>\n</head>\n<body>\n<section>\n    <div class='
               b'"wrapper">\n        <header class="page-header">\n            <ul>\n       '
               b'         <li class="inline"><a href="/">IP Calc</a></li>\n               '
               b' <li class="inline"><a href="/faq">FAQ</a></li>\n                <li clas'
               b's="inline"><a href="/about">About</a></li>\n            </ul>\n           '
               b' <hr>\n        </header>\n        <main class="page-body">\n<h1>About</h1>\n'
               b'<p>An IP calculator may be required for designing new networks, researching '
               b'and optimizing existing networks, and\n    dividing large networks into s'
               b'ubnets.</p>\n<p>This application was written by a network engineer,\n    i'
               b't does not use cookies and does not execute any scripts on the client side. '
               b'<br>\n    Enjoy using.</p>\n</main>\n        <footer class="page-footer">\n '
               b'           <hr>\n            <p>&copy; 2023 Pavlov Aleksey</p>\n          '
               b'  <p>Powered by <a href="https://flask.palletsprojects.com/">Flask</a>\n '
               b'           </p>\n        </footer>\n    </div>\n</section>\n</body>\n</ht'
               b'ml>'
           ) in rv.data


def test_api(client):
    rv = client.get('/api/192.168.0.0_24')
    assert (
               b'{"version":"IPv4","address":"192.168.0.0","address_db":"11000000.10101000.00'
               b'000000.00000000","address_type":"Private","network_dd":"192.168.0.0/24","net'
               b'work_db":"11000000.10101000.00000000.00000000","preflen":24,"netmask_dd":"25'
               b'5.255.255.0","netmask_db":"11111111.11111111.11111111.00000000","wildcard_dd'
               b'":"0.0.0.255","wildcard_db":"00000000.00000000.00000000.11111111","hostmin_d'
               b'd":"192.168.0.1","hostmin_db":"11000000.10101000.00000000.00000001","hostmax'
               b'_dd":"192.168.0.254","hostmax_db":"11000000.10101000.00000000.11111110","bro'
               b'adcast_dd":"192.168.0.255","broadcast_db":"11000000.10101000.00000000.111111'
               b'11","hosts":254,"type":"Private","class":"Class C"}\n'
           ) in rv.data


if __name__ == "__main__":
    pass

