from __future__ import print_function
from __future__ import division
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import time

# List your parameters as strings
# Get area numbers by searching StreetEasy for your desired location and looking in the address bar
# Also use search bar to identify if new parameters are needed
price = "3500-6000"
area = "117,109,107"
min_beds = "1"
no_fee = "" # 1 gets only no fee apartment listings; leave blank if no preference 

def create_search_url(price, area, min_beds, no_fee):
    start = 'http://streeteasy.com/for-rent/nyc/status:open'
    price_param = "%7Cprice:"
    area_param = "%7Carea:"
    beds_param = "%7Cbeds%3E="
    fee_param = "%7Cno_fee:"
    page_param = "?page="
    url = start + price_param + price + area_param + area + beds_param + min_beds + fee_param + no_fee + page_param
    return url

search_url = create_search_url(price, area, min_beds, no_fee)

def create_page_url(page):
    return  search_url + str(page)

# Get number of listings from first search page
# FYI urllib: http://stackoverflow.com/questions/2792650
url = create_page_url(1)
r = urlopen(url)
if r.getcode() == "404":
    time.sleep(1)
else:
    r = r.read()
    soup = BeautifulSoup(r,'html.parser')
    num_results = soup.find_all('div',{'class':'result-count first'})[0].text
    # 14 results on a page but the top 2 featured don't count towards total
    num_pages = int(int(num_results)/12)

# Create list of links to each listing page
links = []
for page in range(1, num_pages + 1):
    print("Pages percent done: ", round(page/num_pages,3)*100)
    url = create_page_url(page)
    r = urlopen(url)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        r = r.read()
        soup = BeautifulSoup(r,'html.parser')
        listings = soup.find_all('div',{'class':'left-two-thirds items item-rows listings'})[0]
        for i in range(14):
            try:
                links.append(listings.find_all('div', {'class': 'details row'})[i].find('a', href = True)['href'])
            except IndexError:
                # Deals with final page not having the full 14 results, probably a better way
                pass

# Go to each page and extract date available 
avails = {}
for i, link in enumerate(links):
    print("Dates percent done: ", round(i/len(links),3)*100)
    r =urlopen("http://streeteasy.com" + link)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        r = r.read()
        soup = BeautifulSoup(r,'html.parser')
        div_set = soup.find_all('div',{'class':'right-two-fifths'})[0].find_all('h6')
        text_div_set = [x.text for x in div_set]
        if "Available on" in text_div_set:
            index = text_div_set.index("Available on")
            date = div_set[index].parent.text.split("\n")[2].strip()
            avails["http://streeteasy.com" + link] = date
        elif "Listing Availability" in text_div_set:
            index = text_div_set.index("Listing Availability")
            date = div_set[index].parent.text.split("\n")[2].strip()
            avails["http://streeteasy.com" + link] = date
        else:
            avails["http://streeteasy.com" + link] = np.nan

# Go to each page and extract price
prices = {}
for i, link in enumerate(links):
    print("Prices percent done: ", round(i/len(links),3)*100)
    r =urlopen("http://streeteasy.com" + link)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        r = r.read()
        soup = BeautifulSoup(r,'html.parser')
        div_set = soup.find_all('div',{'class':'price '})[0]
        price = div_set.parent.text.split("\n")[3].strip()
        prices["http://streeteasy.com" + link] = price

# Create dataframe from results
df1 = pd.DataFrame.from_dict(avails, orient = "index").reset_index()
df1.columns = ['link', 'avail']
df2 = pd.DataFrame.from_dict(prices, orient = "index").reset_index()
df2.columns = ['link', 'price']
df = pd.merge(df1, df2, on = 'link')
df = df.sort("avail", na_position = "last")

# Write to file with date in filename
today = datetime.datetime.now().date().strftime("%m_%d")
df.to_csv(today + "_listings.csv", index = False) 