# -*- coding: utf-8 -*-
import datetime
import requests
import numpy
import matplotlib.pyplot as plt
import matplotlib.widgets as widget

"""
INTC to PLN simple graph

Created on Mon Feb 12 20:56:56 2018

@author: Michal Duzinkiewicz
"""


"""
Copyright © 2018 All market data provided by Barchart Solutions.

BATS market data is at least 15-minutes delayed. Forex market data is at least
10-minutes delayed. AMEX, NASDAQ, NYSE and futures market data (CBOT, CME,
COMEX and NYMEX) is end-of-day.Information is provided 'as is' and solely for
informational purposes, not for trading purposes or advice, and is delayed.
To see all exchange delays and terms of use, please see our disclaimer.
"""

URL = "https://marketdata.websol.barchart.com/getHistory.json"
API_KEY = "de845f7902386646116b91433e4c2c2e"

PERIODS = ['1d', '5d', '1M', '3M', '6M', '1Y', '2Y']

COMMON_PARAMETERS = {'order': 'asc'}

PERIOD_PARAMETERS = {'1d': {'type': 'minutes', 'interval': '15'},
                     '5d': {'type': 'minutes', 'interval': '30'},
                     '1M': {'type': 'minutes', 'interval': '30'},
                     '3M': {'type': 'daily'},
                     '6M': {'type': 'daily'},
                     '1Y': {'type': 'daily'},
                     '2Y': {'type': 'daily'}}

TIME_DIFFS = {'1d': datetime.timedelta(days=1),
              '5d': datetime.timedelta(days=5),
              '1M': datetime.timedelta(days=31),
              '3M': datetime.timedelta(days=3*31),
              '6M': datetime.timedelta(days=6*31),
              '1Y': datetime.timedelta(days=365),
              '2Y': datetime.timedelta(days=2*365)}

# we need to expand timespan to make sure we fetch all necessary data while
# dealing with timezones
MARKET_TIME_DIFFS = {'1d': datetime.timedelta(days=1 + 2),
                     '5d': datetime.timedelta(days=5 + 4),
                     '1M': datetime.timedelta(days=31 + 5),
                     '3M': datetime.timedelta(days=3*31 + 5),
                     '6M': datetime.timedelta(days=6*31 + 5),
                     '1Y': datetime.timedelta(days=365 + 7),
                     '2Y': datetime.timedelta(days=2*365 + 7)}

# Plot resolution
DELTA_DATETIMES = {'1d': datetime.timedelta(minutes=15),
                   '5d': datetime.timedelta(minutes=30),
                   '1M': datetime.timedelta(minutes=30),
                   '3M': datetime.timedelta(days=1),
                   '6M': datetime.timedelta(days=1),
                   '1Y': datetime.timedelta(days=1),
                   '2Y': datetime.timedelta(days=1)}


SYMBOLS = {'Intel': 'INTC',
           'Currency': '^USDPLN'}

RESPONSE_STATUS_CODES = {'OK': 200,
                         'Bad Request ': 400,
                         'Internal Server Error': 500}


def rreplace(old_str, old, new, occurrence):
    """
    Replace from last occurance in string

    Function rreplace returns a copy of the string in which the occurrences
    of old have been replaced with new but function starts from the end of
    the old_str.

    Args:
        old_str: input string
        old: substring to be replaced
        new: substring to be inserted
        occurrence: number of old substring occurrences to be replaced

    Returns:
        Formatted string with replaced substrings
    """
    new_str = old_str.rsplit(old, occurrence)
    return new.join(new_str)


def get_start_datetime(period):
    """
    Function returns query start datetime

    This function returns query start datetime in fixed string format
    compatibile with data provider barchart: "YYYYMMDDhhmmss+1:00"

    Args:
        period: string with requested datetime interval e.g '1d'..'2Y'

    Returns:
        Formatted string with start datetime
    """
    start_date = datetime.datetime.today() - MARKET_TIME_DIFFS[period]
    # +0100 add Polish timezone information
    start_date_str_template = ("{year:04d}"
                               "{month:02d}"
                               "{day:02d}"
                               "{hour:02d}"
                               "{minute:02d}"
                               "{second:02d}"
                               "+01:00")

    # start_date_str_template = ("{Year:04d}"
    #                            "{Month:02d}"
    #                            "{Day:02d}"
    #                            "{Hour:02d}"
    #                            "{Minute:02d}"
    #                            "{Second:02d}")

    start_date_str = start_date_str_template.format(year=start_date.year,
                                                    month=start_date.month,
                                                    day=start_date.day,
                                                    hour=start_date.hour,
                                                    minute=start_date.minute,
                                                    second=start_date.second)

    return start_date_str


