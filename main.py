from netmiko import ConnectHandler
import requests
import argparse
import requests
from bs4 import BeautifulSoup
import re
import numpy as np




def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--username',type=str,required=True, help='please input your tacacs username')
    parser.add_argument('-p','--password',type=str,required=True, help='please input your tacacs password')
    args = parser.parse_args()
    return args.username,args.password

def get_webex_ip():
    
    URL = "https://help.webex.com/en-US/article/WBX000028782/Network-Requirements-for-Webex-Services#id_135011"

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id='id_135011')
    job_elements = results.find_all("div", class_="body refbody")
    tds=[]
    for job_element in job_elements:
        rows = job_element.find_all('tr')
        for row in rows:
            tds.append(str(row.find_all('td')))
        
    results=[]
    for i in range(1, len(tds)):
        # print(type(tds[i]))
        regexed=re.findall(r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?',tds[i])
        results.append(regexed)
        
    asd = np.concatenate( results, axis=None )
    return asd

def get_zoom_ip():
    response = requests.get("https://assets.zoom.us/docs/ipranges/ZoomMeetings.txt")
    response.encoding = 'utf-8'
    asd=response.text
    a=asd.split()
    # print(a)
    return a


def get_zoom_pan(user,pwd):
    panci={
        "device_type": "paloalto_panos",
        "host":"192.168.135.128",
        "username":user,
        "password":pwd,
        "fast_cli":False,
    }

    net_connect = ConnectHandler(**panci)
    # test = net_connect.send_command_timing('show system info')

    # uncomment 2 line dibawah ini
    test = net_connect.send_command_timing('set system setting target-vsys vsys4')
    output = net_connect.send_command_timing('show running nat-policy-addresses',strip_prompt=False,strip_command=False)
    net_connect.disconnect()
    #write pan subnet list
    with open('pan.txt','w') as f:
        f.write(output)

    # test = open("pan.txt")
    flag = 0  
    index = 0
    zoom = 'Zoom-Primary'
    webex = 'Webex-Primary'
    # test.close()

    #check if rule present on pan
    test = open("pan.txt")
    for line in test:
        index +=1
        if zoom in line:
            flag = 1
            break

    if flag == 0:
        print ('not found')
    else:
        pass
    test.close()

    test = open("pan.txt")
    content = test.readlines()
    b= content[index+1]
    test.close()
    b=b.split('[',1)[1]
    b="["+b
    x="[];"
    for spec in x:
        b = b.replace(spec,"")
    b=b.split(' ')
    del b[0]
    return b

def get_webex_pan(user,pwd):
    panci={
        "device_type": "paloalto_panos",
        "host":"192.168.135.128",
        "username":user,
        "password":pwd,
        "fast_cli":False,
    }

    net_connect = ConnectHandler(**panci)
    # test = net_connect.send_command_timing('show system info')

    # uncomment 2 line dibawah ini
    test = net_connect.send_command_timing('set system setting target-vsys vsys4')
    output = net_connect.send_command_timing('show running nat-policy-addresses',strip_prompt=False,strip_command=False)
    net_connect.disconnect()


    # test = open("pan.txt")
    flag = 0  
    index = 0
    webex = 'Webex-Primary'
    # test.close()

    #check if rule present on pan
    test = open("pan.txt")
    for line in test:
        index +=1
        if webex in line:
            flag = 1
            break

    if flag == 0:
        print ('not found')
    else:
        pass
    test.close()

    test = open("pan.txt")
    content = test.readlines()
    b= content[index+1]
    test.close()
    b=b.split('[',1)[1]
    b="["+b
    x="[];"
    for spec in x:
        b = b.replace(spec,"")
    b=b.split(' ')
    del b[0]
    return b

if __name__ == '__main__':
    c = get_args()
    b = get_zoom_pan(*c)
    e = get_webex_pan(*c)
    a = get_zoom_ip()
    d = get_webex_ip()
    print("webex pan",e)
    nk=set(a).intersection(b)
    wp=set(d).intersection(e)

    for x in a:
        test = 0
        if x in nk:
            pass
        else:
            test = 1
            print (x,'absent in zoom website')
    if test == 0:
        print('all zoom subnet list all already present on PAN')
    for x in d:
        test = 0
        if x in wp:
            pass
        else:
            test = 1
            print (x,'absent in webex website')
    if test == 0:
        print('all webex subnet list all already present on PAN')

    abc = input('press enter to exit. . . ')


