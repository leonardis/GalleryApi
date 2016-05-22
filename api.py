#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Vtelca: 11.673728, -70.200473

import json
from bottle import route, run, request, abort
import MySQLdb as mdb
import math
import time    

con = mdb.connect('localhost', 'root', '/*4pp4rg474*/', 'appargata');
#con = mdb.connect('localhost', 'root', '', 'appargata');
cur = con.cursor()

@route('/get/sitios', method='POST')
def get_sitios():
    sitios = []
    
    data = request.body.readline()
    print "Data recibida [get sitios]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('latitud'):
        return{"error": 400, "message": "No ha incluido la latitud"}
    elif not entity.has_key('longitud'):
        return{"error": 400, "message": "No ha incluido la longitud"}
    elif not entity.has_key('distancia'):
        return{"error": 400, "message": "No ha incluido la distancia"}

    cur.execute(u"SELECT s.id_sitio, s.nombre, s.latitud, s.longitud, c.id_categoria, c.categoria FROM appargata.sitios s left join appargata.categorias c on s.categoria_id = c.id_categoria")
    rows = cur.fetchall()
    for row in rows:
        id_sitio = row[0]
        nombre = row[1]
        latitud = row[2]
        longitud = row[3]
        distancia = dist(entity['latitud'], entity['longitud'], latitud, longitud)
        id_categoria = row[4]
        categoria = row[5]
        if distancia <= entity['distancia']:
            #sitios.insert(0, {"nombre": nombre, "descripcion": descripcion, "telefono" : telefono, "latitud": latitud, "longitud" : longitud, "distancia": distancia, "id_categoria" : id_categoria, "categoria" : categoria})
            sitios.insert(0, {
                "id_sitio": id_sitio, 
                "nombre": nombre, 
                "latitud": latitud, 
                "longitud" : longitud, 
                "distancia": distancia, 
                "id_categoria" : id_categoria,
                "categoria" : categoria
            })
            
    return {"data": {"sitios": sitios}}

@route('/get/sitio', method='POST')
def get_sitio():
    urls = []
    sitio = []
    
    data = request.body.readline()
    print "Data recibida [get_sitio]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('id_usuario'):
        return{"error": 400, "message": "No ha incluido el id del usuario"}
    elif not entity.has_key('id_sitio'):
        return{"error": 400, "message": "No ha incluido la id del sitio"}

    sql = u"SELECT distinct id_sitio, nombre, descripcion, telefono, (select count(id_favorito) from favoritos where sitio_id=" + str(entity['id_sitio']) + " and usuario_id=" + str(entity['id_usuario']) + ") as favorito, (select count(id_favorito) from favoritos where sitio_id=" + str(entity['id_sitio']) + ") as favoritos FROM sitios s left join favoritos f on s.id_sitio=f.sitio_id where id_sitio = " + str(entity['id_sitio'])
    print sql
    cur.execute(sql)
    rows = cur.fetchall()
    valoracion = valoraciones(entity['id_usuario'], entity['id_sitio'])
    for row in rows:
        id_sitio = row[0]
        nombre = row[1]
        descripcion = row[2]
        telefono = row[3]
        favorito = row[4]
        favoritos = row[5]
        imgs = cur.fetchall()
        cur.execute("SELECT url FROM appargata.imagenes where sitio_id = " + str(id_sitio))
        imgs = cur.fetchall()
        for img in imgs:
            urls.insert(0, img[0])
        sitio.insert(0, {
            "id_sitio" : id_sitio, 
            "nombre" : nombre, 
            "descripcion" : descripcion,
            "telefono" : telefono,
            "favorito" : favorito,
            "favoritos" : favoritos,
            "img1" : urls[0],
            "img2" : urls[1],
            "img3" : urls[2],
            "valoracion" : str(valoracion[0]),
            "promedio" : str(valoracion[1])
        })
    return {"data": sitio[0]}

