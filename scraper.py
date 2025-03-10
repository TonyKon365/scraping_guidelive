from fastapi import FastAPI, HTTPException, status, Query, Response  # type: ignore
from pydantic import BaseModel  
import os
from supabase import create_client, Client  # type: ignore
from dotenv import load_dotenv 
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from datetime import datetime
import sys  
# # News
# from visit.totarastreetNews import get_news_from_totarastreet
# from visit.eventfindaNews import get_news_from_eventfinda
# from visit.undertheradarNews import get_news_from_undertheradar
# from visit.christchurchnzNews import get_news_from_christchurchnz
# from visit.voicesnzNews import get_news_from_voicesnz
# from visit.aucklandliveNews import get_news_from_aucklandlive
# from visit.taupowinterfestivalNews import get_news_from_taupowinterfestival
# from visit.comedyfestivalNews import get_news_from_comedyfestival
# from visit.neckofthewoodsNews import get_news_from_neckofthewoods
# from visit.rotoruanzNews import get_news_from_rotoruanz
# from visit.greenstoneentertainmentNews import get_news_from_greenstoneentertainment
# from visit.wellingtonnzNews import get_news_from_wellingtonnz
# #events
from visit.neckofthewoods import get_events_from_neckofthewoods

# from visit.visitperth import get_events_from_visitperth
# from visit.eventfinda import get_events_from_eventfinda
# from visit.undertheradar import get_events_from_undertheradar
# from visit.nzso import get_events_from_nzso
# from visit.mytauranga import get_events_from_mytauranga
# from visit.jazz import get_events_from_jazz
# from visit.comedyfestival import get_events_from_comedyfestival
# from visit.festivaloflights import get_events_from_festivaloflights
# from visit.taupowinterfestival import get_events_from_taupowinterfestival
# from visit.aaaticketing import get_events_from_aaaticketing
# from visit.humanitix import get_events_from_humanitix
# from visit.whakatance import get_events_from_whakatance
# from visit.crankworx import get_events_from_crankworx
# from visit.wellingtonnz import get_events_from_wellingtonnz
# from visit.heartofthecity import get_events_from_heartofthecity
# from visit.Rotoruanui import get_events_from_rotoruanui
# from visit.hawkesbaynz import get_events_from_hawkesbaynz
# from visit.venuesotautahi import get_events_from_venuesotautahi
# from visit.northlandnz import get_events_from_northlandnz
# from visit.frontiertouring import get_events_from_frontiertouring
# from visit.voicesnz import get_events_from_voicesnz
# from visit.nzopera import get_events_from_nzopera
# from visit.aucklandlive import get_events_from_aucklandlive
# from visit.dingdongloungenz import get_events_from_dingdongloungenz
# from visit.totarastreet import get_events_from_totarastreet
# from visit.powerstation import get_events_from_powerstation
# from visit.theincubator import get_events_from_theincubator
# from visit.bayvenues import get_events_from_bayvenues
# from visit.galatos import get_events_from_galatos
# from visit.hollywoodavondale import get_events_from_hollywoodavondale
# from visit.cabana import get_events_from_cabana
# from visit.crownrangelounge import get_events_from_crownrangelounge
# from visit.valhallatavern import get_events_from_valhallatavern
# from visit.arollingstone import get_events_from_arollingstone

# from visit.forummelbourneEvent import get_event_from_forummelbourne
# from visit.cornerhotelEvent import get_event_from_cornerhotel
# from visit.thetotehotelEvent import get_event_from_thetotehotel
# from visit.brisbaneEvent import get_event_from_brisbane
# from visit.destinationgoldcoastEvent import get_event_from_destinationgoldcoast
# from visit.bohmpresentsEvent import get_event_from_bohmpresents
# from visit.ticketfairyEvent import get_event_from_ticketfairy
# from visit.bigfanEvent import get_event_from_bigfan
# from visit.yonderqtEvent import get_event_from_yonderqt
# from visit.iticketEvent import get_event_from_iticket
# from visit.eventbriteEvent import get_event_from_eventbriteNZ
# from visit.livenationEvent import get_event_from_livenationNZ
# from visit.livenation import get_events_from_livenation
# from visit.tuningforkEvent import get_event_from_tuningfork
# from visit.sanfranEvent import get_event_from_sanfran
# from visit.ecclesEvent import get_event_from_eccles
# from visit.rnzbEvent import get_event_from_rnzb
# from visit.plonkwinebar import get_event_from_plonkwinebar
# from visit.ponsonbysocialclub import get_event_from_ponsonbysocialclub
# from visit.croxtonparkhotel import get_event_croxtonparkhotel
# from visit.moshtix import get_event_moshtix
# from visit.ticketfairyNz import get_event_ticketfairyNz
# from visit.ticketfairyAu import get_event_ticketfairyAu
# from visit.moshtixAu import get_event_moshtixAu
# from visit.enmoretheatreAu import get_event_enmoretheatreAu
# from visit.aucklandartgallery import get_event_aucklandartgallery
# from visit.aucklandmuseum import get_event_aucklandmuseum
# from visit.tepapaevents import get_event_get_tepapaevents
# from visit.sydney import get_event_sydney
# from visit.metrotheatre import get_event_metrotheatre
# from visit.paraoa import get_event_paraoa
# from visit.bandsintown import get_event_bandsintown
# from visit.unitedcinemas import get_event_unitedcinemas
# from visit.basementcinema import get_event_basementcinema
# from visit.abstract import get_event_abstract
# from visit.academycinemas import get_event_academycinemas
# from visit.silkyotter import get_event_silkyotter
# from visit.tivolicinema import get_event_tivolicinema
# from visit.libertystage import get_event_libertystage
# from visit.homegrown import get_event_homegrown
# from visit.manawatunz import get_event_manawatunz
# from visit.taranaki import get_event_taranaki
# from visit.wildfortaranaki import get_event_wildfortaranaki
# from visit.pumphouse import get_event_pumphouse
# from visit.mustdobrisbane import get_event_mustdobrisbane
# from visit.lovetaupo import get_event_lovetaupo
# from visit.waikatonz import get_event_waikatonz
# from visit.byronbay import get_event_byronbay
# from visit.govettbrewster import get_event_govettbrewster
# from visit.bachmusica import get_event_bachmusica
# from visit.worldofwearableart import get_event_worldofwearableart
# from visit.lakehousearts import get_event_lakehousearts
# from visit.comedy import get_event_comedy
# from visit.circa import get_event_circa
# from visit.wunderbar import get_event_wunderbar
# from visit.dunedinnz import get_event_dunedinnz





