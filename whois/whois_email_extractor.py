import pythonwhois
import re

def get_all_emails_by_whois(domain):
   try:
       details = pythonwhois.get_whois(domain)
       new_emails_found = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", str(details), re.I))
       print ("Total Emails Found By Whois:{}".format(len(new_emails_found))) 
       return new_emails_found  
   except Exception as e:
          print str(e)


def get_data_from_whois(domain):
    dic={'Domain' : None,'Email' : None,'Name' : None,'Company' : None, }
    try:
        details = pythonwhois.get_whois(domain)

        contact=details['contacts']
        admin=contact['admin']
        dic['Domain']=domain
        try:
            email=admin['email']
            dic['Email']=email
        except:
          dic['Email']= None
          print "Email Not Found"
        try:
          name=admin['name']
          dic['Name']=name
        except:
            dic['Name']= None
            print "Name Not Found"
        try:
            org=admin['organization']
            dic['Company']=org
        except:
            print "Organization Not Found"
            dic['Company']= None
    except:
        print "Cant Extract Data From Whois"

    return dic

if __name__ == '__main__':
  print get_data_from_whois("seacotehotel.com")