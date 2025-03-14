import os 
import json 
import requests 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #FastAPI 
import uvicorn
from typing import Union 
from fastapi import FastAPI,File,UploadFile,Request,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

app = FastAPI() 


class_comp_map = {} # Get the class of component mapping semantic search for checking the category and redirect components to the right category  
#Get the list of the category element for semantic component search 
listcategory_elem = {"Vision_system":["Camera"],
"Motion_system":["Servo-motor","Brushless-motor","Stepper-motor","DC-motor"],
"Audio_system":["audio_port"],
"Single_Board_computer":["Single-Board-Computer"],
"Navigation_system":["GPS","Wifilocalization","Cellular-network","Lidar-UART","Lidar-serial","Beacon-nav","Ultra-wideband (UWB)"],
"Sensors":["Mechanical_force-array","Temperature-array","Optical-array","Acoustic-array","Electromagnetic-array"],
"Odometry_system":["imus","encoders","visual-odometry","gps","radar","optic-flow"],
"Communication_system":["communication-network"],
"Microcontroller":["STM32","MSP","ESP32","Arduino"],
"Battery":["Litium-ion","Li-Po"],
"Materials":["Plastic","Metal","Rubber","Composit","Reinforcement"]
} 
#element key to consider from each component data 
mouser_data_keys = [
    'Availability',
    'DataSheetUrl',
    'Description',
    'FactoryStock',
    'ImagePath',
    'Category',
    'LeadTime',
    'Manufacturer',
    'ManufacturerPartNumber',
    'Min',
    'Mult',
    'MouserPartNumber',
    'ProductAttributes',
    'PriceBreaks',
    'ProductDetailUrl',
    'ROHSStatus',
    'AvailabilityInStock',
    'AvailabilityOnOrder',
    'InfoMessages',
    'SurchargeMessages',
    'ProductCompliance'
]

@app.get("/total_search_data")
def get_total_search():
      print("Get total_search")
      return class_comp_map

@app.post("/post_sub_search")
async def sub_searchdata(request:Request):
       reqdat = await request.json() 
       print(reqdat)
       email = reqdat.get("email")
       project_name = reqdat.get("project_name")
       search_dat = reqdat.get("search_data") 
       components_class = reqdat.get('components_class')
       print("Searching data",search_dat)
       #Check the data in mouser electronics or digikey if not found then search in google 
       try:
          print("Search data processing Mouser electronics")
          payload={"email":email,"project_name":project_name,"components_search":search_dat}
          reqdat = requests.post("http://192.168.50.247:8235/mouser_part_search",json=payload).json() 
          print("Mouser search result")
          print(reqdat) 
          if reqdat.get(email).get(project_name).get('NumberOfResult')  > 0:
                       print("Extract the data from the Mouser api data")
                       Parts = reqdat.get(email).get(project_name).get('Parts') # Get the part element data to reforming structure 
                            
                       return Parts                            
          #{"NumberOfResult":0,"Parts":[]}
          if reqdat.get(email).get(project_name).get('NumberOfResult')  == 0:
                       print("Mouser part search error") 
                       #Processing the data of the google search
                       try: 
                           print("Google searching data from URL") 
                           search_google = requests.post("http://0.0.0.0:9767/post_regular_search",json={"email":email,"project_name":project_name,"search_data":search_dat}).json()                       
                           print(search_google)              
                           
                           try:
                              class_category = requests.post("http://192.168.50.247:8466/processing_part_match",json={email:{"command":search_google,"ref_data":list(listcategory_elem)}}).json() 
                              print(class_category)                                 
                              #Get the max value of the 
                              maxcom = class_category['max_command'] 
                              sub_categorydat = requests.post("http://192.168.50.247:8466/processing_part_match",json={email:{"command":search_google, "ref_data":listcategory_elem[maxcom]}}).json()
                              print("Class_component,Sub_category: ",search_dat,maxcom,sub_categorydat.get('max_command'),components_class)
                              if email not in list(class_comp_map):
                                             class_comp_map[email] = {project_name:{search_dat:{maxcom:sub_categorydat}}} 
                              if email in list(class_comp_map):
                                           if project_name not in list(class_comp_map[email]):
                                                            print("project is not in list")
                                                            class_comp_map[email][project_name] = {search_dat:{maxcom:sub_categorydat}}
                                           if project_name in list(class_comp_map[email]):
                                                            print("project is now in list")                                            
                                                            if search_dat not in list(class_comp_map[email][project_name]):
                                                                 if maxcom == components_class:               
                                                                     class_comp_map[email][project_name][search_dat] = {maxcom:sub_categorydat['max_command'],"selected_class":components_class,"logic":True}
                                                                 if maxcom != components_class:
                                                                     class_comp_map[email][project_name][search_dat] = {maxcom:sub_categorydat['max_command'],"selected_class":components_class,"logic":False} 
                                                                  
                                                            if search_dat in list(class_comp_map[email][project_name]):
                                                                 if maxcom == components_class:               
                                                                     class_comp_map[email][project_name][search_dat] = {maxcom:sub_categorydat['max_command'],"selected_class":components_class,"logic":True}
                                                                 if maxcom != components_class:
                                                                     class_comp_map[email][project_name][search_dat] = {maxcom:sub_categorydat['max_command'],"selected_class":components_class,"logic":False} 
                              return class_comp_map 
                           except:
                              print("Processing the components semantic category search ")                            
                           
                           
                       except:
                           print("Error processing data from google search") 
       except:
          print("proessing search data error finding alternative") 
     

if __name__ == "__main__":
   
       uvicorn.run("sub_search_data:app",host="0.0.0.0",port=9443)

