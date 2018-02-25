# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 20:56:56 2018

@author: M
"""

#INTC to PLN simple graph

import requests
import datetime
import numpy
import matplotlib.pyplot as plt
import matplotlib.widgets as widget

Url = "https://marketdata.websol.barchart.com/getHistory.json"
ApiKey = "de845f7902386646116b91433e4c2c2e"

Periods = ['1d','5d','1M','3M','6M','1Y','2Y']

CommonParameters = {
        'order' : 'asc'
        }

PeriodParameters = {
        '1d' : {'type':'minutes',
                'interval' : '15'},
        '5d' : {'type':'minutes',
                'interval' : '30'},
        '1M' : {'type':'minutes',
                'interval' : '30'},
        '3M' : {'type':'daily'   },
        '6M' : {'type':'daily'   },
        '1Y' : {'type':'daily'   },
        '2Y' : {'type':'daily'   }}


TimeDiffs = {'1d' : datetime.timedelta(days=1),
             '5d' : datetime.timedelta(days=5),
             '1M' : datetime.timedelta(days=31),
             '3M' : datetime.timedelta(days=3*31),
             '6M' : datetime.timedelta(days=6*31),
             '1Y' : datetime.timedelta(days=365),
             '2Y' : datetime.timedelta(days=2*365),
            }

# we need to expand timespan to make sure we fetch all necessary data while dealing
# with timezones
MarketTimeDiffs = {'1d' : datetime.timedelta(days=1 + 2),
             '5d' : datetime.timedelta(days=5 + 4),
             '1M' : datetime.timedelta(days=31 + 5),
             '3M' : datetime.timedelta(days=3*31 + 5),
             '6M' : datetime.timedelta(days=6*31 + 5),
             '1Y' : datetime.timedelta(days=365 + 7),
             '2Y' : datetime.timedelta(days=2*365 + 7),
            }

#Plot resolution
DeltaDatetimes = {'1d' : datetime.timedelta(minutes=15),
             '5d' : datetime.timedelta(minutes=30),
             '1M' : datetime.timedelta(minutes=30),
             '3M' : datetime.timedelta(days=1),
             '6M' : datetime.timedelta(days=1),
             '1Y' : datetime.timedelta(days=1),
             '2Y' : datetime.timedelta(days=1),
            }

#TODO: Add plot params for each period
PlotParameters = {}

Symbols = { 'Intel' : 'INTC',
            'Currency' : '^USDPLN'}
        
Response_Status_Codes = {
    'OK' : 200,
    'Bad Request ' : 400,
    'Internal Server Error' : 500}

#Replace from last occurance in string    
def rreplace(S, Old, New, Occurrence):
    Li = S.rsplit(Old, Occurrence)
    return New.join(Li)


#Function returns start date in fixed string format for our stock market query
def GetStartDatetime(Period):
    StartDate = datetime.datetime.today() - MarketTimeDiffs[Period]
    #+0100 add Polish timezone information
    StartDateString = "{Year:04d}{Month:02d}{Day:02d}{Hour:02d}{Minute:02d}{Second:02d}+01:00".format(Year = StartDate.year,
                                                                                                      Month = StartDate.month,
                                                                                                      Day = StartDate.day,
                                                                                                      Hour = StartDate.hour,
                                                                                                      Minute = StartDate.minute,
                                                                                                      Second = StartDate.second)
    #StartDateString = "{Year:04d}{Month:02d}{Day:02d}{Hour:02d}{Minute:02d}{Second:02d}".format(Year = StartDate.year,
    #                                                                                            Month = StartDate.month,
    #                                                                                            Day = StartDate.day,
    #                                                                                            Hour = StartDate.hour,
    #                                                                                            Minute = StartDate.minute,
    #                                                                                            Second = StartDate.second)
    return StartDateString

#Function gathers parameters for stock market query
def PrepareRequestParameters(Period,Symbol):
    Request = {'apikey' : ApiKey}
    Request.update({'symbol' : Symbol})
    Request.update(PeriodParameters[Period])
    Request.update({'startDate' : GetStartDatetime(Period)})
    Request.update(CommonParameters)
    return Request

#Function sends stock market query and get response
def GetWebData(Period,Symbol):
    Parameters = PrepareRequestParameters(Period,Symbol)
    print(Parameters)
    Response = requests.get(Url, params=Parameters)
    return Response

#Wrapper for sending INTC query
def GetIntelData(Period):
    return GetWebData(Period,Symbols['Intel'])

#Wrapper for sending ^USDPLN query
def GetCurrencyData(Period):
    return GetWebData(Period,Symbols['Currency'])

#Function reshape data format into data[key][...] 
def ExtractData(Keys,Data):
    return [[record[key] for record in Data] for key in Keys]


#we need to convert timestamp from Web API's barchart format '2018-02-13T00:00:00-06:00'
#to datetime.datetime acceptable format '2018-02-13T00:00:00:-0600'
def ConvertTimestamp(Timestamp):
    #TODO: do it more pythonic
    if Timestamp[-6] == '+':
        ConvertedTimestamp = rreplace(Timestamp,"+",":+",1)
    else:
        ConvertedTimestamp = rreplace(Timestamp,"-",":-",1)
    ConvertedTimestamp = rreplace(ConvertedTimestamp,":","",1)
    return ConvertedTimestamp  

#Extract datetime from string
#Time - array of datetime strings
def ExtractDatetimeData(Time):
    return [datetime.datetime.strptime(ConvertTimestamp(item),'%Y-%m-%dT%H:%M:%S:%z') for item in Time]

#Function gets requested stock exchange data from barchart.com using free getHistory API in .json format
def GetMarketData(Period):
    IntcData = GetIntelData(Period)
    UsdPlnData = GetCurrencyData(Period)
    if (Response_Status_Codes['OK'] == IntcData.status_code) and (Response_Status_Codes['OK'] == UsdPlnData.status_code):
        #TODO: try..catch exception if json fails 
        IntcData = IntcData.json()
        UsdPlnData = UsdPlnData.json()

        #Extract only necessary data from response
        IntcData = ExtractData(['timestamp','close'],IntcData['results'])
        UsdPlnData = ExtractData(['timestamp','close'],UsdPlnData['results'])

        #Format timestamp info from string to datatime.datetime object with timezone awareness
        IntcData[0] = ExtractDatetimeData(IntcData[0])
        UsdPlnData[0] = ExtractDatetimeData(UsdPlnData[0])
  
        return IntcData, UsdPlnData
    else:
        return None


def FindBestFittingElement(np_index,start_data_index,data,np_dt):
    end_data_index = len(data[0])
    return_done = False
    
    for data_index in range(start_data_index,end_data_index):
            #print("\tSprawdzam data_index: ",data_index," z chwili: ",data[0][data_index])
            if data[0][data_index] > np_dt[np_index]:
                #wstaw wartosc z poprzeniej probki
                if (data_index-1) >= 0:
                    return_np_data = data[1][data_index-1]
                    #mozemy isc do nastpnego elementu NpDatetime
                    return_data_index = data_index
                    #print("Znalezlilsmy best fit data")
                    break
                else:
                    print("Mamy za malo danych")
                    #print(dt_index)
                    return_np_data = 0;
                    return_data_index = data_index
                    break

            elif data[0][data_index] == np_dt[np_index]:
                return_np_data = data[1][data_index]
                #mozemy isc do nastpnego elementu NpDatetime
                return_data_index = data_index
                #print("Znalezlilsmy best fit data - w punkt")
                break
            else:
                if data_index == end_data_index:
                    #no need to further processing
                    #fill rest of array with Intc[1][IntcLastIndex]
                    return_np_data = data[1][data_index]
                    return_data_index = data_index
                    return_done = True
                    #print("doszli do konca tablicy")
                    break
                
    else:
        #TODO: opisz ten case
        return_np_data = data[1][data_index]
        return_data_index = data_index
        return_done = False
        #print("wyszliszmy z petli for")
            
    return return_np_data,return_data_index,return_done

def PreparePlotData(period,Intc,UsdPln):
    EndDatetime = datetime.datetime.today()
    #Add timezone awareness UTC+1
    EndDatetime = EndDatetime.replace(tzinfo = datetime.timezone(datetime.timedelta(hours = 1)))

    StartDatetime = EndDatetime - TimeDiffs[period]

    #numpy datetime array data init
    NpDatetime = numpy.arange(StartDatetime, EndDatetime, DeltaDatetimes[period], dtype = datetime.datetime)

    print("Datatime:")
    print(StartDatetime)
    print(EndDatetime)

    #lets do the magic...
    
    #create and init NpIntc, NpUsdPln, NpIntc2Pln numpy arrays
    NpIntc = numpy.zeros(len(NpDatetime))
    #fill Intc numpy array with last value from INTC response
    NpIntc.fill(Intc[1][-1])
    
    NpUsdPln = numpy.zeros(len(NpDatetime))
    #fill UsdPln numpy array with last value from ^USDPLN response
    NpUsdPln.fill(UsdPln[1][-1])
    
    NpIntc2Pln = numpy.zeros(len(NpDatetime))

    #Intc[0][] - contains datetime
    #Intc[1][] - contains data

    intc_data_index = 0
    intc_data_done = False
    usdpln_data_index = 0
    usdpln_data_done = False
        
    for dt_index in range(len(NpDatetime)):
        #print("Iter dt_index: ", dt_index ," czas: ", NpDatetime[dt_index])

        #przeszukujemy tablice datetime dla kursu Intc, czyli Intc[0] od zerowego
        #elementu w petli.
        #Sprawdzamy czy jego wartosc jest wieksza od aktualnie analizowane 'dt'. Jesli jest
        #ozanacza to ze wartosc akcji z !!poprzedniego!! element bedzie stanowila faktyczna cene akcji w chwili dt
        #Corner case w ktorym okaze sie ze nasz element z petlo for ma index 0 i musimy brac -1 jest sytuacja bledna
        #bo oznacza ze mamy za malo danych z gieldy

        #Find the best fitting data
        if intc_data_done == False:
            NpIntc[dt_index],intc_data_index,intc_data_done = FindBestFittingElement(dt_index,intc_data_index,Intc,NpDatetime)
        if usdpln_data_done == False:    
            NpUsdPln[dt_index],usdpln_data_index,usdpln_data_done = FindBestFittingElement(dt_index,usdpln_data_index,UsdPln,NpDatetime)

    #final step 
    NpIntc2Pln = NpIntc * NpUsdPln

    return NpDatetime,NpIntc,NpUsdPln,NpIntc2Pln


def UpdatePlot(Period):
    #Fetch data from stock exchange market using barchart Web APi
    Intc,UsdPln = GetMarketData(Period)

    #prepare plot array
    NpDatetime,NpIntc,NpUsdPln,NpIntc2Pln = PreparePlotData(Period,Intc,UsdPln)

    ax[0].clear()
    ax[0].set_ylabel("INTC(USD)")
    ax[0].set_title("Kurs INTC w USD")
    ax[0].grid(True,linestyle = '--')
    ax[0].plot_date(NpDatetime,NpIntc,'r',xdate=True)

    ax[1].clear()
    ax2.clear()

    ax[1].set_xlabel("Czas")
    ax[1].set_ylabel("INTC(PLN)")
    ax[1].set_title("Kurs INTC w PLN")
    ax[1].grid(True,linestyle = '--')
    ax[1].plot_date(NpDatetime,NpIntc2Pln,'b',xdate=True)
    
    ax2.set_ylabel("^USDPLN")
    ax2.plot_date(NpDatetime,NpUsdPln,'g:',xdate=True,linewidth=0.7)

     
    plt.draw()
    return


class ButtonClickProcessor(object):
    def __init__(self, axes, label):
        self.button = widget.Button(axes, label)
        self.button.on_clicked(self.process)
        return

    def process(self, event):
        UpdatePlot(self.button.label.get_text())
        return


def CreateButtons(Periods):

    width = 1/len(Periods)
    bx = []
    buttons = []
    left = 0.0
    for index in range(len(Periods)):
        bx.append(plt.axes([left, 0.0, width, 0.05]))
        buttons.append(ButtonClickProcessor(bx[-1], Periods[index]))
        left += width
   
    return bx,buttons
    
#----Script Start----
if __name__ == "__main__":

    #create plot figure
    fig, ax = plt.subplots(2,1)
    fig.canvas.set_window_title('intc2pln')
    plt.subplots_adjust(bottom=0.15)
    ax2 = ax[1].twinx()

    UpdatePlot(Periods[1])
    
    #create buttons
    bx,buttons = CreateButtons(Periods)
       
    
    plt.show() 






