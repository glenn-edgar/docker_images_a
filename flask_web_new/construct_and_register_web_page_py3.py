





class Construct_And_Register_Pages(object):
  
    def __init__(self,parent_self):
        self.parent_self = parent_self
        self.web_properties = self.parent_self.server_properties["menu"]
        base_html = ""
        self.parent_self.web_map = {}
        self.ajax_handlers = {}    
        self.parent_self.add_ajax_handler = self.add_ajax_handler
        self.constuct_and_register(self.parent_self.web_map, base_html,self.web_properties)
        
    def add_ajax_handler(self,name,process,methods):
        temp = {}
        temp['name'] = name
        temp['process'] = process
        temp['methods'] = methods
        self.ajax_handlers[name] = temp
    
    
    
    def register_ajax_handlers(self):
        for i,item in self.ajax_handlers.items():
            self.parent_self.app.add_url_rule(item["name"],item["name"],item["process"],methods=item["methods"])
        
    def constuct_and_register(self,web_map, base_html, web_properties):

       children = web_properties["children"]
       
       for i in children:
          
          link = base_html+"/"+i["display_name"]
          
          if (i["type"] == True) and (len(i["children"])):
             self.constuct_and_register(web_map,link ,i)

          elif i["type"] == False:
             #instanciate web_class
             class_name = i["class_name"]
            
             class_object = self.parent_self.class_map[class_name]
             
             class_instanciated = class_object(self.parent_self,i)
             
             class_instanciated.construct_web_page()
             web_list = link.split("/")
             web_name = "_".join(web_list)
             self.parent_self.app.add_url_rule(link,web_name,class_instanciated.render_page)
             self.parent_self.web_map[link]  = class_instanciated
       self.register_ajax_handlers()
      