def prepare_request_parameters(period, symbol):
    """
    Function merges parameters for stock market query.

    This function merges all needed stock market query into one dictonary
    object.

    Args:
        period: string with requested datetime interval e.g '1d'..'2Y'
        symbol: stock market symbol e.g INTC, ^USDPLN, APPL, IBM

    Returns:
        Dictonary with stock market query parameters
    """
    request = {'apikey': API_KEY,
               'symbol': symbol,
               'startDate': get_start_datetime(period)}
    request.update(PERIOD_PARAMETERS[period])
    request.update(COMMON_PARAMETERS)
    return request


def get_web_data(period, symbol):
    """
    Function sends stock market query and returns query response

    This function prepares stock market query and sends it to barchart data
    provider. As a result function returns Response object with requested data.

    Args:
        period: string with requested datetime interval e.g '1d'..'2Y'
        symbol: string with stock market symbol e.g INTC, ^USDPLN, APPL, IBM

    Returns:
        requests.Response object with requested data
    """
    parameters = prepare_request_parameters(period, symbol)
    print(parameters)
    response = requests.get(URL, params=parameters)
    return response


def get_intel_data(period):
    """
    Wrapper for INTC get data

    This function prepares INTC query and sends it to barchart data
    provider. As a result function returns Response object with requested data.

    Args:
        period: string with requested datetime interval e.g '1d'..'2Y'

    Returns:
        requests.Response object with INTC requested data
    """
    return get_web_data(period, SYMBOLS['Intel'])


def get_currency_data(period):
    """
    Wrapper for ^USDPLN get data

    This function prepares ^USDPLN query and sends it to barchart data
    provider. As a result function returns Response object with requested data.

    Args:
        period: string with requested datetime interval e.g '1d'..'2Y'

    Returns:
        requests.Response object with ^USDPLN requested data
    """
    return get_web_data(period, SYMBOLS['Currency'])


# Function reshape data format into data[key][...]
def extract_data(keys, data):
    """
    Function reshape data format into data[key][...] format

    This one liner function format interleaved array into [key][data] format.
    Example: Our data array looks like this [[a:d1, b:d1, c:d1,], [a:d2, b:d2,
    c:d2],...]. Keys are ['a','c']. Our output array will look like:
    Output[][] = ['a':[d1,d2...],'c':[d1,d2...]]

    Args:
        key: list with columns names strings
        data: array of interleaved data

    Returns:
        Array of column-sorted data
    """
    return [[record[key] for record in data] for key in keys]


def convert_timestamp(timestamp):
    """
    Function converts timestamp

    This function converts timestamp from Web API's barchart format e.g:
    '2018-02-13T00:00:00-06:00' to datetime.datetime acceptable format:
    '2018-02-13T00:00:00:-0600'

    Args:
        timestamp: string from barchart with datetime

    Returns:
        string convertable to datetime format
    """
    # TODO: do it more pythonic
    if timestamp[-6] == '+':
        converted_timestamp = rreplace(timestamp, "+", ":+", 1)
    else:
        converted_timestamp = rreplace(timestamp, "-", ":-", 1)

    converted_timestamp = rreplace(converted_timestamp, ":", "", 1)
    return converted_timestamp


# Extract datetime from string
# Time - array of datetime strings
def extract_datetime_data(time):
    return [datetime.datetime.strptime(convert_timestamp(x),
                                       '%Y-%m-%dT%H:%M:%S:%z') for x in time]


# Function gets requested stock exchange data from barchart.com using free
# getHistory API in .json format
def get_market_data(period):
    intc_data = get_intel_data(period)
    usdpln_data = get_currency_data(period)

    if (RESPONSE_STATUS_CODES['OK'] == intc_data.status_code) and \
       (RESPONSE_STATUS_CODES['OK'] == usdpln_data.status_code):
        # print(intc_data)
        # print(usdpln_data)

        intc_data = intc_data.json()
        usdpln_data = usdpln_data.json()

        # Extract only necessary data from response
        intc_data = extract_data(['timestamp', 'close'],
                                 intc_data['results'])
        usdpln_data = extract_data(['timestamp', 'close'],
                                   usdpln_data['results'])

        # Format timestamp info from string to datatime.datetime object
        # with timezone awareness
        intc_data[0] = extract_datetime_data(intc_data[0])
        usdpln_data[0] = extract_datetime_data(usdpln_data[0])

        return intc_data, usdpln_data
    else:
        raise ValueError


def find_best_fitting_element(start_data_index, data, np_dt):
    end_data_index = len(data[0])
    return_done = False

    for data_index in range(start_data_index, end_data_index):
        # print("\tChecking data_index: ", data_index,
        #      " from: ", data[0][data_index])
        if data[0][data_index] > np_dt:
            # insert value from previous element
            if (data_index-1) >= 0:
                return_np_data = data[1][data_index-1]
                # ok, we're done. We can go to the next NpDatetime element
                return_data_index = data_index
                # print("Best fitting element found")
                break
            else:
                # We are asking for best fitting data element for datetime
                # x while our data datetimes are from later period
                # print("We don't enought data to find best fitting elem.")
                # print(dt_index)
                return_np_data = None
                return_data_index = data_index
                break

        elif data[0][data_index] == np_dt:
            return_np_data = data[1][data_index]
            # ok, we're done. Exact match. We can go to the
            # next NpDatetime element
            return_data_index = data_index
            # print("Best fitting element found - exact match")
            break
        else:
            if data_index == end_data_index:
                # no need to further processing
                # fill rest of array with Intc[1][IntcLastIndex]
                return_np_data = data[1][data_index]
                return_data_index = data_index
                return_done = True
                # print("We're run out of data")
                break

    else:
        # We should never get here, but if we somehow get here just insert
        # data from last element
        return_np_data = data[1][data_index]
        return_data_index = data_index
        return_done = False
        # print("End of data search loop")

    return return_np_data, return_data_index, return_done


