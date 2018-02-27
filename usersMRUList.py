import datetime
import sys
import time
import winreg as reg


__author__ = "pacmanator"
__email__ = "mrpacmanator@gmail.com"
__version__ = "v1.0"

"""
    Python script to print a list of the Most Recently Used docs by some user.
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


# Not readable characters to name a file or directory
NOT_READABLE_CHARS = [chr(character) for character in range(0, 32)]
NOT_READABLE_CHARS += [chr(character) for character in range(33, 40)]
NOT_READABLE_CHARS += ["*", ">", "<", "\"", ":", "?", "\\", "/", "|"]
NOT_READABLE_CHARS += ["^", "=", "@", "}", "{", ";", "[", "]", "+"]


def user2sid(user_name):
    """
        Returns the user id of the provided user name.
        @param user_id: The user name.
    """
    path = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList"

    # Opens the specified key path.
    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, path) as key:

        # Iterates through each sub key.
        for inx in range(reg.QueryInfoKey(key)[0]):
            
            key_name = reg.EnumKey(key, inx)

            # Retrieves information of the provided profile key.
            with reg.OpenKeyEx(key, key_name) as user_key:

                # Get the name of the user from its profileImagePath key value.
                profile_image_path = reg.QueryValueEx(user_key, "ProfileImagePath")[0]
                user_name_index = profile_image_path.rfind("\\") + 1

                # Return the user identification if it matches the provided user name
                if user_name.lower() in profile_image_path[user_name_index:].lower():
                    return key_name


def get_time(windows_time):
    """
        Converts a windows time to a UTC time.
        @param windows_time: 64-bits Windows timestamp.
    """
    time = datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=windows_time//10)
    return "{0} UTC".format(time.ctime())


def users_list():
    """ 
        Returns the sid of non-system users.
    """
    # A list of existing users.
    users = list()

    # Path to the users profile list HKEY.
    PATH = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList"

    # Open the users HKEY with the Profile list path as sub key.
    with reg.OpenKeyEx(reg.HKEY_LOCAL_MACHINE, PATH) as userList:

        # Obtain the amount of sub keys in the userList HKEY.
        numSubKeys = reg.QueryInfoKey(userList)[0]

        for user in range(0, numSubKeys):
            
            # Excludes the system accounts.
            if reg.EnumKey(userList, user).startswith("S-1-5-21"):
                users.append(reg.EnumKey(userList, user))
            else:
                continue

    return users


def remove_chars(key_value):
    """ This function removes the not readable characters and
        the not allowed files characters from a string.
    """
    filename = list()
    for byte in key_value:

        try:
            char = chr(byte).encode('utf-8')
            readable_char = chr(ord(char))

            if not (readable_char in NOT_READABLE_CHARS):
                filename.append(readable_char)
            else:
                continue

        # Some windows registry keys has a two-bytes value
        # this exception skips that encoding error.
        except TypeError:
            continue

    return "".join(filename)


def get_filename(filename, file_extension):
    """
        Returns the filename of the provided RecentDocs key value.
        @param filename: The name of the file.
        @param file_extension: The file extension.
    """
    # Index where the file extension begins.
    file_extension_inx = filename.lower().find(file_extension.lower())
    return filename[:file_extension_inx + len(file_extension)]


def parse_mru_inx(mru_list_ex):
    """
        Return an index of the most recently opened files.
        @param mru_list_ex: MRUListEx value.
    """
    # MRU files index.
    file_inx = list()

    # Iterates through the whole MRUListEx value in bytes chunks.
    for inx in range(0, len(mru_list_ex) - 4, 4):
        # Divides de MRUListEx into chunks of 4 bytes.
        chunk = mru_list_ex[inx:inx + 4]

        # Adds the hexadecimal values of the provided MRUListEx chunk.
        file_inx.append(sum([chunk[inx]  for inx in range(4)]))

    return file_inx


def get_recent_docs(key, file_extension):
    """
        Get the recently opened files, based on its file extension.
        @param key: Hive key.
        @param file_extension: The MRU file extension.
    """
    # Recent files.
    recent_docs = list()

    with reg.OpenKeyEx(key, file_extension) as file_extension_key:
        # MRU files indexes.
        mru_list_ex = reg.QueryValueEx(file_extension_key, "MRUListEx")[0]

        # Get the last time this key was modified.
        last_accessed_key_date = get_time(reg.QueryInfoKey(file_extension_key)[2])

        for file_index in parse_mru_inx(mru_list_ex):
            # I have no idea how to call this variable...
            mru_unit = reg.QueryValueEx(file_extension_key, str(file_index))[0]

            # Remove all unreadable characters from the filename.
            filename = get_filename(remove_chars(mru_unit), file_extension)
            recent_docs.append(filename)
    
        return recent_docs, last_accessed_key_date


def recent_docs(user_sid):
    """ This function prints the most recent documents used by a
        a registered user on the windows hive key.
    """
    # Recent documnent HKEY path of each user.
    mru_path = user_sid + "\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs"

    # Last modified date of the root key.
    root_last_modified_date = 0

    # Most recentrly used file extensions.
    files = dict()

    # If the user doesn't have the previous sub key, then it
    # has no history of 'Recent Opened' files.
    try:

        with reg.OpenKeyEx(reg.HKEY_USERS, mru_path) as mru_key:
            num_sub_keys = reg.QueryInfoKey(mru_key)[0]

            # Enumerates all the recent files extensions and saves them on a list.
            files_extensions = [reg.EnumKey(mru_key, ext) for ext in range(0, num_sub_keys)]
            root_last_modified_date = get_time(reg.QueryInfoKey(mru_key)[2])

            for file_extension in files_extensions:
                # Skip the folder subkey.
                if file_extension == "Folder":
                    continue

                files[file_extension] = get_recent_docs(mru_key, file_extension)

    except FileNotFoundError:
        pass

    return files, root_last_modified_date


def print_all_users_mru():
    for user_sid in users_list():

        mru_user_data = recent_docs(user_sid)

        if len(mru_user_data[0]) == 0:
            print("It seems that {0} doesn't have a 'most recent files' history.".format(user_sid))
            continue

        print("[*] Showing MRU docs for user {0}".format(user_sid))
        print("[+] Last modified date of the root key:", mru_user_data[1])

        for key, value in mru_user_data[0].items():
            files, last_accessed_date = value[0], value[1]

            print("\n\t[+] Showing files for extention: {0}".format(key))
            print("\t[!!] Files are shown from the most recent to the oldest one.")
            print("\t[+] Last accessed date: {0}".format(last_accessed_date))
            for file in files:
                print("\t\t[-] File:", file)


def print_single_user_mru(user_name):
    user_id = user2sid(user_name)

    if user_id is None:
        print("Error: User doesn't exists", file=sys.stderr)
        sys.exit()

    mru_user_data = recent_docs(user_id)

    if len(mru_user_data[0]) == 0:
        print("It seems that {0} doesn't have a 'most recent files' history.".format(user_id))
        sys.exit()

    print("[*] Showing MRU docs for user '{0}' -> id: {1}".format(user_name, user_id))
    print("[+] Last modified date of the root key:", mru_user_data[1])

    for key, value in mru_user_data[0].items():
        files, last_accessed_date = value[0], value[1]

        print("\n\t[+] Showing files for extention: {0}".format(key))
        print("\t[!!] Files are shown from the most recent to the oldest one.")
        print("\t[+] Last accessed date: {0}".format(last_accessed_date))

        for file in files:
            print("\t\t[-] File:", file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_all_users_mru()

    else:
        print_single_user_mru(sys.argv[1])