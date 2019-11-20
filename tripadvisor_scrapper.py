# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from google_search import search
import google

from bs4 import BeautifulSoup
import cookielib
import datetime
from dateutil.relativedelta import relativedelta
import json
import os
import csv
import unicodecsv
import codecs
import logging
from pprint import pprint
from random import choice
from random import randrange
import random
import re
import time
import tldextract
import urllib
import urllib2
import difflib
import requests
import requesocks as requests
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
'''
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
'''
logging.basicConfig(level=logging.INFO)


class IO(object):

    @staticmethod
    def save_text_to_file(text, filename):
        with codecs.open(filename, 'a', 'utf-8') as f:
            f.write(text)


    @staticmethod
    def create_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def create_file(filename):
        with codecs.open(filename, 'w', 'utf-8') as f:
            pass
        return
 
    @staticmethod
    def read_list_of_lists_from_file_usung_csv_v1(filename):
        """

        :param filename:
        :return: [[p11, p12],[p21, p22]]
        """
        datas = []
        with codecs.open(filename, 'r') as f:
            r = csv.reader(f, delimiter=str(','))
            for l in r:
                unicode(l).encode("utf-8")
                datas.append(l)
        return datas     


class BaseScrapper(object):

    def google_search(self, search):
        links = None
        try:
            links = [url for url in google.search(str(search), stop=5) ]
   
        except Exception as e:
            logging.error('in google_search: {}'.format(e))

        return links

    def bing_search(self,query, search_type, key="EwTKq+48VUkZWeqGTe7RC73y/VrVnM70L/duOHpmesg"):
        #search_type: Web, Image, News, Video
        try:

            query = urllib.quote(query)
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
            credentials = (':%s' % key).encode('base64')[:-1]
            auth = 'Basic %s' % credentials
            url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/' + search_type + '?Query=%27' + query + '%27&$top=10&$format=json'
            request = urllib2.Request(url)

            request.add_header('Authorization', auth)
            request.add_header('User-Agent', user_agent)
            request_opener = urllib2.build_opener()
            response = request_opener.open(request)
            response_data = response.read()
            #print "In bing_search, read response :"
            json_result = json.loads(response_data)
            #print "In Bing_search, json response:"
            result_list = json_result['d']['results']
            #print result_list
            return result_list    
        except Exception as e:
            logging.error('in bing_search: {}'.format(e))
            return

        