@route('/login', method='POST')
def login():
    datos = []
    
    data = request.body.readline()
    print "Data recibida [login]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('nombre'):
        return{"error": 400, "message": "No ha incluido el nombre"}
    elif not entity.has_key('apellido'):
        return{"error": 400, "message": "No ha incluido el apellido"}
    elif not entity.has_key('correo'):
        return{"error": 400, "message": "No ha incluido el correo"}
    
    nombre = entity['nombre']
    apellido = entity['apellido']
    correo = entity['correo']
    fecha_inicio = time.strftime('%Y-%m-%d %H:%M:%S')

    sql = "SELECT id_usuario FROM usuarios where correo = '" + correo + "'"
    cur.execute(sql)
    id_usuario = cur.fetchall()
    
    if not id_usuario:
        print "guardando"
        sql = "INSERT INTO usuarios (nombre, apellido, correo, fecha_inicio) values ('" + nombre + "', '" + apellido + "', '" + correo + "', '" + fecha_inicio + "')"
        print sql
        cur.execute(sql)
        con.commit()
        id_usuario = cur.lastrowid
    else:
        id_usuario = id_usuario[0][0]
    return {"id_usuario": str(id_usuario)}

@route('/fav', method='POST')
def fav():
    datos = []
    
    data = request.body.readline()
    print "Data recibida [fav]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('id_usuario'):
        return{"error": 400, "message": "No ha incluido el ID del usuario"}
    elif not entity.has_key('id_sitio'):
        return{"error": 400, "message": "No ha incluido el sitio"}
    
    id_usuario = entity['id_usuario']
    id_sitio = entity['id_sitio']

    sql = "SELECT id_favorito FROM favoritos where usuario_id = " + id_usuario + " and sitio_id = " + id_sitio
    cur.execute(sql)
    id_favorito = cur.fetchall()
    if not id_favorito:
        print "guardando"
        sql = "INSERT INTO favoritos (usuario_id, sitio_id) values (" + id_usuario + ", " + id_sitio + ")"
        cur.execute(sql)
        con.commit()
        return{"estado": "favorito creado"}
    else:
        id_favorito = id_favorito[0][0]
        # No te olvides de poner el where en el delete from
        sql = "delete from favoritos where id_favorito=" + str(id_favorito)
        cur.execute(sql)
        con.commit()
        return{"estado": "favorito eliminado"}

@route('/checkin', method='POST')
def checkin():
    datos = []
    
    data = request.body.readline()
    print "Data recibida [fav]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('id_usuario'):
        return{"error": 400, "message": "No ha incluido el ID del usuario"}
    elif not entity.has_key('id_sitio'):
        return{"error": 400, "message": "No ha incluido el sitio"}
    
    id_usuario = entity['id_usuario']
    id_sitio = entity['id_sitio']
    fecha = time.strftime('%Y-%m-%d %H:%M:%S')
    
    sql = "SELECT if(TIMEDIFF('" + fecha + "',fecha) < '06:00:00', 1, 0) as diff FROM appargata.checkins where usuario_id = " + id_usuario + " and sitio_id= " + id_sitio + " order by id_checkin desc limit 1;"
    print sql
    cur.execute(sql)
    id_favorito = cur.fetchall()
    if not id_favorito or (id_favorito and id_favorito[0][0] == 0):
        sql = "INSERT INTO checkins (usuario_id, sitio_id, fecha) values (" + id_usuario + ", " + id_sitio + ", '" + fecha + "')"
        cur.execute(sql)
        con.commit()
        estado = "exito"        
    else:
        estado = "debe esperar 6 horas"
    sql = "select count(id_checkin) from checkins where usuario_id = " + id_usuario + " and sitio_id = " + id_sitio
    cur.execute(sql)
    checkins = cur.fetchall()[0][0]
    
    sql = "select count(id_checkin) from checkins where sitio_id = " + id_sitio
    cur.execute(sql)
    totales = cur.fetchall()[0][0]
    return{"estado": estado, "checkins": checkins, "totales": totales}
        
@route('/valorar', method='POST')
def valorar():
    datos = []
    
    data = request.body.readline()
    print "Data recibida [fav]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('id_usuario'):
        return{"error": 400, "message": "No ha incluido el ID del usuario"}
    elif not entity.has_key('id_sitio'):
        return{"error": 400, "message": "No ha incluido el sitio"}
    elif not entity.has_key('valoracion'):
        return{"error": 400, "message": "No ha incluido la valoracion"}
    
    id_usuario = entity['id_usuario']
    id_sitio = entity['id_sitio']
    valoracion = entity['valoracion']
    fecha = time.strftime('%Y-%m-%d %H:%M:%S')
    
    sql = "select usuario_id from valoraciones where usuario_id=" + id_usuario + " and sitio_id=" + id_sitio
    print sql
    cur.execute(sql)
    id_usr = cur.fetchall()
    if not id_usr or (id_usr and id_usr[0][0] == 0):
        sql = "insert into valoraciones (usuario_id, sitio_id, valoracion, fecha) values(" + id_usuario + ", " + id_sitio + ", " + valoracion + ", '" + fecha + "')"
        cur.execute(sql)
        con.commit()
        estado = "valoracion agregada"    
        val = valoraciones(id_usuario, id_sitio)
    else:
        sql = "update valoraciones set valoracion=" + valoracion + " where usuario_id=" + id_usuario + " and sitio_id=" + id_sitio
        cur.execute(sql)
        con.commit()
        estado = "valoracion editada"        
        val = valoraciones(id_usuario, id_sitio)
    return {"estado": estado, "valoracion": str(val[0]), "promedio": str(val[1])}

