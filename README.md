# PF
## RUTAS
- ["GET"] localhost:5000/
- ["GET","POST"] localhost:5000/lectura

### Ruta raiz "/"
-  Allow methods : "GET"
   -  Response "GET" : ```` {
     "title": "prueba",
     "version": "v0.0.1"
   } ````

### Ruta lectura "/lectura"
- Allow methods : 
  - "GET"
    - Response "GET" : ````{
  "data": "ES UN POST MANIIII"
}````
  - "POST"
    - Body: ````{
    "month":7,
    "day":20,
    "ts":0
}````
- Response ````{"data":{"llave1":"Valor1",
                    "iamge":[BASE64],
                    "proceso":"hecho" }}````


## Run project
````python entrypoint.py````