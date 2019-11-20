import pythonwhois
def get_address_detail(domain):
    try:
        dic={'whoisCoName' : None,'whoisPhone' : None,'whoisFax' : None,'whoisAddrStreet' : None ,'whoisFax' : None,'whoisAddrCity' : None,'whoisAddrState' : None,'whoisAddrCountry' : None,'whoisAddrZip':None}
        all_detail = pythonwhois.get_whois(domain)
        contact_detail=all_detail['contacts']
        address_detail=contact_detail['admin']
        try:
           whoisCoName = address_detail['name']
           dic['whoisCoName']=whoisCoName
           print whoisCoName
        except:
          dic['whoisCoName']= None
        try:
           whoisPhone = address_detail['phone']
           dic['whoisPhone']=whoisPhone
        except:
          dic['whoisPhone']= None
        try:
           whoisFax = address_detail['fax']
           dic['whoisFax']=whoisFax
        except:
          dic['whoisFax']= None
        try:
           whoisAddrStreet = address_detail['street']
           dic['whoisAddrStreet']=whoisAddrStreet
        except:
          dic['whoisAddrStreet']= None
        try:
           whoisAddrCity = address_detail['city']
           dic['whoisAddrCity']=whoisAddrCity
        except:
          dic['whoisAddrCity']= None
        try:
           whoisAddrState = address_detail['state']
           dic['whoisAddrState']=whoisAddrState
        except:
          dic['whoisAddrState']= None
        try:
           whoisAddrCountry = address_detail['country']
           dic['country']=whoisAddrCountry
        except:
          dic['whoisAddrCountry']= None
        try:
           whoisAddrZip = address_detail['postalcode']
           dic['whoisAddrZip']=whoisAddrZip
        except:
          dic['whoisAddrZip']= None
        return dic

    except:
        print "Not found"
        return dic
if __name__ == '__main__':
    print get_address_detail("facebook.com")



