import mysql.connector as sqlcon
from mysql.connector import Error
import matplotlib.pyplot as plt 
import numpy as np
from statistics import mean

try:
    np.set_printoptions(formatter={'float_kind':'{:.4f}'.format})
    strFile = "lectura.png"
    mydb= sqlcon.connect(
        host="data-2018.ctuemwnho5fn.us-east-1.rds.amazonaws.com",
        port=3306,
        user="admin",
        passwd="Elq2GaxlhUQWHUmW5Mo5",
        database="DataMetasys"
    )
    if mydb.is_connected():
        print("Conexion exitosa")
        infoserver = mydb.get_server_info()
        print("Info del servidor:",infoserver)
    #Creating a cursor object using the cursor() method
    cursor = mydb.cursor()
    
    #Info to search in database
    year=2018#input('Año: ')
    month=8
    day=26
    ts=2
    precio_kWh=850
    #EXTRACCION DE INFORMACION
    if ts == 0:
        print('Caso diario')
        exe=""" SELECT date_format(DATE,"%d-%M-%Y"),time_format(TIME,"%r"),FORMAT(P_ACTIVA,2),FORMAT(E_ACTIVA,2) from DataMetasys.D_2018 
        WHERE (YEAR(DATE)= """+str(year)+""" AND MONTH(DATE)="""+str(month)+""" AND DAY(DATE)="""+str(day)+""" 
        )or ((DAY(DATE)="""+str(day+1)+""" and month(DATE)="""+str(month)+""")  and (TIME='00:00:00'))"""
        cursor.execute(exe)
        result = cursor.fetchall()
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        leng_arr-=1
    if ts ==  1:
        exe=""" SELECT date_format(DATE,"%d-%M-%Y"),time_format(TIME,"%r"),FORMAT(P_ACTIVA,2),FORMAT(E_ACTIVA,2) from DataMetasys.D_2018 
        WHERE ((TIME='00:00:00') or (TIME='23:00:00')) AND YEAR(DATE)= """+str(year)+""" AND MONTH(DATE)="""+str(month)+""" """
        cursor.execute(exe)
        result = cursor.fetchall()
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        leng_arr/=2
    if ts == 2:
        print('Caso Anual')
        exe=""" SELECT date_format(DATE,"%d-%M-%Y"),time_format(TIME,"%r"),FORMAT(P_ACTIVA,2),FORMAT(E_ACTIVA,2) from DataMetasys.D_2018 
        WHERE (DATE IN (SELECT MIN(DATE) FROM DataMetasys.D_2018 GROUP BY MONTH(DATE), YEAR(DATE) )AND TIME IN (SELECT MIN(TIME) FROM DataMetasys.D_2018 )) 
        OR (DATE IN (SELECT MAX(DATE) FROM DataMetasys.D_2018 GROUP BY MONTH(DATE), YEAR(DATE) ) AND TIME IN (SELECT MAX(TIME) FROM DataMetasys.D_2018 ))"""
        cursor.execute(exe)
        result = cursor.fetchall()
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        arr = np.asarray(result)#convertir a matriz
        leng_arr=arr.shape[0] #largo del matriz
        leng_arr/=2
    #EXTRACCION DEL CONSUMO
    n=-1 #variable contadora
    n1=0#variable contadora
    vf=[] #variable de valores
    vf_moment=0
    vf_ac=0
    vf_max=0
    vf_min=10000000
    for i in range((int(leng_arr))):
        n+=1
        n1+=1
        v1=arr[n,3]
        v2=arr[n1,3]
        v1f=float(v1.replace(",",""))
        v2f=float(v2.replace(",",""))
        vf_moment=v2f-v1f
        vf.append(v2f-v1f)
        vf_ac+=int(vf[i]) #Total acumulado de kWh
        #almacenamiento de valor max
        if vf_moment>=vf_max:
            vf_max=vf_moment
            max_info=arr[n,0:2]
        if vf_min>=vf_moment:
            vf_min=vf_moment
            min_info=arr[n,0:2]
        if ts!=0:
            n+=1
            n1+=1
    vf=np.vstack(vf)
    vf[5,0]*=2
    print(vf)
    #CALCULO DE INDICADORES
    #Consumo per capita
    Num_estudiantes=1000
    kWh_p_capita=round(float(vf_ac/Num_estudiantes),2)
    #Calculo por area
    Mtk=6408
    CalculoMt=round(float(vf_ac/Mtk),2)
    #Calculo de CO2
    Ic=164.38
    Co2=round(float((Ic*(vf_ac))/1000),2)
    # Sacar promedio
    pru=len(vf)
    largovf=vf[int(pru*0.3):int(pru*0.9)]
    vf_list=tuple(largovf.reshape(1, -1)[0])#Convertir a tuple
    Prom_consumo=round(float(mean(vf_list)),2)# sacar promedio
    porcentaje_alm=0
    porcentaje_date=0
    fig, gf1 =plt.subplots(tight_layout=True)
    if ts == 0:
        porcentdprot=0.85#0.85
        porcentuprot=1#1
        for i in range(pru):
            if i<=int(round(pru*0.26,0)):
                porcentaje=round(float(((vf[i]-Prom_consumo*porcentdprot)/Prom_consumo*porcentdprot)*100),2) #calculo instantaneo
                if porcentaje>=10:
                    porcentaje_alm=(float(vf[i]))
                    porcentaje_date=((i))
                    gf1.plot(porcentaje_date,porcentaje_alm, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="red")
            elif (i>int(pru*0.26)) and (i<int(pru*0.9)):
                porcentaje=round(float(((vf[i]-Prom_consumo*porcentuprot)/Prom_consumo*porcentuprot)*100),2) #calculo instantaneo
                if porcentaje>=20:
                    porcentaje_alm=(float(vf[i]))
                    porcentaje_date=((i))
                    gf1.plot(porcentaje_date,porcentaje_alm, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="red")
            elif i>=int(pru*0.9):
                porcentaje=round(float(((vf[i]-Prom_consumo*porcentdprot)/Prom_consumo*porcentdprot)*100),2) #calculo instantaneo
                if porcentaje>=10:
                    porcentaje_alm=(float(vf[i]))
                    porcentaje_date=((i))
                    gf1.plot(porcentaje_date,porcentaje_alm, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="red")
    if ts ==  1:
        porcentdprot=1#0.85
        porcentuprot=1#1
        for i in range(pru):
            porcentaje=round(float(((vf[i]-Prom_consumo*porcentuprot)/Prom_consumo*porcentuprot)*100),2) #calculo instantaneo
            print(porcentaje)
            if porcentaje>=15:
                porcentaje_alm=(float(vf[i]))
                porcentaje_date=((i))
                gf1.plot(porcentaje_date,porcentaje_alm, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="red")
    if ts == 2:
        porcentdprot=1#0.85
        porcentuprot=1#1
        for i in range(pru):
            porcentaje=round(float(((vf[i]-Prom_consumo*porcentuprot)/Prom_consumo*porcentuprot)*100),2) #calculo instantaneo
            print(porcentaje)
            if porcentaje>=15:
                porcentaje_alm=(float(vf[i]))
                porcentaje_date=((i))
                gf1.plot(porcentaje_date,porcentaje_alm, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="red")
    gf1.plot(vf,'k')

    porcentd=0.85
    porcentu=1
    if ts == 0:
        # int(pru*0.3):int(pru*0.9)
        gf1.plot([0,(int(pru*0.26))],[Prom_consumo*porcentd, Prom_consumo*porcentd], 'r--', lw=2,)
        gf1.plot([(int(pru*0.3)),(int(pru*0.85))],[Prom_consumo*porcentu, Prom_consumo*porcentu], 'r--', lw=2,)
        gf1.plot([(int(pru*0.9)),len(arr)],[Prom_consumo*porcentd, Prom_consumo*porcentd], 'r--', lw=2,)
        default_x_ticks = range(len(arr))
        plt.xticks(default_x_ticks, arr[:,1])
        gf1.tick_params(axis='x', rotation=75)
        plt.xlabel('Dia')# naming the x axis
        plt.ylabel('kWh')# naming the y axis
        def meses(i):
            switcher={
                1:'Enero',
                2:'Febrero',
                3:'Marzo',
                4:'Abril',
                5:'Mayo',
                6:'Junio',
                7:'Julio',
                8:'Agosto',
                9:'Septiembre',
                10:'Octubre',
                11:'Noviembre',
                12:'Diciembre'
                }
            return switcher.get(i,"Invalid day of week")
        monthplot=meses(month)
        plt.title('Consumo de energia electrica\npara el dia '+str(day)+ ' del mes '+monthplot+' de '+str(year))
        plt.grid(color = 'grey', linestyle = '--', linewidth = 0.5)
    if ts == 1:
        gf1.plot([0,len(arr)/2],[Prom_consumo*1.15, Prom_consumo*1.15], 'r--', lw=2,)
        days_of_month=[]
        for i in range(int(leng_arr*2)):
            if i%2!=0:
                days_of_month.append(arr[i,0])
        default_x_ticks=range(len(days_of_month))
        plt.xticks(default_x_ticks, days_of_month)
        gf1.tick_params(axis='x', rotation=90)
        plt.xlabel('Dias del mes')# naming the x axis
        plt.ylabel('kWh')# naming the y axis
        def meses(i):
            switcher={
                1:'Enero',
                2:'Febrero',
                3:'Marzo',
                4:'Abril',
                5:'Mayo',
                6:'Junio',
                7:'Julio',
                8:'Agosto',
                9:'Septiembre',
                10:'Octubre',
                11:'Noviembre',
                12:'Diciembre'
                }
            return switcher.get(i,"Invalid day of week")
        monthplot=meses(month)
        plt.title('Consumo de energia electrica para el mes '+monthplot+' de '+str(year))
        plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        
    if ts == 2:
        gf1.plot([0,(len(arr)/2)-1],[Prom_consumo, Prom_consumo], 'r--', lw=2,)
        months_of_year=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        default_x_ticks=range(len(months_of_year))
        plt.xticks(default_x_ticks, months_of_year)
        gf1.tick_params(axis='x', rotation=70)
        plt.xlabel('Meses del Año')# naming the x axis
        plt.ylabel('kWh')# naming the y axis
        plt.title('Consumo de energia electrica para el año '+str(year))
        plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
    plt.show()

except Error as ex:
    print("Error durante la conexion",ex)

finally:
    if mydb:
        mydb.close()
        print("La conexion se ha finalizado")
