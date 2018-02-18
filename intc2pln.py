# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 20:56:56 2018

@author: M
"""

#INTC to PLN

import requests
import datetime
import numpy

Url = "https://marketdata.websol.barchart.com/getHistory.json"
ApiKey = "de845f7902386646116b91433e4c2c2e"

Periods = ['1d','5d','1M','3M','6M','1Y','3Y']

CommonParameters = {
        'order' : 'asc'
        }

PeriodParameters = {
        '1d' : {'type':'minutes',
                'interval' : '15'},
        '5d' : {'type':'minutes',
                'interval' : '60'},
        '1M' : {'type':'daily'   },
        '3M' : {'type':'daily'   },
        '6M' : {'type':'daily'   },
        '1Y' : {'type':'daily'   },
        '3Y' : {'type':'daily'   }}

# we need to expand timespan to make sure we fetch all necessary data while dealing
# with timezones
TimeDiffs = {'1d' : datetime.timedelta(days=2),
             '5d' : datetime.timedelta(days=5),
             '1M' : datetime.timedelta(days=31),
             '3M' : datetime.timedelta(days=3*31),
             '6M' : datetime.timedelta(days=6*31),
             '1Y' : datetime.timedelta(days=365),
             '3Y' : datetime.timedelta(days=3*365),
            }

MarketTimeDiffs = {'1d' : datetime.timedelta(days=1 + 2),
             '5d' : datetime.timedelta(days=5 + 3),
             '1M' : datetime.timedelta(days=31 + 5),
             '3M' : datetime.timedelta(days=3*31 + 5),
             '6M' : datetime.timedelta(days=6*31 + 5),
             '1Y' : datetime.timedelta(days=365 + 7),
             '3Y' : datetime.timedelta(days=4*365 + 14),
            }

DeltaDatetimes = {'1d' : datetime.timedelta(minutes=15),
             '5d' : datetime.timedelta(hours=1),
             '1M' : datetime.timedelta(days=1),
             '3M' : datetime.timedelta(days=1),
             '6M' : datetime.timedelta(days=1),
             '1Y' : datetime.timedelta(days=1),
             '3Y' : datetime.timedelta(days=1),
            }

Symbols = { 'Intel' : 'INTC',
            'Currency' : '^USDPLN'}
        
Response_Status_Codes = {
    'OK' : 200,
    'Bad Request ' : 400,
    'Internal Server Error' : 500}


#TODO: add comment
def GetStartDatetime(Period):
    StartDate = datetime.datetime.today() - MarketTimeDiffs[Period]
    #+0100 add timezone information
    StartDateString = "{Year:04d}{Month:02d}{Day:02d}{Hour:02d}{Minute:02d}{Second:02d}+01:00".format(Year = StartDate.year, Month = StartDate.month, Day = StartDate.day,Hour = StartDate.hour, Minute = StartDate.minute,Second = StartDate.second)
    return StartDateString

#TODO: add comment
def PrepareRequestParameters(Period,Symbol):
    Request = {'apikey' : ApiKey}
    Request.update({'symbol' : Symbol})
    Request.update(PeriodParameters[Period])
    Request.update({'startDate' : GetStartDatetime(Period)})
    Request.update(CommonParameters)
    return Request

#TODO: add comment
def GetWebData(Period,Symbol):
    Parameters = PrepareRequestParameters(Period,Symbol)
    print(Parameters)
    Response = requests.get(Url, params=Parameters)
    return Response

#TODO: add comment
def GetIntelData(Period):
    return GetWebData(Period,Symbols['Intel'])

#TODO: add comment
def GetCurrencyData(Period):
    return GetWebData(Period,Symbols['Currency'])

#TODO: add comment
def ExtractData(Keys,Data):
    return [[record[key] for record in Data] for key in Keys]

#Replace from last occurance in string    
def rreplace(S, Old, New, Occurrence):
    Li = S.rsplit(Old, Occurrence)
    return New.join(Li)

#we need to convert timestamp from barchart format '2018-02-13T00:00:00-06:00'
#into datetime.datetime acceptable format '2018-02-13T00:00:00:-0600'
def ConvertTimestamp(Timestamp):
    if Timestamp[-6] == '+':
        ConvertedTimestamp = rreplace(Timestamp,"+",":+",1)
    else:
        ConvertedTimestamp = rreplace(Timestamp,"-",":-",1)
    ConvertedTimestamp = rreplace(ConvertedTimestamp,":","",1)
    return ConvertedTimestamp  

def FormatDatetimeData(Time):
    return [datetime.datetime.strptime(ConvertTimestamp(item),'%Y-%m-%dT%H:%M:%S:%z') for item in Time]

#TODO: add comment
def GetMarketData(Period):
    IntcData = GetIntelData(Period)
    UsdPlnData = GetCurrencyData(Period)
    if (Response_Status_Codes['OK'] == IntcData.status_code) and (Response_Status_Codes['OK'] == UsdPlnData.status_code):
        #TODO try..catch exception if json fails 
        IntcData = IntcData.json()
        UsdPlnData = UsdPlnData.json()

        #Extract only necessary data from response
        IntcData = ExtractData(['timestamp','close'],IntcData['results'])
        UsdPlnData = ExtractData(['timestamp','close'],UsdPlnData['results'])

        #Format timestamp info from string to datatime.datetime object with timezone awareness
        IntcData[0] = FormatDatetimeData(IntcData[0])
        UsdPlnData[0] = FormatDatetimeData(UsdPlnData[0])
       
        return IntcData, UsdPlnData
    else:
        return None


def FindBestFittingElement(np_index,start_data_index,data):
    end_data_index = len(data)
    return_done = false
    
    for data_index in range(start_data_index,end_data_index):
            #print("\tSprawdzam intc_index: ",intc_index," z chwili: ",Intc[0][intc_index])
            if data[0][data_index] > NpDatetime[np_index]:
                #wstaw wartosc z poprzeniej probki
                if (data_index-1) >= 0:
                    return_np_data = data[1][data_index-1]
                    #mozemy isc do nastpnego elementu NpDatetime
                    return_data_index = data_index
                    break
                else:
                    #print("Mamy za malo danych z gieldy")
                    #print(dt_index)
                    return_np_data = 0;
                    return_data_index = data_index
                    break

            elif data[0][data_index] == NpDatetime[np_index]:
                return_np_data = data[1][data_index]
                #mozemy isc do nastpnego elementu NpDatetime
                return_data_index = data_index
                break
            else:
                if data_index == end_data_index:
                    #no need to further processing
                    #fill rest of array with Intc[1][IntcLastIndex]
                    return_np_data = data[1][data_index]
                    return_data_index = data_index
                    return_done = true
                    break
                
    else:
        #TODO: opisz ten case
        return_np_data = data[1][data_index]
        return_data_index = data_index
        return_done = false
            
    return return_np_data,return_data_index,return_done

def PreparePlotData(period,Intc,UsdPln):
    #musimy okreslic rozmiar naszej tablicy
    EndDatetime = datetime.datetime.today()
    #Add timezone awareness UTC+1
    EndDatetime = EndDatetime.replace(tzinfo = datetime.timezone(datetime.timedelta(hours = 1)))
    StartDatetime = EndDatetime - TimeDiffs[period]

    #numpy datetime data      
    NpDatetime = numpy.arange(StartDatetime, EndDatetime, DeltaDatetimes[period], dtype = datetime.datetime)

    print("Datatime:")
    print(StartDatetime)
    print(EndDatetime)


    #musimy wkopiowac pod odpowiednie indeksy w tablicy dane z Intc i UsdPln
    #odpowiadające biezacemu dla danego indexu czasu 

    #lets do the magic...
    #tworzymy puste tablice dla danych akcji i kursu walut
    NpIntc = numpy.zeros(len(NpDatetime))
    NpIntc.fill(Intc[1][-1])
    
    NpUsdPln = numpy.zeros(len(NpDatetime))
    NpUsdPln.fill(UsdPln[1][-1])
    
    NpIntc2Pln = numpy.zeros(len(NpDatetime))

    #Intc[0][] - zawiera datetime'y
    #Intc[1][] - zawiera kursy akcji

    IntcIndex = 0
    IntcLastIndex = len(Intc[0])
    
    for dt_index in range(len(NpDatetime)):
        #print("Iter dt_index: ", dt_index ," czas: ", NpDatetime[dt_index])
        #print(dt)
        #przeszukujemy tablice datetime dla kursu Intc, czyli Intc[0] od zerowego
        #elementu w petli.
        #Sprawdzamy czy jego wartosc jest wieksza od aktualnie analizowane 'dt'. Jesli jest
        #ozanacza to ze wartosc akcji z !!poprzedniego!! element bedzie stanowila faktyczna cene akcji w chwili dt
        #Corner case w ktorym okaze sie ze nasz element z petlo for ma index 0 i musimy brac -1 jest sytuacja bledna
        #bo oznacza ze mamy za malo danych z gieldy

        #Find the best fitting data
        for intc_index in range(IntcIndex,IntcLastIndex):
            #print("\tSprawdzam intc_index: ",intc_index," z chwili: ",Intc[0][intc_index])
            if Intc[0][intc_index] > NpDatetime[dt_index]:
                #wstaw wartosc z poprzeniej probki
                if (intc_index-1) >= 0:
                    NpIntc[dt_index] = Intc[1][intc_index-1]
                    #mozemy isc do nastpnego elementu NpDatetime
                    IntcIndex = intc_index
                    break
                else:
                    #print("Mamy za malo danych z gieldy")
                    #print(dt_index)
                    NpIntc[dt_index] = 0;
                    break

            elif Intc[0][intc_index] == NpDatetime[dt_index]:
                NpIntc[dt_index] = Intc[1][intc_index]
                #mozemy isc do nastpnego elementu NpDatetime
                IntcIndex = intc_index
                break
            else:
                if intc_index == IntcLastIndex:
                    #no need to further processing
                    #fill rest of array with Intc[1][IntcLastIndex]
                    #TBD
                    ...
                
        else:
            #uzupelnij pozostale elementy w tablicy NpIntc wartoscia ostatniego elementu z Intc[1]
            NpIntc[dt_index] = Intc[1][intc_index]
        


    return NpDatetime,NpIntc,NpUsdPln,NpIntc2Pln

  



    


#Design:
#    GUI sklada sie z wykresu przedwiajacego kurs z ostatniego dnia (1d)
#    Nad wykresem sa guziki z nastepujacymi opcjami:1D,5D,1M,3M,6M,1Y,3Y,5Y
#    Po kliknieciu guziki konstruowane jest zapytanie do barchart 
#    o dane kursu intela oraz kurs usd2pln
#    
#    Potrzebuje funkcje, ktora tworzy zapytanie. jej jedynym parameterem jest okres i symbol.
#    Od tego parametru beda zalezec paramtery zapytnia do barchrt.
#    Dla pytan 1d i 5d bedziemy brac dane co 1h. dla pozostalych co 1dzien
#    
#    Potrzebne moduly:
#        requests, json, datetime, numpy as np?, matplotlib.pyplot as plt
#      
#    Caly skrytp potem przewaliny py2exe na plik .exe i wsio
#      
# Funkcje:
#     
#    
#     PrepareRequest - przygtowuje zapytania (okres i symbol)
#     SendRequest - wysyla zapytanie
#     GetData - wysyla zapytania
#     PreparePlotData -na podstawie odp. z zapytan tworzy dane wynikowe 
#     DrawPlotData - rysuje wykres
#     
#     i wsio:)

    
#----Script Start----
if __name__ == "__main__":

    for period in ['1M']:#Periods:
        print(period)

        #Fetch data from stock exchange market using barchart Web APi
        Intc,UsdPln = GetMarketData(period)

        #prepare plot array
        NpDatetime,NpIntc,NpUsdPln,NpIntc2Pln = PreparePlotData(period,Intc,UsdPln)


        
        print("Intc:")
        print(Intc[0][0])
        print(Intc[0][-1])
        print(len(Intc[0]))
        print("^UsdPln")
        print(UsdPln[0][0])
        print(UsdPln[0][-1])
        print(len(UsdPln[0]))
        print("\n\r")
    

    

   
#Include timezone info    
#Unify time zone
#Match records    

#Parameters = 
#        'apikey' : ApiKey,
#        'symbol' : 'INTC',
#        'type' : 'daily',
#        'startDate' : '20100101',
#        'maxRecords' : '30',
#        'order' : 'asc' }

    #Parameters = PrepareRequestParameters('1d','INTC')
    #print(Parameters)
    
    #Response = requests.get(Url, params=Parameters)

# Print the content of the response (the data the server returned)
    #print(Response.content)