@route('/buscar', method='POST')
def buscar():
    urls = []
    sitios = []
    datos = []
    
    data = request.body.readline()
    print "Data recibida [fav]"
    print data
    if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not entity.has_key('id_usuario'):
        return{"error": 400, "message": "No ha incluido el ID del usuario"}
    elif not entity.has_key('termino'):
        return{"error": 400, "message": "No ha incluido el termino"}
    elif not entity.has_key('latitud'):
        return{"error": 400, "message": "No ha incluido la latitud"}
    elif not entity.has_key('longitud'):
        return{"error": 400, "message": "No ha incluido la longitud"}
    elif not entity.has_key('orden'):
        entity['orden'] = '0'

    o = ['distancia asc', 'valoracion desc', 'checkins desc']
    id_usuario = entity['id_usuario']
    terminos = entity['termino'].split(" ")
    orden =o[int(entity['orden'])]
    latitud = entity['latitud']
    longitud = entity['longitud']

    print terminos
    
    where = ''
    where2 = ''
    for t in terminos:
        where += 'nombre like "%' + t + '%" or '
        where2 += 'categoria like "%' + t + '%" or '
    sql = "SELECT id_sitio, nombre, latitud, longitud, categoria_id, categoria, sqrt(pow(abs(latitud - 11.673728), 2) + pow(abs(longitud -  -70.200473), 2)) as distancia, if(ISNULL(valoracion), 0, valoracion) as valoracion, (select count(id_checkin) from checkins where sitio_id = id_sitio) as checkins FROM sitios s left join valoraciones v on s.id_sitio=v.sitio_id left join checkins c on s.id_sitio=c.sitio_id left join categorias a on s.categoria_id=a.id_categoria where " + where + where2[:-4] + " group by id_sitio order by " + orden
    print sql
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        id_sitio = row[0]
        nombre = row[1]
        latitud = row[2]
        longitud = row[3]
        distancia = dist(entity['latitud'], entity['longitud'], latitud, longitud)
        id_categoria = row[4]
        categoria = row[5]
        sitios.insert(0, {
           	"id_sitio": id_sitio,
           	"nombre": nombre,
            "latitud": latitud,
            "longitud" : longitud,
            "distancia": distancia,
            "id_categoria" : id_categoria,
            "categoria" : categoria
        })

    return {"data": {"sitios": sitios}}


def valoraciones(id_usuario, id_sitio):
    sql = "select ifnull(sum(valoracion), 0) as valoracion, ifnull(((select sum(valoracion) from valoraciones where sitio_id=" + id_sitio + ") / (select count(valoracion) from valoraciones where sitio_id=" + id_sitio + ")), 0) as promedio from valoraciones where usuario_id=" + id_usuario + " and sitio_id=" + id_sitio
    print "valoraciones SQL: " + sql
    cur.execute(sql)
    data = cur.fetchall()
    print (str(data[0][0]), str(data[0][1]))
    return (data[0][0], data[0][1])
    
                    
def dist(lat1, long1, lat2, long2):
    '''
        http://www.johndcook.com/python_longitude_latitude.html
    '''
    lat1 = float(lat1)
    long1 = float(long1)
    lat2 = float(lat2)
    long2 = float(long2)
    
    # Convert latitude and longitude to spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians
        
    # theta = longitude
    theta1 = long1 * degrees_to_radians
    theta2 = long2 * degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    # To get the distance in miles, multiply by 3960. 
    # To get the distance in kilometers, multiply by 6373.
    return arc * 6373

run(host='190.9.33.246', port=8080, debug=True)
#run(host='localhost', port=8080, debug=True)
