#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from bottle import route, run, request
import MySQLdb as mdb
import time

con = mdb.connect('localhost', 'root', 'leonardis', 'gallery')
cur = con.cursor();


@route('/get/photos', method='GET')
def get_photos():
    photos = []

    data = request.body.readline()
    print data
    '''if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not 'user_id' in entity:
        return {"error": 400, "message": "No user ID received"}'''

    cur.execute("SELECT users_f.user_follow_id, users.user_name, images.uri, images.description, images.status, (select count(*) from likes where likes.Images_id=images.id) as likes from (select uf.* from users u join users_follow uf on u.id = uf.users_id where u.id=1) as users_f join images on users_f.user_follow_id = images.users_id join users on users_f.user_follow_id = users.id")
    rows = cur.fetchall()
    for row in rows:
        user_id = row[0]
        user_name = row[1]
        image_uri = row[2]
        image_description = row[3]
        image_status = row[4]
        likes = row[5]
        if image_status == 1:
            photos.insert(0, {
                "user_id": user_id,
                "user_name": user_name,
                "image_uri": image_uri,
                "image_description": image_description,
                "likes": likes
            })

    return {"photos": photos}


@route('/get/users', method='GET')
def get_users():
    users = []

    data = request.body.readline()
    print data
    '''if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not 'user_id' in entity:
        return {"error": 400, "message": "No user ID received"}'''

    cur.execute("SELECT users_f.user_follow_id, users.user_name from (select uf.* from users u join users_follow uf on u.id = uf.users_id where u.id=1) as users_f join users on users_f.user_follow_id = users.id")
    rows = cur.fetchall()
    for row in rows:
        user_id = row[0]
        user_name = row[1]
        users.insert(0, {
            "user_id": user_id,
            "user_name": user_name
        })

    return {"users": users}


@route('/get/user', method='GET')
def get_user():

    data = request.body.readline()
    print data
    '''if not data:
        return{"error": 400, "message": "No data received"}
    entity = json.loads(data)
    if not 'user_id' in entity:
        return {"error": 400, "message": "No user ID received"}'''

    cur.execute("SELECT * FROM users WHERE id=1")
    rows = cur.fetchall()
    for row in rows:
        user_id = row[0]
        user_name = row[3]
        user_full_name = row[1]+" "+row[2]
        user_email = row[4]
        user_image = row[5]

    return {"user_id": user_id, "user_name": user_name, "user_full_name": user_full_name, "user_email": user_email, "user_image": user_image}

run(host='localhost', port=8080, debug=True)