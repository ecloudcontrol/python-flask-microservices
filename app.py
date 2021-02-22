#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
#import pymysql
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
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(DATABASE,table))
    r = cursor.fetchall()
    if r[0][0] < 1:
        table=sample(conn,cursor)
    if duser == 'all':
        cursor.execute("SELECT * FROM {}".format(table))
        row_headers = [x[0] for x in cursor.description]
        result = cursor.fetchall()
        for x in result:
            json_data.append(dict(zip(row_headers, x)))
    else:
        cursor.execute("SELECT * FROM {} where NAME='{}' ".format(table,duser))
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


def sample(conn, cursor):
    with open('./create_account_model.sql', 'r',
                  encoding='utf-8') as sql_file:
        data = sql_file.read().split(';')
    flag = 0
    txt=data[0]
    global table
    x = txt.split(" ")
    for d in x:
        if d == 'TABLE' or d == 'table' or flag == 1:
            if flag == 1:
                table=d
                break;
            else:
                flag = 1
    app.logger.info("table is :" + table)
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(DATABASE,table))
    r = cursor.fetchall()
    if r[0][0] < 1:
        with open('./create_account_model.sql', 'r',
                  encoding='utf-8') as sql_file:
            data = sql_file.read().split(';')
            app.logger.info(data)
            for d in data:
                if d and d.strip():
                    app.logger.info(d)
                    cursor.execute(d)
            conn.commit()
    return table 


if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=8080)
