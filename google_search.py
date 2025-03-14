import os 
import json 
import requests 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #FastAPI 
import uvicorn
from typing import Union 
from fastapi import FastAPI,File,UploadFile,Request,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
             #Search engine tool 
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from urllib.parse import urljoin
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
app = FastAPI() 

result_search = {} #Get the result search 
result_pdf_search = {} #Get the result pdf search 

#url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
# Define headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

@app.get("/total_regular_search")
def result_regular_search():

     return result_search #Get th result regular search 

@app.get("/total_pdf_search")
def resultpdf_search():

     return  result_pdf_search 
          
@app.post("/post_pdf_search")
async def post_regular_search(request:Request):

      reqsearch = await request.json() 
      print(reqsearch)
      email = reqsearch.get('email') 
      project_name = reqsearch.get('project_name')
      search = reqsearch.get("search_data") 
      print("Current user post search data",email,project_name)
      result_pdf_search.clear() 
      #Checking semantic components search 
      query = f"{search} datasheet PDF"
      url = f"https://www.google.com/search?q={query.replace(' ', '+')}"    
      #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
      # Define headers to mimic a browser request
      response = requests.get(url,headers=headers) #Get the response data of the url header 
      if response.status_code == 200:
                 soup = BeautifulSoup(response.text, "html.parser")
                 # Extract PDF links
                 search_results = soup.select(".tF2Cxc")
                 for result in search_results:
                       title = result.select_one("h3").text if result.select_one("h3") else "No title"
                       link = result.select_one("a")["href"] if result.select_one("a") else "No link"
                       snippet = result.select_one(".VwiC3b").text if result.select_one(".VwiC3b") else "No snippet"
                      
                       # Check if the link is a PDF
                       if link.endswith(".pdf"):
                              print(f"Title: {title}")
                              print(f"PDF Link: {link}\n")
                              print(f"Snippet: {snippet}\n\n")
                              #try:
                              #    print("Create the features data extraction of a component from pdf")
                              #    read_pdf = requests.post("http://192.168.50.247:8478/post_read_pdf_link",json={"email":email,"project_name":project_name,"url":link})
                              #except:
                              #    print("Error pdf reader server fail to request") 

                              if email not in list(result_pdf_search):
                                    print("email account not found")
                                    result_pdf_search[email] = {project_name:{snippet:link}}
                                                                                                                              
                              if email in list(result_pdf_search):
                                     print("email account found")
                                     if project_name not in list(result_pdf_search[email]):
                                            result_pdf_search[email][project_name] = {snippet:link}
                                     if project_name in list(result_pdf_search[email]):
                                         if snippet not in list(result_pdf_search[email][project_name]):
                                                print("Snippet not found inside the project")
                                                result_pdf_search[email][project_name][snippet] = link 

                                         if snippet in list(result_pdf_search[email][project_name]):
                                                print("Snippet found inside the project")
                                                result_pdf_search[email][project_name][snippet] = link                              
      else: 
          print(f"Failed to fetch data. Status code: {response.status_code}")
               
      return result_pdf_search[email]
@app.post("/post_list_ai_select")
async def select_link_by_AI_processing(request:Request):
       reqsearch = await request.json() #get search data request
       print("post link list ai selector: ",reqsearch)
       email = reqsearch.get('email')
       project_name = reqsearch.get('project_name')
       search_data = reqsearch.get('search_data') 
       query = search_data
       url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
       # Define headers to mimic a browser request
       headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
       }
       response = requests.get(url, headers=headers)
       # Check the response status
       if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract search result items
            search_results = soup.select(".tF2Cxc")
            for i, result in enumerate(search_results[:10]):
               title = result.select_one("h3").text if result.select_one("h3") else "No title"
               link = result.select_one("a")["href"] if result.select_one("a") else "No link"
               snippet = result.select_one(".VwiC3b").text if result.select_one(".VwiC3b") else "No snippet"
               # Extract image URL (if available)
               image_tag = result.select_one("img")
               image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else "No image"
               # Ensure image URL is fully qualified
               if image_url and not image_url.startswith('http'):
                   image_url = urljoin("https://www.google.com", image_url)
               print(f"Result {i+1}:")
               print(f"Title: {title}")
               print(f"Link: {link}")
               print(f"Snippet: {snippet}")
               print(f"Image URL: {image_url}\n")
                
       return reqsearch      
@app.post("/post_regular_search")
async def post_pdf_search(request:Request):
       reqsearch = await request.json()
       print(reqsearch)
       email = reqsearch.get('email')
       project_name = reqsearch.get('project_name')
       query = reqsearch.get('search_data') 
       print("current user post pdf search ",email,project_name)
       result_search.clear() 
       #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
       #Processing search data from google
       snappit_ref = {} #get referent list semantic data  
       results = DDGS().text(query, max_results=5)
       print(results)
       for rc in results:
                 print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                 title_data = rc['title']
                 href_data = rc['href']
                 snappit = rc['body']
                 print("Title data: ",title_data)
                 print("url_link: ",href_data)
                 print("snappit: ",snappit)
                 snappit_ref[title_data]  = {href_data:snappit}         
       print(list(snappit_ref.values()))
       #Finding maximum probability match one 
       ref_snap =  list(snappit_ref)
       reqdat = requests.post("http://192.168.50.247:8466/processing_part_match",json={email:{'command':query,'ref_data':ref_snap}})
       print("Semantic selection: ",reqdat.json())              
       selected_reconstruct = {reqdat.json()['max_command']:snappit_ref[reqdat.json()['max_command']]}
       print("Reconstruct_selected ",selected_reconstruct) #Get selected reconstruct 
       if email not in list(result_search):
                              print("Account user is not existing inside the dict")
                              result_search[email] = {project_name:selected_reconstruct} # Get the snippet and link url
       if email in list(result_search):
                              print("Account user is already exist now checking link and snippet")
                              if project_name not in list(result_search[email]):
                                       print("Project name is not in the list")
                                       result_search[email][project_name] = selected_reconstruct
                                        
                              if project_name in list(result_search[email]):
                                       print("Project name is in the list")
                                       result_search[email][project_name] = selected_reconstruct
                                       if reqdat.json()['max_command'] not in list(result_search[email][project_name]):
                                               print("Snippert data is not in the list")
                                               result_search[email][project_name][reqdat.json()['max_command']] = snappit_ref[reqdat.json()['max_command']] 
                                       if reqdat.json()['max_command'] in list(result_search[email][project_name]):
                                               print("Snippet data is in the list")
                                               result_search[email][project_name][reqdat.json()['max_command']]  = snappit_ref[reqdat.json()['max_command']]
                                    
       return result_search[email]
       

if __name__ == "__main__":

         uvicorn.run("google_search:app",host="0.0.0.0",port=9767)


      
