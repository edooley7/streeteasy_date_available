#!/usr/bin/env python3

## StreatEasy Apartment Finder

from __future__ import print_function
from __future__ import division
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import time

# Run from command line
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = "StreetEasy Apartment Finder")
    parser.add_argument("--outfile", help = "Example: test.csv")
    parser.add_argument("--area")
    parser.add_argument("--min_price", default = "")
    parser.add_argument("--max_price")
    parser.add_argument("--beds", default = "", help = "Examples: =1, <=1, >=1")
    parser.add_argument("--no_fee", default = "")
    args = parser.parse_args()

# Get area numbers by searching StreetEasy for your desired location and looking in the address bar
# Also use search bar to identify if new parameters are needed
price = args.min_price+"-"+args.max_price
area = args.area
if args.beds[0] == '=':
	beds = ':' + args.beds[1]
else:
	beds = args.beds
no_fee = args.no_fee # 1 gets only no fee apartment listings; 0 gets none

def create_search_url(price, area, min_beds, no_fee):
    start = 'http://streeteasy.com/for-rent/nyc/status:open'
    price_param = "%7Cprice:"
    area_param = "%7Carea:"
    beds_param = "%7Cbeds"
    fee_param = "%7Cno_fee:"
    page_param = "?page="
    url = start + price_param + price + area_param + area + beds_param + beds
    if no_fee in ['1', '0']:
    	url = url + fee_param + no_fee + page_param
    else:
    	url = url + page_param
    return url

search_url = create_search_url(price, area, beds, no_fee)
print(search_url)
print("Starting at " + str(datetime.datetime.now()))

def create_page_url(page):
    return  search_url + str(page)

# Get number of listings from first search page
url = create_page_url(1)
r = urlopen(url)
if r.getcode() == "404":
    time.sleep(1)
else:
    r = r.read()
    soup = BeautifulSoup(r,'html.parser')
    num_results = soup.find_all('div',{'class':'result-count first'})[0].text
    # 14 results on a page but the top 2 featured don't count towards total
    num_pages = int(int(num_results.replace(',', ''))/12)

# Create list of links to each listing page
links = []
for page in range(1, num_pages + 1):
    print("Pages percent done: ", round((page/num_pages)*100, 3))
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
    print("Getting date for (", i + 1, " of ", len(links), ") ", link)
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
    print("Getting rent for (", i + 1, " of ", len(links), ") ", link)
    r =urlopen("http://streeteasy.com" + link)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        try:
            r = r.read()
            soup = BeautifulSoup(r,'html.parser')
            div_set = soup.find_all('div',{'class':'price '})[0]
            price = div_set.parent.text.split("\n")[3].strip()
            prices["http://streeteasy.com" + link] = price
        except(IndexError):
            print("No Rent Listed.")

# Go to each page and extract the description of the listing
listingdesc = {}
for i, link in enumerate(links):
    print("Getting description for (", i + 1, " of ", len(links), ") ", link)
    r = urlopen("http://streeteasy.com" + link)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        try:
            r = r.read()
            soup = BeautifulSoup(r, 'html.parser')
            div_set = soup.find_all('meta',{'name':'description'})[0]
            div_set = div_set['content']
            listingdesc["http://streeteasy.com" + link] = div_set
        except(IndexError):
            print("Description error.")

# Go to each page and extract the amenities
amenities = {}
for i, link in enumerate(links):
    print("Getting amenities for (", i + 1, " of ", len(links), ") ", link)
    r = urlopen("http://streeteasy.com" + link)
    if r.getcode() == "404":
        time.sleep(1)
    else:
        try: 
            r = r.read()
            soup = BeautifulSoup(r, 'html.parser')
            div_set = soup.find_all('div',{'class':'third'})
            text_div_set = [x.text.strip().split("\n") for x in div_set]
            # Flatten lists and remove whitespace
            amenlist = [y.strip() for x in text_div_set for y in x if y.strip()]
            # Test if not a googletag
            amenlist2 = [x for x in amenlist if x[0].istitle()]
            # Convert into string 
            amenlist3 = ', '.join(amenlist2)
            amenities["http://streeteasy.com" + link] = amenlist3
        except(IndexError):
            print("Amenities Error")

# Create dataframe from results
df1 = pd.DataFrame.from_dict(avails, orient = "index").reset_index()
df1.columns = ['link', 'date_avail']
df2 = pd.DataFrame.from_dict(prices, orient = "index").reset_index()
df2.columns = ['link', 'rent']
df3 = pd.DataFrame.from_dict(listingdesc, orient = "index").reset_index()
df3.columns = ['link', 'listingdesc']
df4 = pd.DataFrame.from_dict(amenities, orient = "index").reset_index()
df4.columns = ['link', 'amenities']
df = pd.merge(df1, df2, on = 'link')
df = pd.merge(df, df3, on = 'link')
df = pd.merge(df, df4, on = 'link')
df = df.sort_values("date_avail", na_position = "last")

# Write to file with date in column
df['record_added'] = datetime.datetime.now().date().strftime("%Y-%m-%d")
df.to_csv(args.outfile, index = False) 
print("Ending at " + str(datetime.datetime.now()))