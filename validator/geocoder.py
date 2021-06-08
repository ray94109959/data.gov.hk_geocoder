import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import datetime

def parse(x):
    finallist = []
    print('1008a')
    if x != 'error1':
        print(datetime.datetime.now(),'1008bi')
        try:
            pagetext = requests.get(x)
            print('1008bii')
            page = pagetext.text
            print('1008c')
            soup = bs(page, 'lxml')
            print('1008d')
            data = soup.find_all('engpremisesaddress', limit=11)
            data1 = soup.find_all('chipremisesaddress', limit=11)
            data2 = soup.find_all('geoaddress', limit=11)
            data3 = soup.find_all('latitude', limit=11)
            data4 = soup.find_all('longitude', limit=11)
            data5 = soup.find_all('validationinformation', limit=11)
            print('1008e')
            if data == []:
                finallist.append(["Error", "2"])
            else:
                for i in range(len(data)):
                    rank = data[i].get_text(', ')
                    rank1 = data1[i].get_text(',')
                    rank2 = data2[i].get_text(',')
                    rank3 = data3[i].get_text(',')
                    rank4 = data4[i].get_text(',')
                    rank5 = data5[i].get_text(',')
                    resultlist = [rank, rank1, rank2, rank3, rank4, rank5]
                    finallist.append(resultlist)
            print('1008f')
        except Exception as e:
            print(e)
        
            
    else:
        print('1008bi')
        finallist.append(["Error", "1"])
    #   print('x')
    return(finallist)


