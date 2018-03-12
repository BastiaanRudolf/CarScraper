# Webscraping data

# import libraries
import urllib3
from bs4 import BeautifulSoup
import time
import certifi
import csv
import numpy as np

# Start time
start_time = time.time()

#Create storage lists
prices = []
kms = []
year = []
# Initiating a for loop to fill the sorage lists with raw data per page
for i in range(1,21):
    # specify the url
    url_base = "https://www.autoscout24.nl/resultaten?mmvmk0=13&mmvmd0=18481&mmvco=1&cy=NL&fuel=D&powertype=kw&atype=C&ustate=N%2CU&sort=standard&desc=0&page="
    url = url_base + str(i) + '&size=20'
    print('extracting information from page '+ str(i))
    # query the website and return parsed data into variable 'soup'
    http = urllib3.PoolManager(10, ca_certs=certifi.where())
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html.parser")

    # LISTING PRICES----------------------------------------------------------------
    # Find all price locations and store them in price_loc
    price_loc = soup.findAll("span", {"class": "cldt-price sc-font-xl sc-font-bold", "data-item-name": "price"})

    # Loop through each element in price_loc
    for each in price_loc :
        # Strip each price from location and store them in the list prices
        prices.append(each.text.strip()) # strip() is used to remove starting and trailing

    # LISTING KMs and year----------------------------------------------------------
    # Create temporary storage list
    li_kms_year = []
    # Find list locations containing kms and year and store in li_loc
    li_loc = soup.findAll("ul", {"data-item-name": "vehicle-details"}) # NOTE: selects whole li!

    # Loop through each element in li_loc
    for each in li_loc :
        # Appends every li to combined li_kms_year list
        li_kms_year.append(each.text.strip())

    # Extracting kms and year from the li_kms_year list
    i = 0
    while i < len(li_kms_year) : # NOTE: EOF technique
    # split list in var for car i and extract kms and year, appending to the lists
        var = li_kms_year[i].split("\n\n\n")
        kms.append(var[0])
        year.append(var[1])
        i += 1
    # Wait 1 second before opening new page
    time.sleep(1)

#Cleaning prices
prices_clean1 = ''.join(''.join(prices).split('€ ')).split(',-')
prices_clean2= []
for each in prices_clean1 :
    if len(each) < 9 :
        prices_clean2.append(each)
    else :
        prices_clean2.append(each[17:])
del(prices_clean2[-1])
prices_clean3=[]
for each in prices_clean2 :
    prices_clean3.append(each.replace('.',''))
# Converting string into int
clean_prices = list(map(int,prices_clean3))

#Cleaning kms
clean_kms1 = []
for each in kms :
    clean_kms1.append(each[:-3])
clean_kms2 = []
for each in clean_kms1 :
    clean_kms2.append(each.replace('.',''))
# Converting string into int
clean_kms = list(map(int,clean_kms2))

# Cleaning year
clean_year1 = []
for each in year :
    clean_year1.append(each[3:])

# Finding incomplete datapoints
# Indexlist incomplete datapoints
indexes_missing_data = []
for index, year in enumerate(clean_year1) :
    if year == ' (Bouwjaar)':
        indexes_missing_data.append(str(index))
# Converting string into int
clean_missing = list(map(int,indexes_missing_data))

# Using the indexes to delete corresponding data points in the lists
for i in clean_missing :
    i = i - clean_missing.index(i)
    del(clean_year1[i])
    del(clean_kms[i])
    del(clean_prices[i])
# Converting string year into int
clean_year = list(map(int,clean_year1))

# Combining the clean data, converting to np and transposing the columns
combined_list = np.transpose(np.array([clean_year, clean_kms, clean_prices]))

# Printing update about the number of cars found
print('extracted information of ' + str(len(clean_year)) + ' cars, in ' + '%s seconds' % round((time.time() - start_time), 0))

# Exporting data to .csv file
with open('/Users/bastiaanwitte/desktop/datascience/bmw.csv', "w") as output:
    writer = csv.writer(output)
    writer.writerows(combined_list)

# End of script
