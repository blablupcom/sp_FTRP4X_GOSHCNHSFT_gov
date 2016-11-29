# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.0

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = urllib2.urlopen(url)
        count = 1
        while r.getcode() == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = urllib2.urlopen(url)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        elif not sourceFilename:
            ext = os.path.splitext(url)[1]
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in r.headers.get('content-type'):
            ext = '.xlsx'
        elif 'application/vnd.ms-excel' in r.headers.get('content-type'):
            ext = '.xls'
        validURL = r.getcode() == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx', '.pdf']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string

#### VARIABLES 1.0

entity_id = "FTRP4X_GOSHCNHSFT_gov"
url = "http://www.gosh.nhs.uk/about-us/our-corporate-information/how-we-spend/expenditure-over-25000"
errors = 0
data = []


#### READ HTML 1.0

html = urllib2.urlopen(url)
soup = BeautifulSoup(html, 'lxml')

#### SCRAPE DATA

links = soup.find('div', 'node__content').find_all('a')
for link in links:
    if 'http' not in link['href']:
        url = 'http://www.gosh.nhs.uk'+link['href']
    else:
        url = link['href']
    try:
        title = link.text.strip()
    except:
        pass
    if not title:
        continue
    csvMth = csvYr = ''
    if 'month 1' in title:
        csvMth = '01'
    elif 'month 2' in title:
        csvMth = '02'
    elif 'month 3' in title:
        csvMth = '03'
    elif 'month 4' in title:
        csvMth = '04'
    elif 'month 5' in title:
        csvMth = '05'
    elif 'month 6' in title:
        csvMth = '06'
    elif 'month 7' in title:
        csvMth = '07'
    elif 'month 8' in title:
        csvMth = '08'
    elif 'month 9' in title:
        csvMth = '09'
    if re.findall('\\bmonth 10\\b', title):
        csvMth = '10'
    elif re.findall('\\bmonth 11\\b', title):
        csvMth = '11'
    elif re.findall('\\bmonth 12\\b', title):
        csvMth = '12'
    elif '-' in title:
        csvMth = 'Q0'
    if '@' in title:
        break
    csvYr = title.split(',')[-1].strip()

    csvMth = convert_mth_strings(csvMth.upper())
    data.append([csvYr, csvMth, url])



#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF

