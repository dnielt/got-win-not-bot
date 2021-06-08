import os
import requests
import re
import time
import json
# import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup


# download_folder = os.path.join(
    # "c:", os.sep, "Users", "Daniel", "Desktop", 
    # "2021-05-02 sg pools results", "data")
# download_folder_nfiles = 0
# saved_files = []
# PATH =  os.path.join(
    # "c:", os.sep, "Program Files (x86)", "chromedriver.exe")


options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument("--headless")
PATH =  os.path.join("c:", os.sep, "Program Files (x86)", "chromedriver.exe")
# driver = webdriver.Chrome("./chromedriver", options=options)
driver = webdriver.Chrome(PATH, options=options)


try:
    with open("data.txt") as file:
       results = json.load(file)
except:
    results = {}

new_results = {}
url = ("https://www.singaporepools.com.sg/en/product/"
       "sr/Pages/toto_results.aspx")

# Open SG POOLS RESULTS webpage
driver.get(url)

# draw date button
date_label = driver.find_element_by_xpath("//label[text()='Draw Date']")
menu = date_label.find_element_by_xpath("./..")
options = menu.find_elements_by_xpath(".//option")

# get list of all previous draw dates, and links
draw_date_menu = {i.text: {"querystring": i.get_attribute('querystring'),
                           "value": i.get_attribute('value')} 
                           for i in options}

driver.close()


for key in draw_date_menu:
    draw_date_menu[key]["link"] = f'{url}?{draw_date_menu[key]["querystring"]}'


# visit all draw result links and store results
for key in draw_date_menu:
    if key in results:
        continue
    draw_date_url = draw_date_menu[key]["link"]
    page = requests.get(draw_date_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    winning_numbers_elements = soup.find_all("td", class_=re.compile("^win.$"))
    winning_numbers = [i.get_text() for i in winning_numbers_elements]
    additional_number = [soup.find("td", class_="additional").get_text()]
    
    new_results[key] = {"winning_numbers": winning_numbers, 
                    "additional_number": additional_number}
    print(f"in {draw_date_url}\n"
          f"{key}\n"
          f"winning numbers: {winning_numbers}\n"
          f"additional:{additional_number}")

# final = pd.DataFrame(results).transpose()
# final.to_csv("results.csv")

results.update(new_results)

if new_results:
    with open('data.txt', 'w') as file:
        json.dump(results, file)
    print("updated with new results")
else:
    print("no new results to update")