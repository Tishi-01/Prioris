import threading
import webbrowser
import time
import requests
from flask import Flask, request as flask_request, jsonify, render_template_string


def pick_city(api_key, port=5051):
    """Open a browser-based Google Maps city picker and return selected city name."""
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
    def index():
        return render_template_string(HTML, k=api_key)

    @app.route("/set", methods=["POST"])
    def set_city():
        data = flask_request.get_json()
        result["city"] = data.get("city")
        try:
            requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=1)
        except Exception:
            pass
        return jsonify(ok=True)

    @app.route("/shutdown")
    def shutdown():
        func = flask_request.environ.get("werkzeug.server.shutdown")
        if func:
            func()
        return "ok"

    def run():
        app.run(port=port, debug=False, use_reloader=False)

    threading.Thread(target=run, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/")

    while result["city"] is None:
        time.sleep(0.2)
    return result["city"]
