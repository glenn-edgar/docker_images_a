#
#
# File: eto.py
#
#

from eto_py3.wunderground_personal_weather_station_py3 import Wunder_Personal
from eto_py3.messo_handlers_py3 import Messo_ETO
from eto_py3.messo_handlers_py3 import Messo_Precp
from eto_py3.cimis_spatial_py3 import CIMIS_SPATIAL
from eto_py3.cimis_handlers_py3 import CIMIS_ETO
from eto_py3.hybrid_handler_py3 import Hybrid_Calculator
from eto_py3.eto_init_py3 import Initialize_ETO_Accumulation_Table
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from file_server_library.file_server_lib_py3 import Construct_RPC_Library




ONE_DAY = 24 * 3600


class Eto_Management(object):
    def __init__(self,  eto_sources, package,site_data,qs,initial_accumulation_tables ):

        self.eto_sources = eto_sources
        self.package  = package
        self.site_data = site_data
        self.qs = qs
        
        self.generate_redis_handlers()
        self.eto_hash_table =  self.ds_handlers["ETO_ACCUMULATION_TABLE"]
        self.initialize_values()
        self.generate_calculators()
        initial_accumulation_tables.initialize_eto_tables(self.eto_hash_table)
        #self.new_day_rollover()

                               
    def generate_redis_handlers(self):
        self.handlers = {}
        data_structures = self.package["data_structures"]
        generate_handlers = Generate_Handlers(self.package,self.qs)
        self.ds_handlers = {}
        self.ds_handlers["EXCEPTION_VALUES"] = generate_handlers.construct_hash(data_structures["EXCEPTION_VALUES"])
        self.ds_handlers["ETO_VALUES"] = generate_handlers.construct_hash(data_structures["ETO_VALUES"])
        self.ds_handlers["RAIN_VALUES"] = generate_handlers.construct_hash(data_structures["RAIN_VALUES"])
        self.ds_handlers["ETO_CONTROL"] = generate_handlers.construct_hash(data_structures["ETO_CONTROL"])
        self.ds_handlers["ETO_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["ETO_HISTORY"])
        self.ds_handlers["RAIN_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["RAIN_HISTORY"] )
        self.ds_handlers["EXCEPTION_LOG"] = generate_handlers.construct_stream_writer(data_structures["EXCEPTION_LOG"] )
        self.ds_handlers["ETO_ACCUMULATION_TABLE"] = generate_handlers.construct_hash(data_structures["ETO_ACCUMULATION_TABLE"])

    def initialize_values(self):
         if self.ds_handlers["ETO_CONTROL"].hget("ETO_UPDATE_FLAG") == None:
             self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",0)
         if self.ds_handlers["ETO_CONTROL"].hget("ETO_LOG_FLAG") == None:
             self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",0)

     

        
    def generate_calculators(self):
        for data in self.eto_sources:
            print(data["type"])
            if data["type"] == "WUNDERGROUND":
               data["calculator"] = Wunder_Personal(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "CIMIS_SAT":
               data["calculator"] = CIMIS_SPATIAL(data, self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "CIMIS":
               data["calculator"] = CIMIS_ETO(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "MESSO_ETO":
               data["calculator"] = Messo_ETO(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "MESSO_RAIN":
               data["calculator"] = Messo_Precp(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "hybrid":
               data["calculator"] = Hybrid_Calculator(data,self.eto_sources,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
            #assert 0,"data type is not recognized "+data["type"] 
        
       

    def new_day_rollover( self, *parameters ):
         
         self.ds_handlers["EXCEPTION_VALUES"].delete_all()
       
         
         self.ds_handlers["ETO_VALUES"].delete_all()
         self.ds_handlers["RAIN_VALUES"].delete_all()
         
         self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",0)
         self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",0)
         self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_VALUE",None)
         return "DISABLE"

    def make_measurement(self, *parameters):
       
        for source in self.eto_sources:
            print("source",source)
            if "calculator" in source:
                try:
                    source["calculator"].compute_previous_day()
                except Exception as tst:
                    
                    print("exception",source["name"],tst)
                    self.ds_handlers["EXCEPTION_VALUES"].hset(source["name"],str(tst))
        print("calculator done")       
             

    def update_eto_bins(self, *parameters):
        #print(int(self.ds_handlers["ETO_CONTROL"].hget("ETO_UPDATE_FLAG")))
        if int(self.ds_handlers["ETO_CONTROL"].hget("ETO_UPDATE_FLAG")) == 1:
            return True
        self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",1) 
        # find eto with lowest priority
        eto = self.find_eto()
        self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_VALUE",eto)
        if eto ==  None:
           return False
        self.reference_eto = eto
        rain = self.find_rain()
        self.reference_rain = self.find_rain()
        
        for i in self.eto_hash_table.hkeys():
           
           new_value = float(self.eto_hash_table.hget(i)) + float(eto)
           print("eto_update",i,new_value)
           self.eto_hash_table.hset(i,new_value)
        print("logging sprinkler_data")
        self.log_sprinkler_data()
        return True
        


    def log_sprinkler_data(self,*parameters):
       if int(self.ds_handlers["ETO_CONTROL"].hget("ETO_LOG_FLAG")) == 1:
            return  
       eto_data = self.assemble_data("eto",self.ds_handlers["ETO_VALUES"])
       if len(eto_data.keys()) == 0:
          return       

       self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",1) 

       print("logging eto data")
       self.ds_handlers["ETO_HISTORY"].push(data = eto_data) 
       rain_data = self.assemble_data("rain",self.ds_handlers["RAIN_VALUES"])
       if len(rain_data.keys()) > 0:  
           print("loging rain data")       
           self.ds_handlers["RAIN_HISTORY"].push(data = rain_data) 
       exception_data = self.ds_handlers["EXCEPTION_VALUES"].hgetall()
       print("exception data",exception_data)
       if len(eto_data.keys()) > 0:
            self.ds_handlers["EXCEPTION_LOG"].push(data=exception_data)

    def find_eto(self):
       eto_data = self.ds_handlers["ETO_VALUES"].hgetall()
       
       ref_priority = 1000000 # large starting number
       eto_value = None
       for i ,data in eto_data.items():
           print("################## i data @@@@@@@@@@@@@@@@@@@@@",i,data)
           if data["priority"] < ref_priority:
               ref_priority = int(data["priority"])
               eto_value = float(data["eto"])
               
               
       
       return eto_value

    def find_rain(self):
       rain_data = self.ds_handlers["RAIN_VALUES"].hgetall()
       
       ref_priority = 1000000 # large starting number
       for i ,data in rain_data.items():
          
           if data["priority"] < ref_priority:
               ref_priority = int(data["priority"])
               rain_data = float(data["rain"])
       
       return rain_data       
       
 
    def assemble_data(self,field_key,hash_handler):
       data = hash_handler.hgetall()
       return_value = {}
       for key , item in data.items():
         
          return_value[key] = item[field_key]
       return return_value
      
       
       
def replace_keys( redis_site_data,elements ):
   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_password_db"], decode_responses=True)
   for i in elements:
      
       temp = i["access_key"]
       api_key = redis_handle.hget("eto",temp)
      
       i["access_key"] = api_key



def construct_eto_instance(qs, site_data ):

    #
    #
    # find nodes associated with WEATHER_STATIONS
    #
    #
    
    #
    #  Find "WS_STATION" nodes
    #
    #
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "WS_STATION" )
                                        
    eto_sets, eto_sources = qs.match_list(query_list) 
    
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"WEATHER_STATION_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)  
     
    

    
    
    #
    # Replace symbolic keys with actual api keys
    #
    replace_keys(site_data, eto_sources)
    file_server_library = Construct_RPC_Library(qs,site_data)
    initial_accumulation_tables = Initialize_ETO_Accumulation_Table(file_server_library)

   
   
    
    eto = Eto_Management(eto_sources, package_sources[0],site_data,qs,initial_accumulation_tables )
    
    
    
  

    return eto


def add_eto_chains(eto, cf):

    cf.define_chain("test_generator",False)
    cf.insert.log("send Day Tick")
    cf.insert.send_event("DAY_TICK")
    cf.insert.terminate()

    cf.insert.wait_tod_le( hour =  4 )
    cf.insert.send_event("DAY_TICK")
    cf.insert.wait_tod_ge( hour =  5 )
    cf.insert.reset()

    cf.define_chain("eto_time_window", True)
    cf.insert.log("Waiting for day tick")
    cf.insert.wait_event_count( event = "DAY_TICK" )
    cf.insert.log("Got Day Tick")
    cf.insert.one_step(eto.new_day_rollover)
    cf.insert.reset()

    cf.define_chain("enable_measurement", True)
    cf.insert.log("starting enable_measurement")
    cf.insert.wait_tod_ge( hour =  8 )
    cf.insert.enable_chains(["eto_make_measurements"])
    cf.insert.log("enabling making_measurement")
    cf.insert.wait_tod_ge(hour=11)
    cf.insert.enable_chains(["update_eto_bins"])
    cf.insert.log("enable_update_eto_bins")
    
    cf.insert.wait_tod_ge( hour =  23 )
    cf.insert.disable_chains(["eto_make_measurements","update_eto_bins"])
    
    cf.insert.wait_event_count( event = "DAY_TICK" )
    cf.insert.reset()

    cf.define_chain("update_eto_bins", False)
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 8)
    cf.insert.log("updating eto bins")
    cf.insert.wait_function( eto.update_eto_bins )
    cf.insert.disable_chains(["eto_make_measurements"])
    cf.insert.terminate()
 
    
    
    cf.define_chain("eto_make_measurements", False)
    cf.insert.log("starting make measurement")
    
    cf.insert.one_step( eto.make_measurement )

    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 1)
    cf.insert.log("Receiving minute tick")
    
    cf.insert.reset()



if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    
    from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("/data/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close() 
    redis_site = json.loads(data)
     
    #
    # Setup handle
    # open data stores instance
    
    
     
       
    qs = Query_Support( redis_site )
    
  
    
    eto = construct_eto_instance( qs, redis_site)
   

  
    #
    # Adding chains
    #

    cf = CF_Base_Interpreter()
    add_eto_chains(eto, cf)
    #
    # Executing chains
    #
    
    cf.execute()

else:
  pass
  
