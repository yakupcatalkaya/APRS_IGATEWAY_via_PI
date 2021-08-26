# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 19:03:24 2021

@author: yakupcatalkaya
"""

import requests
import json
import time


my_callsign="TA2AQG-5"
my_callsign_2="TA2AQG-1"
#api_key="157188.T2CYJx8s0iAG7d"
#what_is="loc" # "msg","loc","wx" 
#formatt="json" #"json","xml"
my_app_id = " "
API_KEY_SIGNAL = " "
API_KEY_APRS_FI = " "


def get_aprs_loc(old_loce,callsign=my_callsign,api_key=API_KEY_APRS_FI,what_is="loc",formatt="json"):
    while callsign==None :
        callsign=input("Type valid callsign: ").upper()
    while api_key==None:
        api_key=input("Type valid api key: ")
        
    url="https://api.aprs.fi/api/get?name="+callsign+"&what="+what_is+"&apikey="+api_key+"&format="+formatt
    req = requests.get(url)
    info = req.json()
    
    # %Y-%m-%d %H:%M:%S
    while info["found"]==0:
        callsign=input("Type valid callsign: ")
        url="https://api.aprs.fi/api/get?name="+callsign+"&what="+what_is+"&apikey="+api_key+"&format="+formatt
        req = requests.get(url)
        info = req.json()
    comment=info["entries"][0]["comment"]
    lasttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(info["entries"][0]["lasttime"])))
    lat = info["entries"][0]["lat"]
    lng = info["entries"][0]["lng"]
    srccall=info["entries"][0]["srccall"]
    
    string=" Update time: "+ lasttime+ "\n Latittude: "
    string+= lat+ "\n Longtitude: "+lng+ "\n Callsign: "+srccall+ "\n Comment: "+ comment
    
    if old_loce==string:
        return lasttime, lat, lng, srccall, info, comment, string, old_loce
    old_loce=string
    
    pt=time.strptime(lasttime,"%Y-%m-%d %H:%M:%S")
    ptt=time.localtime()
    now=ptt.tm_sec + ptt.tm_min *60 + (ptt.tm_hour)*3600
    send_time = pt.tm_sec + pt.tm_min *60 + pt.tm_hour*3600
    if (ptt.tm_year==pt.tm_year and ptt.tm_mon==pt.tm_mon and ptt.tm_mday==pt.tm_mday) and now-send_time < 900:
        send_notification(message = string, title = "Location")
    
    return lasttime, lat, lng, srccall, info, comment, string, old_loce



def send_notification(message="Test  Message",title="Test Title",alert_type="push"):
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": API_KEY_SIGNAL}
    
    payload = {"app_id": my_app_id,
               "included_segments": ["Subscribed Users"],
               "contents": {"en": message},
               "headings": {"en": title},
               "channel_for_external_user_ids": alert_type}
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    if req.status_code!=200:
        print(req.status_code, req.reason)


def get_message(old_mssge,callsign=my_callsign_2):
    messg_list=[]
    url="http://www.findu.com/cgi-bin/msg.cgi?call="+callsign
    req=requests.get(url).text.split('<TABLE BORDER="3" CELLSPACING="2" CELLPADDING="1">')[1].split('<tr bgcolor="#ccffcc">')[1:]
    for item in req:
        messg=[]
        for itemm in item.split("<td>"):
            if "</td>" in itemm:
                msg=itemm.split("</td>")[0].strip()
                if "href" in msg:
                    msg=msg.split(">")[1].split("<")[0]
                if ":" in msg:
                    msgg=time.strftime("%Y")
                    for item in msg.split()[0].split("/"):
                        msgg += "-" + item
                    msg = msgg + " " + msg.split()[1][:-1]
                messg.append(msg)
        if messg[-2]=="Reply":
            messg_list.append(messg)
            
    if len(messg_list)!=0:
        messg_list=messg_list[0:1]
        if old_mssge==messg_list:
            return messg_list, old_mssge
        old_mssge=messg_list
        for messg in messg_list:
            pt=time.strptime(messg[2],"%Y-%m-%d %H:%M:%S")
            ptt=time.gmtime()
            now=ptt.tm_sec + ptt.tm_min *60 + (ptt.tm_hour)*3600
            send_time = pt.tm_sec + pt.tm_min *60 + pt.tm_hour*3600
            if (ptt.tm_year==pt.tm_year and ptt.tm_mon==pt.tm_mon and ptt.tm_mday==pt.tm_mday) and now-send_time < 900:
                string = " From: " + messg[0] + "\n To: " + messg[1] + "\n Sent time: " + messg[2] + " UTC"
                string += "\n Message: " + messg[-1]
                send_notification(message = string, title = "Message")

    return messg_list, old_mssge

old_mssg=[]
old_loc=[]

while True:
    messages, old_mssg = get_message(old_mssg) # from, to, send_time, type, message 
    lasttime, lat, lng, srccall, info, comment, string, old_loc = get_aprs_loc(old_loc)
    time.sleep(60)



#send_notification(message = string, title = "Information")
