
import datetime
import msgpack
from op_monitor_lib.common_class_py3 import Common_Class
import json
import time


class Block_Chain_Monitor(Common_Class):
  
   def __init__(self, subsystem_name,common_obj ):
       Common_Class.__init__(self,subsystem_name,common_obj )
       
       self.handlers = common_obj.handlers
       self.setup_block_chain_rpc_queue()
       
       
       
       
       
     
   def execute_15_minutes(self):
       print("execute_15_minutes")  
       self.handlers["SYSTEM_STATUS"].hset(self.subsystem_name,True)
       status,data = self.do_block_chain_test()
       if status == True:
          new_data = [0,{"rpc_test":[True,json.dumps(data)]}]
       else:
          new_data = [1,{"rpc_test":[False,json.dumps(data)]}]
       print(new_data)
       
       print(new_data)
       
       self.compare_and_log_data(new_data)
       
  
   def compare_and_log_data(self,new_data):   
       
       #print("new_data",new_data)
       
       
       ref_total_data = self.handlers["MONITORING_DATA"].hget(self.subsystem_name)
       #print("ref_total_data",ref_total_data)
       if ref_total_data == None:
          ref_total_data = new_data
       status = True   
 
       status = status and self.common_obj.detect_new_alert(self.subsystem_name,new_data,ref_total_data)
              
       self.handlers["MONITORING_DATA"].hset(self.subsystem_name,new_data)   
 
       if status == False: # change is monitoring status
           print("log alert")
           self.common_obj.log_alert(self.subsystem_name,new_data)
  
  

   def setup_block_chain_rpc_queue(self):
       
       search_list = ["CLOUD_BLOCK_CHAIN_SERVER","PACKAGE"]
       self.rpc_client = self.common_obj.generate_rpc_queue(search_list,key = "BLOCK_CHAIN_RPC_SERVER")
      
   
   def do_block_chain_test(self):
       return_value = True
       try:
          print("list_data_bases")
          parameters = {}
          test_value  = self.rpc_client.send_rpc_message("fetch_current_block_number",[])
         
          return_value =[True,{"block_number":test_value}]          
       except:
          
          print("exception failure")
          return_value  = [False,"Failure"]      
       return return_value
       
       
       

