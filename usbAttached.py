import datetime
import winreg as reg


__author__ = "pacmanator"
__email__ = "mrpacmanator@gmail.com"
__version__ = "v1.0"

"""
    Python script to print a list of the previously attached usb drives.
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


def enum_usb():
    """
        Enumerates the USB drives stored on the registry.
    """
    usbstor = "SYSTEM\\CurrentControlSet\\Enum\\USBSTOR"

    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, usbstor) as usb_key:
        num_usb_devices = reg.QueryInfoKey(usb_key)[0]

        for device in range(0, num_usb_devices):
            key = reg.EnumKey(usb_key, device)

            with reg.OpenKeyEx(usb_key, key) as sub_key:
                for i in range(0, reg.QueryInfoKey(sub_key)[0]):

                    yield "{0}\\{1}\\{2}".format(usbstor, key, reg.EnumKey(sub_key, i))


def get_disk_id(key):
    """
        Get the diskId value of a usb device.
        @param key: An open registry key.

        @returns str: DiskId of the USB device.
    """
    with reg.OpenKeyEx(key, "Device Parameters\\Partmgr") as device_parameters_key:
        return reg.QueryValueEx(device_parameters_key, "DiskId")[0]


def get_device_class_guid(instance_id):
    """
        Get the USB device class guid.
        @param instance_id: The device instance id.
    """
    path = "SYSTEM\\CurrentControlSet\\Enum\\STORAGE\\Volume"

    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path) as key:
        for key_inx in range(reg.QueryInfoKey(key)[0]):
            key_name = reg.EnumKey(key, key_inx)

            if instance_id in key_name:
                # This is where the GUID begins.
                guid_inx = key_name.rfind("{")
                return key_name[guid_inx:]


def get_windows_time(windows_time):
    """
        Converts a windows time to a UTC time.
        @param windows_time: 64-bits Windows timestamp.
    """
    time = datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=windows_time//10)
    return "{0} UTC".format(time.ctime())


def get_first_attached_date(device_class_guid, instance_id):
    """
        Get the first time a USB drive was attached to the system.
        @param device_class_guid: The device guid.
        @param instance_id: Device serial number or instance id.
    """
    path = "SYSTEM\\CurrentControlSet\\Control\\DeviceClasses\\{0}".format(device_class_guid)

    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path) as key:
        # Iterate over the registry keys.
        for key_inx in range(reg.QueryInfoKey(key)[0]):
            key_name = reg.EnumKey(key, key_inx)

            if (device_class_guid in key_name) and (instance_id in key_name):
                # Open the device registry key.
                with reg.OpenKeyEx(key, key_name) as device_key:
                    # Store last accessed time.
                    windows_time = reg.QueryInfoKey(device_key)[2]
                    return get_windows_time(windows_time)


def get_device_name(instance_id):
    """
        Get the device name.
        @param instance_id: Instance id of the device.
    """
    path = "SOFTWARE\\Microsoft\\Windows Portable Devices\\Devices"
    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path) as key:
        for inx in range(reg.QueryInfoKey(key)[0]):
            key_name = reg.EnumKey(key, inx)

            if instance_id in key_name:
                with reg.OpenKeyEx(key, key_name) as sub_key:
                    return reg.QueryValueEx(sub_key, "FriendlyName")[0]
                

def prev_attached_usb():
    """
        Returns information about the previously connected
        usb drives.
    """
    for sub_key in enum_usb():
        # Additional information of the connected USB storage device.
        extra = list()

        with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, sub_key) as usb:
            instance_id_inx = sub_key.rfind("\\") + 1
            sys_gen_inx = sub_key.rfind("&")
            instance_id = sub_key[instance_id_inx:sys_gen_inx]

            if sys_gen_inx > 0:
                extra.append("Device doesn't have a serial number")
            
            # Names.
            friendly_name = reg.QueryValueEx(usb, "FriendlyName")[0]
            device_name = get_device_name(instance_id)

            # IDs.
            container_id = reg.QueryValueEx(usb, "ContainerID")[0]
            class_guid = reg.QueryValueEx(usb, "ClassGUID")[0]
            disk_id = get_disk_id(usb)
            device_class_guid = get_device_class_guid(instance_id)

            # Extras.
            mfg = reg.QueryValueEx(usb, "Mfg")[0]
            driver = reg.QueryValueEx(usb, "Driver")[0]
            windows_time = get_first_attached_date(device_class_guid, instance_id)

            yield device_name, windows_time, friendly_name, container_id,\
                  class_guid, disk_id, device_class_guid, mfg, driver, extra


if __name__ == "__main__":
    for info in prev_attached_usb():
        print("\n[*] Device name: {0} \tFirst date attached: {1}\n".format(info[0], info[1]))
        print("\t[+] Device friendly name: {0}".format(info[2]))
        print("\t[+] Container ID: {0}\n".format(info[3]))

        print("\t[+] Class GUID: {0}".format(info[4]))
        print("\t[+] Disk ID: {0}\n".format(info[5]))

        print("\t[+] Device class GUID: {0}".format(info[6]))
        print("\t[+] Mfg: {0}".format(info[7]))
        print("\t[+] Driver: {0}".format(info[8]))

        for extra_info in info[9]:
            print("\t[+] Extra information: {0}\n".format(extra_info))
