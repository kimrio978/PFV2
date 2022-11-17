import mysql.connector as sqlcon
from mysql.connector import Error
import matplotlib.pyplot as plt 
import numpy as np
from statistics import mean
import locale as prft
import os

def func_lectura(month,day,ts):
    json_data = {}
    try:
        np.set_printoptions(formatter={'float_kind':'{:.4f}'.format})
        strFile = "lectura.png"
        # if os.path.isfile(strFile):
        #     os.remove(strFile)
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
        vf_list=tuple(vf.reshape(1, -1)[0])#Convertir a tuple
        Prom_consumo=round(float(mean(vf_list)),2)# sacar promedio
        #Indicadores Generales
        json_data.update({"v0":"INDICADORES GENERALES"})
        json_data.update({"v1":"Consumo total en el periodo de estudio "+str(vf_ac)+" kWh"})
        json_data.update({"v2":"Consumo promedio del periodo de estudio "+str(Prom_consumo)+" kWh"})
        json_data.update({"v3":"Consumo por area construida en el periodo de estudio "+str(CalculoMt)+" kWh/m2"})
        json_data.update({"v4":"Consumo per capita en el periodo de estudio "+str(kWh_p_capita)+"kWh/1000 estudiantes"})
        json_data.update({"v5":"Produccion de CO2 en el periodo de estudio es de "+str(Co2)+" kg de CO2"})
        #Consumo MAXIMO Y MINIMO
        json_data.update({'v6':f'INDICADORES DE CONSUMO MAXIMO Y MINIMO'})
        json_data.update({'v7':f'El maximo consumo se registro el dia {max_info[0]} a las {max_info[1]} y fue de {vf_max} kWh'})
        json_data.update({'v8':f'El minimo consumo se registro el dia {min_info[0]} a las {min_info[1]} y fue de {vf_min} kWh'})
        # Precio del kwh para la medicion
        prft.setlocale(prft.LC_ALL, '')
        precio_kWh=850
        P_total=precio_kWh*vf_ac
        json_data.update({'v81':'INDICADORES DE COSTOS'})
        json_data.update({'v9':'El kWh se encuentra a $ '+str(precio_kWh)+' COP'})
        json_data.update({'v91':"El precio total del periodo visualizado es de: "+prft.currency(float(P_total), grouping=True)+", este periodo muestra un total de "+str(vf_ac)+" kWh"})
        
        #Porcentaje aumentado con respecto al consumo promedio de las mediciones
        porcentaje_alm=[]
        porcentaje_date=[]
        crit_value=0
        numero=0
        crit_value_date=0
        for i in range(len(vf)):
            porcentaje=round(float(((vf[i]-Prom_consumo)/Prom_consumo)*100),2) #calculo instantaneo
            #porcentaje_alm.append(round(float(((vf[i]-Prom_consumo)/Prom_consumo)*100),2)) #almacen de valor de porcentaje
            #porcentaje_date.append(arr[i,0:2]) #almacen de la fecha
            if porcentaje>=30:
                crit_value=float(vf[i])
                crit_value_date=(arr[i*2,0:2])
                json_data.update({f'M{numero}':f'{numero}- La medicion es del dia {crit_value_date[0]} a las {crit_value_date[1]} con un valor de {crit_value} kWh, este tiene {porcentaje} % de diferencia con respecto al promedio ({Prom_consumo} kWh)'})
                if numero==0:
                    json_data.update({'A':'MEDICIONES ATIPICAS:'})
                numero+=1
        #IMPRESION DE GRAFICAS
        fig, gf1 =plt.subplots(tight_layout=True)
        gf1.plot(vf)

        if ts == 0:
            default_x_ticks = range(len(arr))
            plt.xticks(default_x_ticks, arr[:,1])
            gf1.tick_params(axis='x', rotation=90)
            plt.xlabel('Dia')# naming the x axis
            plt.ylabel('kWh')# naming the y axis
            plt.title('Consumo de energia electrica para el dia '+str(day)+ ' del mes '+str(month)+' de '+str(year))
            plt.grid(color = 'grey', linestyle = '--', linewidth = 0.5)
        if ts == 1:
            days_of_month=[]
            for i in range(int(leng_arr*2)):
                if i%2!=0:
                    days_of_month.append(arr[i,0])
            default_x_ticks=range(len(days_of_month))
            plt.xticks(default_x_ticks, days_of_month)
            gf1.tick_params(axis='x', rotation=90)
            plt.xlabel('Dias del mes')# naming the x axis
            plt.ylabel('kWh')# naming the y axis
            plt.title('Consumo de energia electrica para el mes '+str(month)+' de '+str(year))
            plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
            
        if ts == 2:
            months_of_year=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
            default_x_ticks=range(len(months_of_year))
            plt.xticks(default_x_ticks, months_of_year)
            gf1.tick_params(axis='x', rotation=70)
            plt.xlabel('Meses del Año')# naming the x axis
            plt.ylabel('kWh')# naming the y axis
            plt.title('Consumo de energia electrica para el año '+str(year))
            plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

        # # function to show the plot
        # plt.show()
        plt.savefig(strFile)

    except Error as ex:
        print("Error durante la conexion",ex)
        return {"error":f"{ex}"}

    finally:
            if mydb:
                mydb.close()
                print("La conexion se ha finalizado")
                return json_data