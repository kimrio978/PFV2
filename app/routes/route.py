from flask import Blueprint, request, jsonify
import base64

from app.utils.test1 import func_lectura

lectura_bp = Blueprint("lectura_bp",__name__, url_prefix="/lectura")


@lectura_bp.route("/",methods=["GET","POST"])
def lectura_datos():
    if request.method == "GET":
        return jsonify({
            "data":"ES UN POST MANIIII"
        })
    elif request.method == "POST":
        try:
            # Obtencion del json
            data = request.get_json()
            month = data.get("month")
            print(month)
            day = data.get("day")
            print(day)          
            ts = data.get("ts")
            print(ts)
            precio_kWh=data.get("precio_kWh")
            
            # llamado a la función
            datos = func_lectura(month,day,ts,precio_kWh)
            # Obtencion base64 img
            with open("lectura.png","rb") as file:
                img64 = base64.b64encode(file.read())
            
            return jsonify({
                "proceso":"hecho",
                "data":datos,
                "image":img64.decode('utf-8')
            })
        except Exception as e:
            return jsonify({
                "proceso": f"{e}"
            })