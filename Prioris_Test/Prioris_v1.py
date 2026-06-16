import mysql.connector
from datetime import datetime
import socket
import time
import requests
import threading, webbrowser, time, requests
from flask import Flask, request, jsonify, render_template_string

API_KEY = "AIzaSyAajd58n7_B6YY94QWEBGsjB4RbASIFdE8"


connection = mysql.connector.connect(
    host="localhost",       
    user="root",            
    password="new_password",
    database="prioris"  
)


if connection.is_connected():
    print("Connected to MySQL!")

cursor = connection.cursor()


def addTask():
    TaskName=input("Enter Task Name:")
    
    
    print("Enter Task Category:\nUrgent and Important: 1\nUrgent but Not Important: 2\nNot Urgent but Important: 3\nNot Urgent and Not Important: 4\n")
    Category=int(input("Enter:"))

    print("Choose Tag for the Task\nAvailable Tags Are-")
    cursor.execute("SELECT tagName,tagID FROM Tags")
    rows = cursor.fetchall()
    for i in rows:
        print(i[0],": ",i[1])
    TagID=int(input())
    sql = "SELECT tagName FROM Tags WHERE tagID = %s"
    cursor.execute(sql, (TagID,))
    result=cursor.fetchone()
    Tag=result[0]

    dl_input=input("Enter deadline (YYYY-MM-DD HH:MM:SS): ")
    deadline=datetime.strptime(dl_input, "%Y-%m-%d %H:%M:%S")
    
    
    taskStatus=0


    sql = "INSERT INTO TaskInfo (taskName,Category,Tag,taskStatus,deadline) VALUES (%s,%s,%s,%s,%s)"
    values = (TaskName,Category,Tag,taskStatus,deadline)
    cursor.execute(sql, values)
    connection.commit()
    print("Task Added Successfully")



