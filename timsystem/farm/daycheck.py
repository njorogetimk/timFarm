class Dates():
    """
    date1: earlier date
    date2: later date

    date formart : Jun 01, 2019
    """

    def __init__(self, date1, date2):
        self.monthmapper = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        self.date1 = date1
        self.date2 = date2
        self.date1_split = self.date1.split()
        self.date2_split = self.date2.split()
        self.day1 = int(self.date1.split()[1].strip(','))
        self.month1 = self.monthmapper[self.date1.split()[0]]
        self.year1 = int(self.date1.split()[2])
        self.day2 = int(self.date2.split()[1].strip(','))
        self.month2 = self.monthmapper[self.date2.split()[0]]
        self.year2 = int(self.date2.split()[2])

        self.leap = {
            '0': 0, '1': 31, '2': 60, '3': 91, '4': 121, '5': 152,
            '6': 182, '7': 213, '8': 244, '9': 274, '10': 305, '11': 335,
            '12': 366
        }
        self.none_leap = {
            '0': 0, '1': 31, '2': 59, '3': 90, '4': 120, '5': 151,
            '6': 181, '7': 212, '8': 243, '9': 273, '10': 304, '11': 334,
            '12': 365
        }

    def day_no(self):
        """
        Check if leap year, if same year date and return day number
        """
        # check if leap year
        if self.year1 % 4 == 0:
            # Leap year
            day_no_1 = self.day1 + self.leap[str(self.month1-1)]
        else:
            # None leap year
            day_no_1 = self.day1 + self.none_leap[str(self.month1-1)]

        if self.year2 % 4 == 0:
            # Leap year
            day_no_2 = self.day2 + self.leap[str(self.month2-1)]
        else:
            # None leap year
            day_no_2 = self.day2 + self.none_leap[str(self.month2-1)]

        # Check for same year
        if self.year1 == self.year2:
            day_no = day_no_2 - day_no_1 + 1
        else:
            # Check if year1 is a leap year
            if self.year1 % 4 == 0:
                end_year = 366 - day_no_1 + 1
                day_no = end_year + day_no_2
            else:
                end_year = 365 - day_no_1 + 1
                day_no = end_year + day_no_2
        return day_no


class ConvDate():
    """
    Converts date formart from 'Jun 01, 2019' to '2019, 6, 1'
    date: Date to be converted
    """

    def __init__(self, date):
        self.date = date

    def result(self):
        """
        Returns date in formart 'yyyy, mm, dd'
        """
        self.monthmapper = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        self.month = self.monthmapper[self.date.split()[0]]
        self.day = self.date.split()[1].strip(',')
        self.year = self.date.split()[2]
        newdate = self.year+', '+str(self.month)+', '+self.day
        return newdate