# Function prepares data for matplotlib pyplot
def prepare_plot_data(period, intc, usdpln):

    # Determinate Start and End datetime:
    end_datetime = datetime.datetime.today()
    # Add timezone awareness UTC+1
    end_datetime = end_datetime.replace(tzinfo=datetime.timezone
                                        (datetime.timedelta(hours=1)))

    start_datetime = end_datetime - TIME_DIFFS[period]

    # Prepare datetime axis
    # numpy datetime array data init
    np_datetime = numpy.arange(start_datetime,
                               end_datetime,
                               DELTA_DATETIMES[period],
                               dtype=datetime.datetime)

    print("Datatime:")
    print(start_datetime)
    print(end_datetime)

    # lets do the magic...

    # create and init NpIntc, NpUsdPln, NpIntc2Pln numpy arrays
    np_intc = numpy.zeros(len(np_datetime))
    # fill Intc numpy array with last value from INTC response
    np_intc.fill(intc[1][-1])

    np_usdpln = numpy.zeros(len(np_datetime))
    # fill UsdPln numpy array with last value from ^USDPLN response
    np_usdpln.fill(usdpln[1][-1])

    np_intc2pln = numpy.zeros(len(np_datetime))

    # Intc[0][] - contains datetime
    # Intc[1][] - contains data

    intc_data_index = 0
    intc_data_done = False
    usdpln_data_index = 0
    usdpln_data_done = False

    for dt_index, dt_value in enumerate(np_datetime):
        # print("Iter dt_index: ", dt_index,
        #      " datetime: ", dt_value)

        # Find the best fitting data for NpDatetime element
        if intc_data_done is False:
            np_intc[dt_index], intc_data_index, intc_data_done = \
                find_best_fitting_element(intc_data_index, intc, dt_value)
        if usdpln_data_done is False:
            np_usdpln[dt_index], usdpln_data_index, usdpln_data_done = \
                find_best_fitting_element(usdpln_data_index, usdpln, dt_value)

    # calculate INTC value in PLN
    np_intc2pln = np_intc * np_usdpln

    return np_datetime, np_intc, np_usdpln, np_intc2pln


def update_plot(period):
    # Fetch data from stock exchange market using barchart Web API
    try:
        intc, usdpln = get_market_data(period)
    except:
        print("Error!!! Something went wrong while fetching data.")
        return

    # prepare plot array
    np_datetime, np_intc, np_usdpln, np_intc2pln = \
        prepare_plot_data(period, intc, usdpln)

    ax[0].clear()
    ax[0].set_ylabel("INTC(USD)")
    ax[0].set_title("Kurs INTC w USD")
    ax[0].grid(True, linestyle='--')
    ax[0].plot_date(np_datetime, np_intc, 'r', xdate=True)

    ax[1].clear()
    ax2.clear()

    ax[1].set_xlabel("Czas")
    ax[1].set_ylabel("INTC(PLN)")
    ax[1].set_title("Kurs INTC w PLN")
    ax[1].grid(True, linestyle='--')
    ax[1].plot_date(np_datetime, np_intc2pln, 'b', xdate=True)

    ax2.set_ylabel("^USDPLN")
    ax2.plot_date(np_datetime, np_usdpln, 'g:', xdate=True, linewidth=0.7)

    plt.draw()
    return


class ButtonClickProcessor(object):
    def __init__(self, axes, label):
        self.button = widget.Button(axes, label)
        self.button.on_clicked(self.process)
        return

    def process(self, event):
        update_plot(self.button.label.get_text())
        return


def create_buttons(periods):

    width = 1/len(periods)
    bx = []
    buttons = []
    left = 0.0

    for period in periods:
        bx.append(plt.axes([left, 0.0, width, 0.05]))
        buttons.append(ButtonClickProcessor(bx[-1], period))
        left += width

    return bx, buttons

# ----Script Start----
if __name__ == "__main__":

    # create plot figure
    fig, ax = plt.subplots(2, 1)
    fig.canvas.set_window_title('intc2pln')
    plt.subplots_adjust(bottom=0.15)
    ax2 = ax[1].twinx()

    # provide data to plot
    update_plot(PERIODS[3])

    # create buttons
    bx, buttons = create_buttons(PERIODS)

    plt.show()
