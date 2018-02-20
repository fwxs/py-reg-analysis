import sys
import utc
import winreg as reg

__author__ = "pacmanator"
__email__ = "mrpacmanator@gmail.com"
__version__ = "v1.1"

"""
    Python script to print a list of the previously connected networks.
    Copyright (C) 2018 pacmanator

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def decode_mac_address(encoded_mac_address):
    """ Returns a readable MAC Address. """
    return ":".join(["{:02x}".format(ch) for ch in encoded_mac_address])


def get_connected_dates(guid):
    """
        This function returns a readable UTC type time, specifying
        when was the last time that some network connection was used
        and the date when it was created.
        @param guid: Connection Guid.
    """
    path = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\Profiles\\{0}".format(guid)
    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path, 0, reg.KEY_READ) as key:
        last_connected_date = reg.QueryValueEx(key, "DateLastConnected")[0]
        first_connected_date = reg.QueryValueEx(key, "DateCreated")[0]

        return utc.get_utc(last_connected_date), utc.get_utc(first_connected_date)


def network_list():
    """
        Crawls the windows registry, to find a list of
        the previously connected networks.
    """
    path = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\Signatures\\Unmanaged"
    names = list()

    try:
        # Reads the HKLM with the specified path.
        with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path, 0, reg.KEY_READ) as key:

            # Get 'n' number of subkeys.
            for i in range(reg.QueryInfoKey(key)[0]):

                # Open the specified subkey.
                with reg.OpenKeyEx(key, reg.EnumKey(key, i), 0, reg.KEY_READ) as sub_key:

                    name = reg.QueryValueEx(sub_key, "Description")[0]

                    if name in names:
                        continue

                    guid = reg.QueryValueEx(sub_key, "ProfileGuid")[0]
                    mac_address = reg.QueryValueEx(sub_key, "DefaultGatewayMac")[0]

                    first_conx, last_conx = get_connected_dates(guid)

                    names.append(name)
                    mac_address = decode_mac_address(mac_address) if mac_address is not None else None

                    yield name, mac_address, first_conx, last_conx

    except PermissionError:
        print("You need to have admin privileges to open the network lists key")
        sys.exit(5)


if __name__ == '__main__':
    for value in network_list():
        print("[*] Network name: {0}".format(value[0]))
        print("\t[+] Mac address: {0}".format(value[1]))
        print("\t[+] First date connection: {0}".format(value[2]))
        print("\t[+] Last date connection: {0}\n".format(value[3]))