def findaddress(addressdata, logfilepathname):       
    # if __name__ == '__main__':
        print(datetime.datetime.now(),'1007')
        executor = ThreadPoolExecutor(max_workers=5)
        global latlist
        global lnglist
        global finallist
        latlist = []
        lnglist =[]
        errorlist = []
        threesamescorelist = []
        finallist = []
        urllist = []
        print(addressdata)
        print(len(addressdata))

        for r in range(len(addressdata)):
        # for r in range(2):
            try:
                address = addressdata[r]
                url = "https://www.als.ogcio.gov.hk/lookup?q=" + address
                url = url.replace(' ', '%20')
                urllist.append(url)
            except:
                urllist.append('error1')
        # print(urllist)
        print('1008')
        result = executor.map(parse, urllist)
        finals = []

        for value in result:
            finals.append(value)
        # print(finals)
        print('1009')
        
        for l in range(len(finals)):
                if len(finals[l]) > 1:
                    if finals[l][0][-1] != finals[l][1][-1]:
                        # print('3: Highest Score Address Found')
                        print('1010')
                        latlist.append(finals[l][0][-3])
                        lnglist.append(finals[l][0][-2])

                        dataframelist = { 
                            "ID" : l+1,
                            'Address Name' : addressdata[l],
                            'Score': [finals[l][0][-1]],
                            'Remark': ["Highest Score Address Found"],
                            'Latitude' : [finals[l][0][-3]],
                            'Longitude' : [finals[l][0][-2]],
                            'Geoaddress' : [finals[l][0][-4]],
                            'English Address Returned by ALS' : [finals[l][0][0]],
                            'Chinese Address Returned by ALS' : [finals[l][0][1]]
                            }
                        dp = pd.DataFrame(dataframelist)

                        with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as ffile:
                            dp.to_csv(ffile, header=False, index=False)

                    else:
                        if finals[l][0][-1] == finals[l][1][-1]:
                            if finals[l][-1][-1] == finals[l][1][-1]:
                                # print('limited to 10')
                                # print('6: 10+ Same Score Returned')
                                print('1010')
                                latlist.append(finals[l][0][-3])
                                lnglist.append(finals[l][0][-2])
                                engaddressappend = []
                                chiaddressappend = []
                                scoreappend = []
                                idlist = []
                                samescore = []
                                addressnameappend = []
                                latappend = []
                                lngappend = []
                                geoappend = []
                                for x in range(len(finals[l])):
                                    samescore.append('10+ Same Score Returned, check ALS for more results')
                                    engaddressappend1 = []
                                    chiaddressappend1 = []
                                    engaddressappend1.append(finals[l][x][0])
                                    chiaddressappend1.append(finals[l][x][1])
                                    scoreappend.append(finals[l][x][-1])
                                    idlist.append(l+1)
                                    addressnameappend.append(addressdata[l])
                                    engaddressappend1 = ', '.join(engaddressappend1)
                                    chiaddressappend1 = ', '.join(chiaddressappend1)
                                    latappend.append(finals[l][x][-3])
                                    lngappend.append(finals[l][x][-2])
                                    geoappend.append(finals[l][x][-4])
                                    engaddressappend.append(engaddressappend1)
                                    chiaddressappend.append(chiaddressappend1) 
                            

                                dataframelist = {
                                    "ID" :   idlist,
                                    'Address Name' : addressnameappend,
                                    'Score': scoreappend,
                                    'Remark': samescore,
                                    'Latitude' : latappend,
                                    'Longitude' : lngappend,
                                    'Geoaddress' : geoappend,
                                    'English Address Returned by ALS' : engaddressappend,
                                    'Chinese Address Returned by ALS' : chiaddressappend
                                    }
                                dv = pd.DataFrame(dataframelist)
                                

                                with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as f:
                                    dv.to_csv(f, header=False, index=False)
                            else:
                                # print('4: Same Score')
                                print('1010')
                                latlist.append(finals[l][0][-3])
                                lnglist.append(finals[l][0][-2])
                                engaddressappend = []
                                chiaddressappend = []
                                scoreappend = []
                                idlist = []
                                samescore = []
                                addressnameappend = []
                                latappend = []
                                lngappend = []
                                geoappend = []
                                for x in range(len(finals[l])):
                                    if x != 0:
                                        if finals[l][x][-1] == finals[l][x-1][-1]:
                                            samescore.append('Same Score')
                                            engaddressappend1 = []
                                            chiaddressappend1 = []
                                            prange = len(finals[l][x])
                                            engaddressappend1.append(finals[l][x][0])
                                            chiaddressappend1.append(finals[l][x][1])
                                            scoreappend.append(finals[l][x][-1])
                                            idlist.append(l+1)
                                            addressnameappend.append(addressdata[l])
                                            engaddressappend1 = ', '.join(engaddressappend1)
                                            chiaddressappend1 = ', '.join(chiaddressappend1)
                                            latappend.append(finals[l][x][-3])
                                            lngappend.append(finals[l][x][-2])
                                            geoappend.append(finals[l][x][-4])
                                            engaddressappend.append(engaddressappend1)
                                            chiaddressappend.append(chiaddressappend1) 
                                    else:
                                        samescore.append('Same Score')
                                        engaddressappend1 = []
                                        chiaddressappend1 = []
                                        prange = len(finals[l][x])
                                        engaddressappend1.append(finals[l][x][0])
                                        chiaddressappend1.append(finals[l][x][1])
                                        scoreappend.append(finals[l][x][-1])
                                        idlist.append(l+1)
                                        addressnameappend.append(addressdata[l])
                                        engaddressappend1 = ', '.join(engaddressappend1)
                                        chiaddressappend1 = ', '.join(chiaddressappend1)
                                        latappend.append(finals[l][x][-3])
                                        lngappend.append(finals[l][x][-2])
                                        geoappend.append(finals[l][x][-4])
                                        engaddressappend.append(engaddressappend1)
                                        chiaddressappend.append(chiaddressappend1) 
                            
                                dataframelist = {
                                    "ID" :   idlist,
                                    'Address Name' : addressnameappend,
                                    'Score': scoreappend,
                                    'Remark': samescore,
                                    'Latitude' : latappend,
                                    'Longitude' : lngappend,
                                    'Geoaddress' : geoappend,
                                    'English Address Returned by ALS' : engaddressappend,
                                    'Chinese Address Returned by ALS' : chiaddressappend
                                    }
                                dv = pd.DataFrame(dataframelist)
                                
                                with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as f:
                                    dv.to_csv(f, header=False, index=False)


                else:
                    if finals[l][0][0] == "Error" and finals[l][0][1] == "1":
                        # print('1: Error - Address field cannot be empty')
                        print('1010')
                        latlist.append("Error")
                        lnglist.append("Error")

                        dataframelist = { 
                            "ID" : l+1,
                            'Address Name' : addressdata[l],
                            'Score': ["None"],
                            'Remark': ["Address field cannot be empty"], 
                            'Latitude' : ["None"],
                            'Longitude' : ["None"],
                            'Geoaddress' : ["None"],
                            'English Address Returned by ALS' : ["None"],
                            'Chinese Address Returned by ALS' : ["None"] 
                            }
                        dp = pd.DataFrame(dataframelist)

                        with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as ffile:
                            dp.to_csv(ffile, header=False, index=False)

                    elif finals[l][0][0] == "Error" and finals[l][0][1] == "2":
                        # print('2: Error - Address not found in ADI Tool')
                        print('1010')
                        latlist.append("Error")
                        lnglist.append("Error")

                        dataframelist = {
                            "ID" : l+1,
                            'Address Name' : addressdata[l],
                            'Score': ["None"],
                            'Remark': ["Address not found in ADI Tool"],
                            'Latitude' : ["None"],
                            'Longitude' : ["None"],
                            'Geoaddress' : ["None"],
                            'English Address Returned by ALS' : ["None"],
                            'Chinese Address Returned by ALS' : ["None"]
                            }
                        dp = pd.DataFrame(dataframelist)

                        with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as ffile:
                            dp.to_csv(ffile, header=False, index=False)
                    else:
                        # print('5: Highest Score Address Found')
                        print('1010')
                        # print(finals[l])
                        latlist.append(finals[l][0][-3])
                        lnglist.append(finals[l][0][-2])

                        engaddressappend = []
                        chiaddressappend = []
                        addressnameappend = []
                        engaddressappend1 = []
                        chiaddressappend1 = []
                        prange = len(finals[l][0])
                        engaddressappend1.append(finals[l][0][0])
                        chiaddressappend1.append(finals[l][0][1])
                        engaddressappend1 = ', '.join(engaddressappend1)
                        chiaddressappend1 = ', '.join(chiaddressappend1)
                        engaddressappend.append(engaddressappend1)
                        chiaddressappend.append(chiaddressappend1)
                                    
                        dataframelist = { 
                            "ID" : l+1,
                            'Address Name' : addressdata[l],
                            'Score': [finals[l][0][-1]],
                            'Remark': ["Highest Score Address Found"],
                            'Latitude' : [finals[l][0][-3]],
                            'Longitude' : [finals[l][0][-2]],
                            'Geoaddress' : [finals[l][0][-4]],
                            'English Address Returned by ALS' : engaddressappend,
                            'Chinese Address Returned by ALS' : chiaddressappend
                            }
                        dp = pd.DataFrame(dataframelist)
                        with open(logfilepathname, 'a', encoding='utf-8-sig', newline='') as f:
                            dp.to_csv(f, header=False, index=False)
        print(latlist, lnglist)
