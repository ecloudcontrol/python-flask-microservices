#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, abort
import pymysql
import os
import logging
import mysql.connector as mysql
app = Flask(__name__)
api = Api(app)
HOST = os.environ['MYSQL_HOST']
USER = os.environ['MYSQL_USER']
PASSWORD = os.environ['MYSQL_PASSWORD_KEY']
DATABASE = os.environ['MYSQL_DATABASE']
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s APP %(threadName)s : %(message)s'
                    )
table=""

class MyConverter(mysql.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        row = super(MyConverter, self).row_to_python(row, fields)

        def to_unicode(col):
            if isinstance(col, bytearray):
                return col.decode('utf-8')
            return col

        return [to_unicode(col) for col in row]


class Apidatadelete(Resource):

    def __init__(self):


        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='The ID of  user to delete',
                                   location='json')
        conn = cursor = None
        super(Apidatadelete, self).__init__()

    def delete(self, user):
        args = self.reqparse.parse_args()
        datauser = args['id']
        if user == None or datauser == '':
            app.logger.warning('Enter Name to Delete')
            return ('Enter Name to Delete', 404)
        if user != datauser:
            app.logger.warning('Enter data username and url username mismatch '
                               )
            return ('Enter data username and url username mismatch ',
                    404)
        conn = mysql.connect(converter_class=MyConverter, host=HOST,
                             database=DATABASE, user=USER,
                             password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = 'ACCOUNT'".format(DATABASE))
        r = cursor.fetchall()
        if r[0][0] < 1:
            return 'NO table'
        cursor.execute('SELECT NAME FROM ACCOUNT where ID={} '.format(datauser))
        result1 = cursor.fetchall()
        cursor.execute('DELETE FROM ACCOUNT WHERE ID={} '.format(str(datauser)))
        conn.commit()
        cursor.execute('SELECT NAME FROM ACCOUNT where ID={} '.format(datauser))
        result = cursor.fetchall()
        if result == [] and result1 != []:
            app.logger.info('DATA -- Successfull Deleted...')
            return jsonify({'Data Deleted ': datauser})
        else:
            app.logger.warning('DATA -- Not Deleted...')
            return jsonify({"Data already deleted or doesn't exsist": result})


class Apigetdata(Resource):

    def __init__(self):


        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='The Keyword all',
                                   location='json')
        conn = cursor = None
        super(Apigetdata, self).__init__()

    def get(self, user):
        duser = user
        if duser is None:
            abort(404)
        conn = mysql.connect(converter_class=MyConverter, host=HOST,
                             database=DATABASE, user=USER,
                             password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(DATABASE,table))
        r = cursor.fetchall()
        if r[0][0] < 1:
            sample()


        json_data = []
        resultjson = []
        if duser == 'all':
            cursor.execute('SELECT * FROM ACCOUNT ')
            row_headers = [x[0] for x in cursor.description]
            result = cursor.fetchall()
            for x in result:
                json_data.append(dict(zip(row_headers, x)))
        else:
            cursor.execute("SELECT * FROM ACCOUNT where id='{}' ".format(duser))
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


class Apipostdata(Resource):

    def __init__(self):


        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='The User ID ', location='json')
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='The Username', location='json')
        self.reqparse.add_argument('fullname', type=str, required=True,
                                   help='The Users fullname',
                                   location='json')
        self.reqparse.add_argument('login', type=str, required=True,
                                   help='The Users login ID',
                                   location='json')
        self.reqparse.add_argument('email', type=str, required=True,
                                   help='The User email ID',
                                   location='json')
        conn = cursor = None
        super(Apipostdata, self).__init__()

    def post(self, user):
        args = self.reqparse.parse_args()
        dataid = args['id']
        datname = args['name']
        datafullname = args['fullname']
        datalogin = args['login']
        dataemail = args['email']
        if user == None and datname == '':
            abort(404)
        if user != datname:
            app.logger.warning('Entered data username and url username mismatch '
                               )
            return ('Enter data username and url username mismatch ',
                    404)
        conn = mysql.connect(converter_class=MyConverter, host=HOST,
                             database=DATABASE, user=USER,
                             password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE  IF NOT EXISTS MyUsers ( userid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(100) ,submission_date DATE)'
                       )


        cursor.execute("INSERT INTO ACCOUNT Values({},'{}','{}','{}','{}')".format(dataid,
                       datname, datafullname, datalogin, dataemail))
        conn.commit()
        cursor.close()
        conn.close()
        resultjson = str(args).strip()
        app.logger.info('DATA -- Successfully Posted the Data '
                        + resultjson + ' in database')
        return jsonify({'Data posted ': resultjson})


api.add_resource(Apipostdata, '/find/create/user/<string:user>')
api.add_resource(Apigetdata, '/find/userid/<string:user>')
api.add_resource(Apidatadelete, '/find/delete/userid/<string:user>')

@app.route('/')
def welcome():
    return "<h1>Hello Welcome To APPZ Webserver </h1>"

def sample():
    conn = mysql.connect(converter_class=MyConverter, host=HOST,
                         database=DATABASE, user=USER,
                         password=PASSWORD)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
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


if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=8080)