class TripAdvisorHotelsCrawler(BaseScrapper,object):

    def __init__(self, *a, **kw):
        
        self.incoming_data_file = kw.get('incoming_data_file','')
        
        if self.incoming_data_file:
            self.tempdir = kw.get('tempdir', 'output')
            self.output_data_file =os.path.abspath(os.path.join(self.tempdir, kw.get('output_data_file', '')))
            self.is_first_file_item = True  # to add ',' only before second and next saving entries
            IO.create_dir(self.tempdir)
            IO.create_file(self.output_data_file)

        self.search_domain =  kw.get('search_domain','')
        self.search_hotel_name =  kw.get('search_hotel_name','')
        self.search_hotel_location = kw.get('search_hotel_location','')
        self.base_url = "http://www.tripadvisor.com/Hotel_Review-"
        self.allowed_domains = "tripadvisor.com"
        self.results = None
        self.main()

    def save_item_to_file(self, json_profile, filename):
            """
            :param json_profile: dict, not json string
            """
            if not self.is_first_file_item:
                IO.save_text_to_file(',', self.output_data_file)

            with codecs.open(filename, 'a', 'utf-8') as j:
                j.write(json.dumps(json_profile, indent=4, sort_keys=True))
            logging.info("Data Saved : '{}'".format(json_profile['Input_search_hotel_name']))
            self.is_first_file_item = False     

    
    def get_links_bing_search(self, query_string):
        search_links = []
        try:
            searchstr ="Site : "+self.base_url
            if query_string['Hotel_Name']:
                searchstr = searchstr + " {} {}".format(str(query_string['Hotel_Name']),str(query_string['Hotel_Location']))

            logging.info("Search IN BING: '{}'".format(searchstr))

            #search_links = self.google_search(searchstr)
            bresults = self.bing_search(searchstr, 'Web')
            if bresults:
                for u in bresults:
                    search_link = u['Url']
                    if self.allowed_domains in search_link:
                        #logging.info(search_link)
                        search_links.append(search_link)


        except Exception as e:
            logging.error('in get_links_bing_search: {}'.format(e))

        return search_links

    
    def get_links_google_search(self, query_string):
        search_links = []
        try:
            searchstr ="Site : "+self.base_url
            if query_string['Hotel_Name']:
                searchstr = searchstr + " {} Near: {}".format(str(query_string['Hotel_Name']),str(query_string['Hotel_Location']))

            logging.info("Search In Google: '{}'".format(searchstr))

            search_links = [links for links in self.google_search(searchstr) if self.allowed_domains in links ]

        except Exception as e:
            logging.error('Error in google_search: {}'.format(e))

        return search_links    


    def extract_trip_advisor_details(self,search_dict,urls):
        exrtacted_data = {
            'Input_search_hotel_name' : '',
            'Hotel_Name' : '',
            'No_of_rooms' : '',
            'Hotel_class' : '',
            'Rooms_price_range' : '',
            'Hotel_location' : '',
            'Hotel_address' : '',
            'Hotel_description' : '',
            'Url': None,
            'Sr_No': None,
        }
        try:
            exrtacted_data['Input_search_hotel_name'] = search_dict['Hotel_Name']

            exrtacted_data['Sr_No'] = search_dict['Sr_No']

            if not urls:
                logging.error("No Link Found For : {} returning Null...".format(exrtacted_data['Input_search_hotel_name']))
                return exrtacted_data

            exrtacted_data['Url'] = urls[0]    

            page = urllib2.urlopen(urls[0])
            soup = BeautifulSoup(page,'html.parser')

            try:
                exrtacted_data['Hotel_Name'] = soup.findAll('div', attrs={'class' : 'heading_name_wrapper'})[0].text.strip('\n')
            except:
                pass
            
            try:
                exrtacted_data['Hotel_description'] = soup.findAll('span', attrs={'class' : 'tabs_descriptive_text'})[0].string.strip('\n')
            except:
                pass

            try:    
                exrtacted_data['No_of_rooms'] = soup.findAll('span', attrs={'class' : 'tabs_num_rooms'})[0].string.strip('\n').strip()
            except:
                pass

            try:    
                exrtacted_data['Hotel_class'] = soup.find('div', {'class' :'additional_info stars'}).text.strip('\n').encode('utf-8')
            except:
                pass

            try:    
                exrtacted_data['Rooms_price_range'] = soup.findAll('span', attrs={'property' : 'priceRange'})[0].string.split(' (')[0].strip('\n')
            except:
                pass

            try:    
                exrtacted_data['Hotel_location'] = soup.findAll('div', attrs={'class' : 'region_list wrap'})[0].text.replace('Location:','').replace('>',',').replace('\n','')
            except:
                pass

            try:    
                exrtacted_data['Hotel_address'] = soup.findAll('address', attrs={'class' : 'additional_info adr'})[0].text.replace('Address: ','').strip('\n')
            except:
                pass

            try:    
                exrtacted_data['streetAddress'] = soup.findAll('span', attrs={'property' : 'streetAddress'})[0].text
                #print 'streetAddress is'
                #print  exrtacted_data['streetAddress']
            except Exception as e:
                pass

            try:    
                exrtacted_data['postalCode'] = soup.findAll('span', attrs={'property' : 'postalCode'})[0].text
                #print 'postalCode is'
                #print  exrtacted_data['postalCode']
            except Exception as e:
                pass    

            try:    
                exrtacted_data['addressLocality'] = soup.findAll('span', attrs={'property' : 'addressLocality'})[0].text
                #print 'addressLocality is'
                #print  exrtacted_data['addressLocality']
            except Exception as e:
                pass    

            try:    
                #exrtacted_data['addressCountry'] = soup.findAll('span', attrs={'property' : 'addressCountry'})[0].text
                country  = soup.find("input", {"id": "GEO_SCOPED_SEARCH_INPUT"}).get('value')
                #Altafulla, Spain
                country = country.split(', ')[1]
                exrtacted_data['addressCountry'] = country
                #print 'addressCountry is'
                #print  exrtacted_data['addressCountry']
            except Exception as e:
                pass

               

            if exrtacted_data['Hotel_Name'] :
                logging.info("Extracted Data for Hotel : '{}'".format(exrtacted_data['Hotel_Name']))
            else:
                logging.info("OPPS Data Cant be Extracted for Hotel : '{}'".format(self.search_hotel_name))
                

        except Exception as e:
            logging.error("in extract_trip_advisor_details: {}".format(str(e)))

        return exrtacted_data    


    def main(self):
        if self.incoming_data_file:
            queries = IO.read_list_of_lists_from_file_usung_csv_v1(self.incoming_data_file)
            IO.save_text_to_file('[', self.output_data_file)
        elif self.search_domain:
            print self.search_domain
            print "Opps!!! Stopped ... Not implemented for domain search yet"
            return
        elif self.search_hotel_name:
            #print self.search_hotel_name
            search_query = [ 1, self.search_hotel_name , '']
            if self.search_hotel_location:
                search_query[2] = self.search_hotel_location
            queries = []
            queries.append(search_query)

        else:
            logging.error('Something went Wrong, Cant Proceed Further.Stop')
            return     
        
        for query_list in queries:
            try:
                try:
                    sr_no = query_list[0]
                except:
                    sr_no = None    
                
                try:
                    hotel_name = query_list[1]
                except:
                    hotel_name = None

                try:
                    hotel_location = query_list[2]
                except:
                    hotel_location = None
    
                if not hotel_name:
                    continue

                #self.input_search_hotel_name =  query_list[0]   
                query_dict = {'Hotel_Name': hotel_name, 'Hotel_Location': hotel_location, 'Sr_No': sr_no}

                logging.info('To Find : {}'.format(query_dict))
                
                domain = 'http://www.tripadvisor.com/Hotel_Review-'
                params = {'lang': 'en', 'tld': 'com'}
                params['pause'] =  2.0
                params['stop']= 1
                params['only_standard']= True
                params['start']=  0
                params['num']= 1

                query = 'Site : {} {} {}'.format(str(self.base_url),hotel_name,hotel_location)
                #print query
                
                #do bing search for hotel 
                links_to_hotels = self.get_links_bing_search(query_dict)
                
                if not links_to_hotels:
                    # if return No Url Then go For google Search
                    links_to_hotels = self.get_links_google_search(query_dict)

                if not links_to_hotels:
                    #last try, if return No Url Then go For google Search With Proxy
                    logging.info("IN Google SEARCH With Proxy")
                    links_to_hotels =  [url for url in search(query, **params)]

                logging.info('Parse Link To Soup : {} '.format(links_to_hotels)) 
                
                hotel_data =self.extract_trip_advisor_details(query_dict,links_to_hotels)
                self.results = hotel_data
                
                if self.incoming_data_file:
                    self.save_item_to_file(hotel_data,self.output_data_file)


            except Exception as e:
                    logging.error('IN MAIN :: {} '.format(str(e)))
                    continue           
            time.sleep(3)
            
        if self.incoming_data_file:
            IO.save_text_to_file(']', self.output_data_file)     # close json list                
       

if __name__ == '__main__':
    '''
    hotels =  TripAdvisorHotelsCrawler(
        output_data_file='hotels_spain_json2.txt' ,
        incoming_data_file= 'hotels_to_find.csv'
        )
    '''
    loc = ['United Kingdom','TQ2 6NT']
    for loc in loc:
        hotels =  TripAdvisorHotelsCrawler(
            search_hotel_name = 'The Grand Hotel',
            search_hotel_location = loc
            )

        print hotels.results
        ratio = fuzz.ratio(hotels.results['Hotel_Name'],hotels.results['Input_search_hotel_name'])
        print ratio




     