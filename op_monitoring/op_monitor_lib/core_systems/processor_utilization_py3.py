from op_monitor_lib.common_class_py3 import Common_Class
import json
import time
import statistics

class Processor_Utilization(Common_Class):
  
   def __init__(self, subsystem_name,common_obj ):
       Common_Class.__init__(self,subsystem_name,common_obj )
       self.construct_data_structures()
       self.handlers = common_obj.handlers
       self.common_obj.one_month
       
       
     
          
   
   def execute_day(self):
       print("execute_hour")
       web_display = {}
       error_hash  = {}
       
      
       
       new_data = {} 
       for i in self.processors:
          new_data[i] = {}
          new_data[i]["free_cpu"]    = self.common_obj.general_stream_handler(i, self.analyize_free_cpu,self.watch_handlers[i]["FREE_CPU"],duration=self.common_obj.one_day, fields=['%idle'])# all keys
          new_data[i]["ram"]         = self.common_obj.general_stream_handler(i,self.analyize_ram,self.watch_handlers[i]["RAM"],duration=self.common_obj.one_month, keys=[])# all keys
          new_data[i]["disk_space"]  = self.common_obj.general_stream_handler(i,self.analyize_disk_space,self.watch_handlers[i]["DISK_SPACE"],duration=self.common_obj.one_month, keys=[])# all keys
          new_data[i]["temperature"] = self.common_obj.general_stream_handler(i,self.analyize_temperature,self.watch_handlers[i]["TEMPERATURE"],duration=self.common_obj.one_day, keys=[])# all keys
          
      
           
       
       
       
       #print("new_data",new_data)
       status = True
       self.handlers["SYSTEM_STATUS"].hset(self.subsystem_name,True)
       ref_total_data = self.handlers["MONITORING_DATA"].hget(self.subsystem_name)
       if ref_total_data == None:
          ref_total_data = new_data
       for i in self.processors:
           
           ref_data = ref_total_data[i]
           #print("ref_data",i,ref_data)
           if ref_data == None:
              print("continue",i)
           else:   
               status = status and self.common_obj.detect_new_alert(self.subsystem_name,new_data[i]["web_display"],ref_data["web_display"])
               status = status and self.common_obj.check_for_error_flag(self.subsystem_name,new_data[i]["error_hash"])
       self.handlers["MONITORING_DATA"].hset(self.subsystem_name,new_data)
       
       print("status",status)
       if status == False: # change is monitoring status
           print("log alert")
           self.common_obj.log_alert(self.subsystem_name,new_data)
           
         
  

   def construct_data_structures(self):
       
       self.processors = self.common_obj.find_processors()
       search_list = [["PACKAGE","SYSTEM_MONITORING"]]
       data_structures = ["FREE_CPU","RAM","DISK_SPACE","TEMPERATURE"]
       self.watch_handlers = self.common_obj.generate_structures_with_processor(self.processors,search_list,data_structures,hash_flag = False)
      
              


   def analyize_free_cpu( self,data):
       data = data['%idle']
       return_data = {}
       return_data["mean"] = statistics.mean(data)
       return_data["median"] = statistics.median(data)
       return_data["std"] = statistics.stdev(data)
       return_data["variance"] = statistics.variance(data)
       return_data["max"] = max(data)
       return_data["min"] = min(data)
       print("return data",return_data)
       exit()
      
       
       
   def analyize_ram( self,data):
       #print("WEB_DISPLAY_DICTIONARY",data)
       if data["error"] == False:
          flag  = True
       else:
          flag = False
       return [True,flag, json.dumps(data)]
       

   def analyize_disk_space( self,data):
       #print("WEB_DISPLAY_DICTIONARY",data)
       if data["error"] == False:
          flag  = True
       else:
          flag = False
       return [True,flag, json.dumps(data)]
       
   def analyize_temperature( self,data):
       #print("WEB_DISPLAY_DICTIONARY",data)
       if data["error"] == False:
          flag  = True
       else:
          flag = False
       return [True,flag, json.dumps(data)]
       




           
   




           
   



           
   




           
   
