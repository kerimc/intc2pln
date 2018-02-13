# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 20:56:56 2018

@author: M
"""

#INTC to PLN

import requests
import datetime

Url = "https://marketdata.websol.barchart.com/getHistory.json"
ApiKey = "de845f7902386646116b91433e4c2c2e"

QueryType = ['1d','5d','1M','3M','6M','1Y','3Y']

CommonParameters = {
        'order' : 'asc'
        }

PeriodParams = {
        '1d' : {'type':'minutes',
                'interval' : '15'},
        '5d' : {'type':'minutes',
                'interval' : '60'},
        '1M' : {'type':'daily'   },
        '3M' : {'type':'daily'   },
        '6M' : {'type':'daily'   },
        '1Y' : {'type':'daily'   },
        '3Y' : {'type':'daily'   }}

TimeDiffs = {'1d' : datetime.timedelta(days=1),
              '5d' : datetime.timedelta(days=5),
              '1M' : datetime.timedelta(days=31),
              '3M' : datetime.timedelta(days=3*31),
              '6M' : datetime.timedelta(days=6*31),
              '1Y' : datetime.timedelta(days=365),
              '3Y' : datetime.timedelta(days=3*365),
             }
        

#TODO: Think of one structure containing all params

def GetStartDate(Period):
    StartDate = datetime.date.today() - TimeDiffs[Period]
    StartDateString = "{Year:04d}{Month:02d}{Day:02d}".format(Year = StartDate.year,Month = StartDate.month,Day = StartDate.day)
    return StartDateString

def PrepareRequestParameters(Period,Symbol):
    Request = {'apikey' : ApiKey}
    Request.update({'symbol' : Symbol})
    Request.update(PeriodParams[Period])
    Request.update({'startDate' : GetStartDate(Period)})
    Request.update(CommonParameters)
    return Request




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
    
#Parameters = {
#        'apikey' : ApiKey,
#        'symbol' : 'INTC',
#        'type' : 'daily',
#        'startDate' : '20100101',
#        'maxRecords' : '30',
#        'order' : 'asc' }

    Parameters = PrepareRequestParameters('1Y','INTC')
    print(Parameters)
    
    Response = requests.get(Url, params=Parameters)

# Print the content of the response (the data the server returned)
    print(Response.content)