def displayTask():

    cursor.execute("SELECT tagName FROM tags ")
    result=cursor.fetchall()
    tag_list=[]
    for i in result:
        tag_list.append(i[0])


    print("Enter Filter (All, Today,",end=' ')
    for i in tag_list:
        print(i,end=", ")
    print("Completed)- ",end='')
    fil=input()

    if fil in ["All","all","ALL"]:
        print("1. Urgent and Important-")
        cursor.execute("SELECT taskName from taskinfo where category=1 and taskStatus=0")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("2. Urgent but Not Important-")
        cursor.execute("SELECT taskName from taskinfo where category=2 and taskStatus=0")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("3. Not Urgent but Important-")
        cursor.execute("SELECT taskName from taskinfo where category=3 and taskStatus=0")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("4. Not Urgent and Not Important-")
        cursor.execute("SELECT taskName from taskinfo where category=4 and taskStatus=0")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

    elif fil in ["today","Today","TODAY"]:
        today = date.today()
        print("1. Urgent and Important-")
        sql="SELECT taskName from taskinfo where category=1 and taskStatus=0 and DATE(deadline) = %s "
        cursor.execute(sql,(today,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("2. Urgent but Not Important-")
        sql="SELECT taskName from taskinfo where category=2 and taskStatus=0 and DATE(deadline) = %s "
        cursor.execute(sql,(today,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("3. Not Urgent but Important-")
        sql="SELECT taskName from taskinfo where category=3 and taskStatus=0 and DATE(deadline) = %s "
        cursor.execute(sql,(today,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("4. Not Urgent and Not Important-")
        sql="SELECT taskName from taskinfo where category=4 and taskStatus=0 and DATE(deadline) = %s "
        cursor.execute(sql,(today,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])


    elif fil in ["Completed","completed","COMPLETED"]:
        print("1. Urgent and Important-")
        cursor.execute("SELECT taskName from taskinfo where category=1 and taskStatus=1")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("2. Urgent but Not Important-")
        cursor.execute("SELECT taskName from taskinfo where category=2 and taskStatus=1")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("3. Not Urgent but Important-")
        cursor.execute("SELECT taskName from taskinfo where category=3 and taskStatus=1")
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("4. Not Urgent and Not Important-")
        cursor.execute("SELECT taskName from taskinfo where category=4 and taskStatus=1")
        result=cursor.fetchall()
        for i in result:
            print(i[0])


    elif fil in tag_list:
        print("1. Urgent and Important-")
        sql="SELECT taskName from taskinfo where category=1 and taskStatus=0 and tag=%s"
        cursor.execute(sql,(fil,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("2. Urgent but Not Important-")
        sql="SELECT taskName from taskinfo where category=2 and taskStatus=0 and tag=%s"
        cursor.execute(sql,(fil,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("3. Not Urgent but Important-")
        sql="SELECT taskName from taskinfo where category=3 and taskStatus=0 and tag=%s"
        cursor.execute(sql,(fil,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])

        print("4. Not Urgent and Not Important-")
        sql="SELECT taskName from taskinfo where category=4 and taskStatus=0 and tag=%s"
        cursor.execute(sql,(fil,))
        result=cursor.fetchall()
        for i in result:
            print(i[0])



def addTag():
    tag=input("Enter Tag Name-")
    print("Tag Type- \nWiFi- 1\nWeather- 2")
    tp=int(input("Enter Type-"))
    if (tp==1):
        print("The Current Connected Wifi will be taken as parameter")
        
        wifi=get_local_ip()
        val=(tag,wifi)
        sql=("INSERT INTO TAGS (tagname,wifi) VALUES (%s,%s)")
        cursor.execute(sql,val)
        connection.commit()
        print("Tag Added Successfully")

    elif tp==2:
        print("The Current Location will be taken as parameter")
        location=pick_city(API_KEY, port=5051)
        val=(tag,location)
        sql=("INSERT INTO TAGS (tagname,location) VALUES (%s,%s)")
        cursor.execute(sql,val)
        connection.commit()
        print("Tag Added Successfully")




def pick_city(API_KEY, port=5051):
    app = Flask(__name__)
    result = {"city": None}

    HTML = """
    <!doctype html>
    <html><head>
      <meta charset="utf-8">
      <title>Pick Location</title>
      <style>html,body,#map{height:100%;margin:0;padding:0}</style>
    </head>
    <body><div id="map"></div>
    <script>
      let map, marker;
      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center:{lat:28.6,lng:77.2},zoom:6
        });
        map.addListener('click', e=>{
          if(marker)marker.setMap(null);
          marker=new google.maps.Marker({position:e.latLng,map});
          const lat=e.latLng.lat(),lng=e.latLng.lng();
          fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key={{k}}`)
          .then(r=>r.json()).then(j=>{
            let c=null;
            for(const r1 of (j.results||[]))
              for(const a of (r1.address_components||[]))
                if(a.types.includes("locality")){c=a.long_name;break;}
            fetch('/set',{method:'POST',headers:{'Content-Type':'application/json'},
              body:JSON.stringify({city:c})});
          });
        });
      }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key={{k}}&callback=initMap" async defer></script>
    </body></html>
    """

    @app.route("/")
    def index(): return render_template_string(HTML, k=API_KEY)

    @app.route("/set", methods=["POST"])
    def set_city():
        data = request.get_json()
        result["city"] = data.get("city")
        try: requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=1)
        except: pass
        return jsonify(ok=True)

    @app.route("/shutdown")
    def shutdown():
        func = request.environ.get("werkzeug.server.shutdown")
        if func: func()
        return "ok"

    def run(): app.run(port=port, debug=False, use_reloader=False)
    threading.Thread(target=run, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/")

    while result["city"] is None:
        time.sleep(0.2)
    return result["city"]


        

def get_local_ip():
    """Return current connected local IP, or None if not connected."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        ip = s.getsockname()[0]
        s.close()
        IP = str(ip)
        return IP
    except Exception:
        return None





def get_city_if_rain_predicted(city_name):
    geo_resp = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": city_name, "key": API_KEY}
    ).json()

    if not geo_resp.get("results"):
        print("Error: City not found.")
        return None

    location = geo_resp["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]

    weather = requests.get(
        "https://weather.googleapis.com/v1/forecast/hours:lookup",
        params={
            "key": API_KEY,
            "location.latitude": lat,
            "location.longitude": lng,
            "hours": 24
        }
    ).json()

    rain_chance = 0
    for hour in weather.get("forecastHours", []):
        prob = (hour.get("precipitation", {})
                    .get("probability", {})
                    .get("percent", 0))
        rain_chance = max(rain_chance, prob)

    # Step 4: Return city name only if chance > 50%
    if rain_chance >=30:
        return True
    else:
        return False





def suggestTask():
    wifi = get_local_ip()
    wifi_tags = []
    sql = "SELECT tagname FROM tags WHERE wifi=%s"
    cursor.execute(sql, (wifi,))
    result = cursor.fetchall()
    for i in result:
        wifi_tags.append(i[0])   

    for j in wifi_tags:
        sql = "SELECT taskName FROM taskinfo WHERE taskStatus=0 AND tag=%s"
        cursor.execute(sql, (j,))   
        result = cursor.fetchall()
        for k in result:
            print(k[0])

    rain_tags = []
    cursor.execute("SELECT location FROM tags")
    result = cursor.fetchall()
    for i in result:
        if i[0] is not None and i[0] != "":     
            if get_city_if_rain_predicted(i[0]): 
                sql = "SELECT tagname FROM tags WHERE location=%s"
                cursor.execute(sql, (i[0],))
                result = cursor.fetchall()
                for m in result:
                    rain_tags.append(m[0])  

    rain_tags = list(dict.fromkeys(rain_tags))

    for j in rain_tags:
        sql = "SELECT taskName FROM taskinfo WHERE taskStatus=0 AND tag=%s"
        cursor.execute(sql, (j,))   
        result = cursor.fetchall()
        for k in result:
            print(k[0])
        
    


    
        
    
    
    







            


    
        
            
        
        
        






    
    
    
    
    
    
