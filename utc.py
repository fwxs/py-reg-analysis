import sys


def get_be_time(encoded_date):
    """
        Returns a reversed list. 
        @param encoded_date: NetworkList encoded time value.
    """
    # Divides the provided value into a four sized element.
    time_units_hex_le = [encoded_date[inx:inx + 2] for inx in range(0, 16, 2)]
    # Reverse the list and the bytes.
    return [time_units_hex_le[inx].hex()[-2:] + time_units_hex_le[inx].hex()[:2] for inx in range(0, 8)]


def get_time_units(encoded_date):
    """ 
        Returns a list of the date in the microsoft 'networkList' Registry value. 
        @param encoded_date: NetworkList encoded time value.
    """
    time_units = []
    time_units_hex_be = get_be_time(encoded_date)

    # Iterates through the values of the Big-Endian order list.
    for i in range(len(time_units_hex_be)):

        j = 3
        result = 0

        for digit in time_units_hex_be[i]:
            # Transforms from hexadecimal to decimal.
            result += int(digit, base=16) * (16 ** j)
            j -= 1

        # Appends the result to a list.
        time_units.append(result)

    return time_units


def get_month(month_value):
    """
        Return the month. 
        @param month_value: NetworkList-time-value month chunk.
    """
    months = {1: "January", 2: "February", 3: "March", 4: "April",
              5: "May", 6: "June", 7: "July", 8: "August",
              9: "September", 10: "October", 11: "November",
              12: "December"}

    # Checks if the values of the list exits in the dictionaries.
    if month_value in months.keys():
        return months.get(month_value)

    else:
        raise KeyError("Can't find the month name.")
        sys.exit(1)


def get_weekday_name(weekday):
    """
        Return the name of the week day. 
        @param weekday: Week day chunk of the NetworkList Registry key.
    """
    weekday_names = {0: "Sunday", 1: "Monday", 2: "Tuesday",
                     3: "Wednesday", 4: "Thursday", 5: "Friday",
                     6: "Saturday"}

    if weekday in weekday_names:
        return weekday_names[weekday]
    else:
        raise KeyError("Can't find the weekday name.")
        exit(1)


def format_date(month, year, weekday_name, day):
    """ Returns a formatted date (month, year weekday_name day). """
    month = get_month(month)
    weekday_name = get_weekday_name(weekday_name)
    return "{0}, {1} {2} {3}".format(month, year, weekday_name, day)


def format_time(time_units):
    """ Returns a formated time value (hh:mm:ss:ms). """
    return ":".join(["{0}".format(time_units[inx]) for inx in range(4, len(time_units))])


def format_date_time(date, time):
    """ Returns a formatted date time version of the provided values. """
    return "{0} {1} UTC".format(date, time)


def get_utc(encoded_date):
    """ Returns a utc time value. """
    time_units = get_time_units(encoded_date)

    date = format_date(time_units[1], time_units[0], time_units[2], time_units[3])
    time = format_time(time_units)

    return format_date_time(date, time)
