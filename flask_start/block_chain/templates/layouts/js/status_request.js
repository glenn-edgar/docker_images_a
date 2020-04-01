function status_request_function()
{
   json_object = {}


   ajax_get( '/ajax/status_update', "Data Not Fetched", status_update )
 
   
}
  
                  
function status_update( data )
{
       var temp
       var temp_1
       var tempDate
       
       //alert(JSON.stringify(data))
       //alert(Object.keys(data))
       var date = new Date( data["TIME_STAMP"]  * 1000);
       tempDate = new Date()
       
       $("#time_stamp").html("Time:  "+tempDate.toLocaleDateString() + "   " + tempDate.toLocaleTimeString() )

       $("#controller_time_stamp").html("Ctr Time: "+ date.toLocaleDateString() + "   " + date.toLocaleTimeString() )
       $("#flow_rate").html("Current Flow Rate: "+parseFloat(data.MAIN_FLOW_METER).toFixed(2));
       $("#plc_flow_rate").html("PLC Flow Rate: "+parseFloat(data.PLC_FLOW_METER).toFixed(2));
       $("#cleaning_rate").html("Cleaning Flow Rate:  "+parseFloat(data.CLEANING_FLOW_METER).toFixed(2));
       $("#schedule").html("Schedule: "+data["SCHEDULE_NAME"])
       $("#step").html("Step:   "+data["STEP"])
       $("#time").html("Step Time:  "+data["RUN_TIME"])
       $("#duration").html("ELASPED_TIME: "+ data["ELASPED_TIME"]) 
       $("#rain_day").html("Rain Day: "+data["RAIN_FLAG"])
       $("#irrigation_current").html("Irrigation  Current:"+parseFloat(data.PLC_IRRIGATION_CURRENT).toFixed(2))
       $("#equipment_current").html("Equipment  Current:  "+parseFloat(data.PLC_EQUIPMENT_CURRENT).toFixed(2))
       $("#pump_input_current").html("Pump Input Current: "+parseFloat(data.INPUT_PUMP_CURRENT).toFixed(2))
       $("#pump_output_current").html("Pump Output Current: "+parseFloat(data.OUTPUT_PUMP_CURRENT).toFixed(2))
       $("#well_pressure").html("Well Pressure:  "+parseFloat(data.WELL_PRESSURE).toFixed(2))
       $("#master_valve").html("Master Valve: "+data.MASTER_VALVE )
       $("#eto_management").html("ETO Management: "+data.ETO_MANAGEMENT )
 
       $("#suspend").html("Suspension State:  "+data.SUSPEND )
       $("#clean_filter_limit").html("Filter Cleaning Limit (Gallon):  "+parseFloat(data.CLEANING_INTERVAL).toFixed(2) )
       $("#clean_filter_value").html("Filter Cleaning Accumulation (GPM):  "+parseFloat(data.CLEANING_ACCUMULATION).toFixed(2 ))


}

$(document).ready(function(){
    $("#status_request").click(function(){
        $("#status_modal").modal("show");
        status_request_function()
    });
    

});

/*
function system_state_init()
{    var g,h,i
     var alarm_data;
     var  queue_interval_id;
     var  nintervalId;
     var data = [];
     var conversion_factor_index;
     var conversion_factor;
     var conversion_factor_array;


 
    

   $( "#status_request"  ).bind({ popupafteropen: status_request_function })
   
   

  } 
*/