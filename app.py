#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import os
import logging
import mysql.connector as mysql
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s APP %(threadName)s : %(message)s'
                    )

@app.route('/account/<string:user>/')
def getuser(user):
    duser = user
    json_data = []
    resultjson = []
    HOST = os.environ['MYSQL_HOST']
    USER = os.environ['MYSQL_USER']
    PASSWORD = os.environ['MYSQL_PASSWORD_KEY']
    DATABASE = os.environ['MYSQL_DATABASE']
    if duser is None:
        return "<h1>No User</h1>",404
    conn = mysql.connect(host=HOST,database=DATABASE, 
                            user=USER,password=PASSWORD)
    cursor = conn.cursor()
    if duser == 'all':
        cursor.execute("SELECT * FROM ACCOUNT")
        row_headers = [x[0] for x in cursor.description]
        result = cursor.fetchall()
        for x in result:
            json_data.append(dict(zip(row_headers, x)))
    else:
        cursor.execute("SELECT * FROM ACCOUNT where NAME='{}' ".format(duser))
        row_headers = [x[0] for x in cursor.description]
        result = cursor.fetchall()
        for x in result:
            json_data.append(dict(zip(row_headers, x)))
    if json_data != []:
        resultjson = str(json_data)[1:-1].strip()
    elif json_data == []:
        resultjason = 'NO DATA'
    else:
        resultjason = json_data
    if duser in resultjson or duser == 'all':
        if resultjson == []:
            app.logger.info('DATA -- Found For request ' + duser
                            + ' Output: NO DATA ')
            return jsonify({'data': resultjson})
        else:
            app.logger.info('DATA -- Found For request ' + duser
                            + ' Output: ' + resultjson)
            return jsonify({'data': resultjson})
    else:
        app.logger.info('DATA -- NOT Found in Database ' + duser)
        return jsonify({'message': 'data not found in db',
                       'value': duser})


