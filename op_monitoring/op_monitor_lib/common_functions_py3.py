
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import time
import statistics


class  Common_Functions(object):

   def __init__(self,site_data,qs,handlers):
       self.site_data = site_data
       self.qs = qs
       self.handlers = handlers
       self.one_day = 3600.*24.
       self.one_week = self.one_day*7.
       self.one_month = self.one_day*30.
       self.one_hour = 3600.
       

   def find_all_containters(self):
       query_list = [] 
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       query_list = self.qs.add_match_terminal( query_list,relationship = "PROCESSOR" )
       processor_sets, processor_lists = self.qs.match_list(query_list)  
       return_value = {}
       for i in processor_lists:
          return_value[i["name"]] = self.find_containers(i["name"])
       return return_value
 
   
       
   def find_processors(self):
       query_list = []
       
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       query_list = self.qs.add_match_terminal( query_list,relationship = "PROCESSOR" )
       processor_sets, processor_lists = self.qs.match_list(query_list)  
       return_value = []
       for i in processor_lists:
          return_value.append(i["name"])
       return return_value
   
   def find_containers(self,processor_name):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       query_list = self.qs.add_match_terminal( query_list,relationship = "PROCESSOR",label = processor_name )
       processor_sets, processor_lists = self.qs.match_list(query_list)  
       return_value = []
       processor_data = processor_lists[0]
       return processor_data[ "containers"]

   def generate_structures_with_processor_container(self,processor_list,key_list,hash_flag = True):
       processor_ds = {}
       
       for i in processor_list:
           containers = self.find_containers(i)
           #print("containers",containers)
           container_ds = {}   
           for j in containers:
                      
               #print(i,j)
               query_list = []
               query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
               query_list = self.qs.add_match_relationship( query_list,relationship = "PROCESSOR",label = i )
               query_list = self.qs.add_match_relationship( query_list,relationship = "CONTAINER",label = j )
               query_list = self.qs.add_match_terminal( query_list,relationship = "PACKAGE",label="DATA_STRUCTURES" )
               package_sets, package_sources = self.qs.match_list(query_list)  
               package = package_sources[0]     
               data_structures = package["data_structures"]
               #print("data_structures",data_structures.keys())
               generate_handlers = Generate_Handlers( package, self.qs )
               temp = {}
               for k in key_list:
                   if hash_flag == True:
                      temp[k] = generate_handlers.construct_hash(data_structures[k] )
                   else:
                      temp[k] = generate_handlers.construct_redis_stream_reader(data_structures[k] )
               container_ds[j] = temp
           processor_ds[i] = container_ds
       #print("pocessor_ds",processor_ds)
      
       return processor_ds


   
   def generate_structures_with_processor(self,processor_list,search_list,key_list,hash_flag = True):
       return_value = {}
      
       
       for i in processor_list:
           #print(i)
           query_list = []
           query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
 
           query_list = self.qs.add_match_relationship( query_list,relationship = "PROCESSOR",label = i )
           for j in range(0,len(search_list)-1):
               query_list = self.qs.add_match_relationship( query_list,relationship = search_list[j] )
           if type(search_list[-1]) == list:
               query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1][0],label = search_list[-1][1] )
           else:
               query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1] )
           package_sets, package_sources = self.qs.match_list(query_list)  
           package = package_sources[0]     
           data_structures = package["data_structures"]
           print("data_structures",data_structures.keys())
           generate_handlers = Generate_Handlers( package, self.qs )
           temp = {}
           for k in key_list:
               if hash_flag == True:
                   temp[k] = generate_handlers.construct_hash(data_structures[k] )
               else:
                   temp[k] = generate_handlers.construct_redis_stream_reader(data_structures[k] )
           return_value[i] = temp
           
       return return_value
           
           
   def generate_structures_without_processor(self,search_list,key_list,hash_flag = True):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       for i in range(0,len(search_list)-1):
           if type(search_list[-1]) == list:
               query_list = self.qs.add_match_relationship( query_list,relationship = search_list[i][0],label = search_list[i][1] )
           else:
               query_list = self.qs.add_match_relationship( query_list,relationship = search_list[i] )
           
       if type(search_list[-1]) == list:
          query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1][0],label = search_list[-1][1] )
       else:
           query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1] )
       
       package_sets, package_sources = self.qs.match_list(query_list)  
       package = package_sources[0]     
       data_structures = package["data_structures"]
       #print("data_structures",data_structures.keys())
       generate_handlers = Generate_Handlers( package, self.qs )
       return_value = {}
       for j in key_list:
           if hash_flag == True:
               return_value[j] = generate_handlers.construct_hash(data_structures[j] )
           else:
               return_value[j] = generate_handlers.construct_redis_stream_reader(data_structures[j] )
       return return_value

 
   def generate_rpc_queue(self,search_list,key):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       for i in range(0,len(search_list)-1):
           if type(search_list[-1]) == list:
               query_list = self.qs.add_match_relationship( query_list,relationship = search_list[i][0],label = search_list[i][1] )
           else:
               query_list = self.qs.add_match_relationship( query_list,relationship = search_list[i] )
           
       if type(search_list[-1]) == list:
          query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1][0],label = search_list[-1][1] )
       else:
           query_list = self.qs.add_match_terminal( query_list,relationship = search_list[-1] )
       
       package_sets, package_sources = self.qs.match_list(query_list)  
       package = package_sources[0]     
       data_structures = package["data_structures"]   
       queue_name = data_structures[key]['queue']
       print("queue_name",queue_name)
       generate_handlers = Generate_Handlers( package, self.qs )
       rpc_client = generate_handlers.construct_rpc_client( )
       rpc_client.set_rpc_queue(queue_name)
       return rpc_client
       
   
       
   def general_hash_iterator(self,processor,check_function,hash_obj):

       
       status_map = {}
       error_count = 0 
            
       for i in hash_obj.hkeys():
          
           store_flag, status,result =  check_function(hash_obj.hget(i))
         
           if store_flag == False:
              continue
           status_map[i] = [status,result]
           if status == False:
               error_count = error_count +1
               
           
       if error_count >0:
          print("failure",i)
          
          self.handlers["SYSTEM_STATUS"].hset(processor,False)
     
       return [error_count, status_map]


   def check_for_error_flag(self,subsystem,new_data):
      
       if new_data[0] > 0: # error count != 0
          self.handlers["SYSTEM_STATUS"].hset(subsystem,False)
          return False
       return True
          


  
   def  detect_new_alert(self,subsystem,new_data,ref_data):
       #print("------------------------------------------")
       #print("new_data",new_data)
       #print("-----------------------------------------")
       #print("ref_data",ref_data)
       #print("-----------------------------------------")
       if new_data[0] != ref_data[0]: # difference in error count
           print("difference in error count")
           self.handlers["SYSTEM_STATUS"].hset(subsystem,False)
           return False       
       
       if len(new_data) != len(ref_data):
          print("difference in lenght")
          return True # wait next time for match
       #
       # Now We make sure all enities are in same state
       #
       #       
       ref_itemized_data = ref_data[1]
       new_itemized_data = new_data[1]
       for i in  new_itemized_data.keys():
          if i not in ref_itemized_data:  # different entites between these two runs
              print("difference in items",i)
              print(new_itemized_data.keys())
              print(ref_itemized_data.keys())
              
              return True  # wait for next run
       for i in  new_itemized_data.keys():
           ref_state = ref_itemized_data[i][0]
           new_state = new_itemized_data[i][0]
           if new_state != ref_state:
              print("state mismatch",i)
              self.handlers["SYSTEM_STATUS"].hset(subsystem,False)
              return False
       #print("subsystem is true")
       return True

   def general_stream_handler(self,comparison_handler,stream_handler,duration):# all keys
       raw_data = stream_handler.revrange(time.time(),time.time()-duration, count=1000)
       

       stream_data = []
       for i in raw_data:
           stream_data.append(i["data"])
        
       if len(stream_data) == 0:
          return [False,json.dumps(stream_data)]       
       return_value = comparison_handler(stream_data)
       return return_value
       
           
   def filter_stream_values(self,keys,input_stream):
       return_value = {}
       for j in keys:
           return_value[j] = []
       for i in input_stream:
           for j in keys:
               if j in i:
                   return_value[j].append(i[j])
 
       return return_value           

   def log_alert(self,subsystem,data):
       print("****************************** log alert *********************",subsystem,data)
       self.handlers["SYSTEM_ALERTS"].push(data={"subsystem":subsystem,"data":data})  
   
        
 
   def determine_statistics(self,data):
       
       data_list = []
       for item in data:
           data_list.append(float(item))
       return_value = {}
       return_value["mean"] = statistics.mean(data_list)
       return_value["median"] = statistics.median(data_list)
       return_value["std"] = statistics.stdev(data_list)
       return_value["max"] = max(data_list)
       return_value["min"] = min(data_list)
       return return_value
       
   def count_errors(self, data):
   
       error_count = 0
       for i,item in data.items():
           
           if item[0] != True:
              error_count = error_count +1
       return error_count