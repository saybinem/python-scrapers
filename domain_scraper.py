import csv
import sys
import math
import unicodecsv
import requests
from bs4 import BeautifulSoup

def get_domainlist(filename):
    try:
        f = open(filename, 'rt')
    except IOError:
        print "File {} not Found...exiting".format(filename)
        sys.exit()

    domains = []
    try:
        reader = csv.reader(f)
        for row in reader:
            try:
                if row[5] not in domains:
                    domains.append(row[5])
            except IndexError:
                continue
    finally:
        f.close()
        #The first element of the domain list, is the row title, we don't need that
        domains.pop(0)
    return domains

def get_similarwebpage(domain):
    url = "https://www.similarweb.com/website/{}".format(domain)
    response = requests.get(url)
    if response.status_code == 404:
        print "::Page returned 404 Not Found, Skipping"
        return None
    else:
        return response.text

def get_scrapeddata(page):
    bsobj = BeautifulSoup(page, "html.parser")
    try:
        totalview = bsobj.find('div', class_='websitePage-contentNarrow websitePage-contentRight\
                websitePage-engagement websitePage-mobileFramed').\
                find_all('div', class_='engagementInfo-content')
    except AttributeError as e:
        print "::None Type received trying scraping, skipping...\nException:{}".format(e)
        return None
    
    """
    Retrieved total view needs to be splitted, because the data is e.g PageView\n28.5M
    afterwards the unit and the actual number has to be seperated as well for further processing
    """
    totalvisits = totalview[0].text.strip().split('\n')[1]
    if totalvisits.isdigit():
        totalvisits = float(totalview[0].text.strip().split('\n')[1])
    else:
        totalvisits = float(totalview[0].text.strip().split('\n')[1][:-1])

    unit_totalvisits = totalview[0].text.strip().split('\n')[1][-1:]
    pageviews = float(totalview[2].text.strip().split('\n')[1])
    return [totalvisits, unit_totalvisits, pageviews]

def get_totalpageviews(scraped_data):
    totalvisits = scraped_data[0]
    unit_totalvisits = scraped_data[1]
    pageviews = scraped_data[2]
    if pageviews < 1:
        totalpageviewshumanreadable = 0
        totalpageviews = 0
        return ["{0}{1}".format(totalvisits, unit_totalvisits), pageviews, totalpageviews,\
            totalpageviewshumanreadable]
    if not unit_totalvisits.isalpha():
        totalpageviews = totalvisits * pageviews
    elif unit_totalvisits == 'B':
        totalpageviews = (totalvisits*10**9)*pageviews
    elif unit_totalvisits == 'M':
        totalpageviews = (totalvisits*10**6)*pageviews
    elif unit_totalvisits == 'K':
        totalpageviews = (totalvisits*10**3)*pageviews
    else:
        return None

    """
    Here we determine what kind of number we have, to specifiy the correct unit for the
    total page views. 2 for million, 3 for billion. The Billions get devided by 1M so we get 1000M
    instead of 1B. If 2 or 3 does not match we have Thousand.
    """
    exponent = int(math.log(totalpageviews, 1000))
    if exponent == 2:
        totalpageviewshumanreadable = "{}{}".format(int(totalpageviews/1000000), 'M')
    elif exponent == 3:
        totalpageviewshumanreadable = "{}{}".format(int(totalpageviews/1000000), 'M')
    else:
        totalpageviewshumanreadable = totalpageviews
    return ["{0}{1}".format(totalvisits, unit_totalvisits), pageviews, totalpageviews,\
            totalpageviewshumanreadable]

def write_csv(results, csv_filename):
    with open(csv_filename, 'a') as f:
        writer = unicodecsv.writer(f, encoding = 'utf-8')
        writer.writerow(results)

def create_csv(csv_filename):
    with open(csv_filename, 'wb') as f:
        writer = unicodecsv.writer(f, encoding = 'utf-8')
        writer.writerow(['Domain', 'Total Visits', 'Page Views', 'Total Page Views',\
                'Total Page Views(M)'])

def main():
    try:
        domainlist = get_domainlist(sys.argv[1])
    except IndexError:
        print "The filename of csv containing the Domains, has to be passed as a argument!"
        sys.exit()

    results = []
    resultscsvfile = 'results_domains_pageview.csv'
    create_csv(resultscsvfile)
    for domain in domainlist:
        print "Scraping {}".format(domain)
        page = get_similarwebpage(domain)
        if page is not None:
            scraped_data = get_scrapeddata(page)
            if scraped_data is not None:
                totalpageviews = get_totalpageviews(scraped_data)
                write_csv([domain, totalpageviews[0], totalpageviews[1], totalpageviews[2],\
                        totalpageviews[3]],resultscsvfile)

if __name__ == '__main__':
    main()