# CronJob function
async def scrape_events():
        # await get_event_from_livenationNZ()

    # await get_events_from_aucklandlive()   
    #  await get_events_from_visitperth()   
    #  await get_event_from_destinationgoldcoast()
    #  await get_event_from_bigfan() 
    # await get_events_from_hawkesbaynz()
      #  await get_event_from_eventbriteNZ()
    #  await get_events_from_whakatance() 
    #  await get_event_sydney()
    # await get_event_from_sanfran()
    # await get_events_from_frontiertouring() 


    #  await get_events_from_heartofthecity()  
    #  await get_events_from_humanitix()
    # await get_events_from_eventfinda()  
    #  await get_events_from_undertheradar() 
    # await get_events_from_livenation()
    # await get_events_from_nzopera() 
    # await get_events_from_voicesnz() 

    # await get_events_from_northlandnz()
    # await get_events_from_venuesotautahi()
    # await get_events_from_taupowinterfestival() 
    # await get_events_from_jazz()dd 
    # await get_events_from_nzso() 
    # await get_events_from_crankworx() 
    # await get_events_from_mytauranga()  
    await get_events_from_neckofthewoods()
    # await get_events_from_crownrangelounge() 
    # await get_events_from_galatos()
    # await get_events_from_bayvenues()  
    # await get_events_from_dingdongloungenz()
    # await get_events_from_totarastreet()
    # await get_events_from_comedyfestival()
    # await get_events_from_valhallatavern()
    # await get_events_from_powerstation()
    # await get_events_from_rotoruanui() 
    # await get_events_from_wellingtonnz()
    # await get_events_from_hollywoodavondale()
    # await get_event_from_plonkwinebar()
    #     await get_event_from_yonderqt()
    # await get_event_from_rnzb()
    # await get_event_from_forummelbourne()
    # await get_event_from_eccles()
    # await get_event_moshtix()
    # await get_event_moshtixAu()
    # await get_event_ticketfairyNz()
    # await get_event_ticketfairyAu()
    # await get_event_enmoretheatreAu()
    # await get_event_aucklandmuseum()
    # await get_event_metrotheatre()
    # await get_event_paraoa()
    # await get_event_get_tepapaevents()
    # await get_event_manawatunz()
    # await get_event_pumphouse()
    # await get_event_mustdobrisbane()
    # await get_event_lovetaupo()
    # await get_event_bachmusica()
    # await get_event_worldofwearableart()
    # await get_event_comedy()
    # await get_event_circa()
    # await get_event_basementcinema()
    # await  get_event_from_iticket()  
    # await get_event_from_tuningfork()
    # await get_events_from_theincubator() 
    # await get_events_from_cabana()
    # await get_events_from_arollingstone()
    # await get_event_from_ponsonbysocialclub()
    # await get_event_aucklandartgallery()
    # await get_event_bandsintown() 
    # await get_event_unitedcinemas() 
    # await get_event_academycinemas() 
    # await get_event_tivolicinema() 
    # await get_event_homegrown()
    # await get_event_wildfortaranaki()
    # await get_event_waikatonz()
    # await get_event_govettbrewster()
    # await get_event_wunderbar()
    # await get_event_dunedinnz()
    # await get_event_from_thetotehotel()
    # await get_events_from_festivaloflights()
    # await  get_events_from_aaaticketing()
    # await get_event_croxtonparkhotel()
    # await get_event_from_brisbane() 
    # await get_event_from_bohmpresents()
    # await get_event_from_cornerhotel() 
#     await get_event_lakehousearts() 
#     await get_event_byronbay()
#     await get_event_taranaki()  
#     await get_event_abstract() 
#     await get_event_libertystage()
#     await get_event_silkyotter()


  #  print('#')
if __name__ == "__main__":
  print("scraping sever is running now")
  with open("/home/ubuntu/scraping_guidelive/test_scraper.log", "a") as log_file:
    log_file.write(f"The scraping start has been run. {datetime.now()}\n")
  asyncio.run(scrape_events())

  with open("/home/ubuntu/scraping_guidelive/test_scraper.log", "a") as log_file:
    log_file.write(f"Scraping had been end  at {datetime.now()}\n")
  sys.exit(0)