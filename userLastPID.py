import sys
import utils
import winreg as reg


__author__ = "pacmanator"
__email__ = "mrpacmanator@gmail.com"
__version__ = "v1.0"

"""
    Python script to print a list of the last processes executed by some user.
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


def get_process_name(proc_name):
    """
        Get the exe process.
        @param proc_name: Sanitized name of the process.
    """
    indexOfExe = proc_name.lower().find(".exe")

    if indexOfExe != -1:
        return proc_name[:indexOfExe + 4]
    else:
        return "{0} not an exe process.".format(proc_name)


def last_pid(user_sid, verbose):
    """
        This function returns the last visited process ID by
        some user.
        @param user_sid: User sid.
        @param verbose: Print raw information of the process.
    """
    path = "{0}\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion".format(user_sid)
    path += "\\Explorer\\ComDlg32\\LastVisitedPidlMRU"

    # Last time the key was modified.
    last_write_time = 0

    try:
        processes = list()
        with reg.OpenKeyEx(reg.HKEY_USERS, path, 0, reg.KEY_READ) as key:

            last_write_time = utils.get_time(reg.QueryInfoKey(key)[2])

            for mru_inx in utils.parse_mru_inx(reg.QueryValueEx(key, "MRUListEx")[0]):
                # Remove not readable chars from the registry value.

                if verbose:
                    process_data = utils.remove_chars(reg.QueryValueEx(key, str(mru_inx))[0])
                    process_name = get_process_name(process_data)
                    processes.append("{0}\n\t\t[-]Verbose data: {1}\n".format(process_name, process_data))
                else:
                    process_data = utils.remove_chars(reg.QueryValueEx(key, str(mru_inx))[0])
                    processes.append(get_process_name(process_data))

    except FileNotFoundError:
        pass

    return last_write_time, processes


def print_all_users_lpids(verbose):
    for user_sid in utils.users_list():
        processes_info = last_pid(user_sid, verbose=verbose)

        if len(processes_info[1]) == 0:
            print("[!!] Looks like user {0} doesn't have a last PID list.\n".format(user_sid))
            continue

        print("\n[*] Showing processes for user {0}.".format(user_sid))
        print("[*] Last write time: {0}".format( processes_info[0]))
        print("[!!] Process are shown from most recent to the older one.\n")

        newline_countdown = 1
        for process in processes_info[1]:
            print("\t[*] Process info:", process)

            if newline_countdown == 3:
                print()
                newline_countdown = 0
            
            newline_countdown += 1


def print_single_user_lpd(user_name, verbose):

    user_id = utils.user2sid(user_name)

    if user_id is None:
        print("Error: User doesn't exists", file=sys.stderr)
        sys.exit()

    processes_info = last_pid(user_id, verbose=verbose)

    if len(processes_info[1]) == 0:
        print("[!!] Looks like user {0} doesn't have a last PID list.\n".format(user_name))

    print("\n[*] Showing processes for user {0} -> id: {1}.".format(user_name, user_id))
    print("[*] Last write time: {0}".format( processes_info[0]))
    print("[!!] Process are shown from most recent to the older one.\n")

    newline_countdown = 1
    for process in processes_info[1]:
        print("\t[*] Process info:", process)

        if newline_countdown == 3:
            print()
            newline_countdown = 0
        
        newline_countdown += 1

if __name__ == '__main__':
    verbose = False

    if "-v" in sys.argv:
        verbose = True
    
    if len(sys.argv) < 2:
        print_all_users_lpids(verbose)

    else:
        print_single_user_lpd(sys.argv[1], verbose)
