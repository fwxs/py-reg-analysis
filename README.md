# py-reg-analysis
A python set of tools to retrieve the following information:

* The previously connected networks.
* The previously attached usb devices.
* The users most recent opened files.
* A list of the processes executed by 'some' user.

# Modules
## networkList.py

Retrieve information of the last connected networks, querying the values from the 
*HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged* key. 
To read that key, you need to execute the script with *administrator* privileges.

### Syntax
**Note**: The script prints the date in the **UTC** format.

```
python networkList.py
[*] Network name: Default
  [+] Mac address: AA:BB:CC:DD:EE:FF
  [+] First date connection: 'Month Name', 'Year' 'Week day name'  HH:MM:SS:MMSS UTC
  [+] Last date connection: 'Month Name', 'Year' 'Week day name'  HH:MM:SS:MMSS UTC
```

## usbAttached.py

Retrieve information of the previously connected usb devices, querying the values of the keys stored in the 
*HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR* and the *HKLM\SYSTEM\CurrentControlSet\Control\DeviceClasses*.

### Syntax
**Note**: The extra information field, has information regarding if the device has a serial number or if the system created it.

```
python usbAttached.py
[*] Device name: 'Device name'      First attached date: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
  [+] Device friendly name: 'Device name'
  [+] Container ID: {aaaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeeee}

  [+] Class GUID: {aaaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeeee}
  [+] Disk ID: {aaaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeeee}
  
  [+] Device class GUID: {aaaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeeee}
  [+] Mfg: Manufacturer information.
  [+] Driver: {aaaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeeee}\xxxx
  [+] Extra information: 
```

## usersMRUList.py

Retrieve information of the Most Recent opened files by the specified user or by all the users.

### Syntax

```
python usersMRUList.py user_name
[*] Showing MRU docs of user 'user_name' -> id: 'user id'
  [+] Last modified date of the root key: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
  
  [+] Showing file for extension: '.ext'
  [!!] Files are shown from the most recent to the oldest one.
  [+] Last accessed date: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
    [+] File: file name
    ...
  ...
```

**Or**

```
python usersMRUList.py
[*] Showing MRU docs of user 'user_name' -> id: 'user id'
  [+] Last modified date of the root key: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
  
  [+] Showing file for extension: '.ext'
  [!!] Files are shown from the most recent to the oldest one.
  [+] Last accessed date: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
    [+] File: file name
    ...
  ...
...
```
## userLastPID.py

Retrieve information of the last processes executed by the specified user or by all users.


### Syntax

```
python userLastPID.py user_name
[*] Showing last executed processes of user 'user_name' -> id: 'user id'
[+] Last write time: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
[!!] Files are shown from the most recent to the oldest one.
    [+] Process name: file name
    ...
```

**Or**

```
python userLastPID.py user_name
[*] Showing last executed processes of user 'user_name' -> id: 'user id'
[+] Last write time: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
[!!] Files are shown from the most recent to the oldest one.
    [+] Process name: process name
    ...
...
```

**Note**: If '-v' is provided after the username or without it, it'll retrieve a sanitized raw version of the process key value.

```
python userLastPID.py user_name -v
[*] Showing last executed processes of user 'user_name' -> id: 'user id'
[+] Last write time: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
[!!] Files are shown from the most recent to the oldest one.
    [+] Process name: file name
        [-] Verbose data: 'data'
    ...
```

**Or**

```
python userLastPID.py -v
[*] Showing last executed processes of user 'user_name' -> id: 'user id'
[+] Last write time: 'Week day name' 'Month name' 'Month' HH:MM:SS 'Year' UTC
[!!] Files are shown from the most recent to the oldest one.
    [+] Process name: 'process name'
        [-] Verbose data: 'data'
    ...
...
```