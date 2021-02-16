from flask import Flask, Response, render_template,jsonify,request
import pymysql,json
from flask_restful import Resource, Api , reqparse, abort, marshal, fields
import os,logging
from flaskext.mysql import MySQL
import mysql.connector as mysql
from json import dumps, loads, JSONEncoder, JSONDecoder
app = Flask(__name__)
api = Api(app)

HOST=os.environ["MYSQL_HOST"]
USER=os.environ["MYSQL_USER"]
PASSWORD=os.environ['MYSQL_PASSWORD_KEY']
DATABASE=os.environ["MYSQL_DATABASE"]

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s %(levelname)s APP %(threadName)s : %(message)s")

class MyConverter(mysql.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        row = super(MyConverter, self).row_to_python(row, fields)

        def to_unicode(col):
            if isinstance(col, bytearray):
                return col.decode('utf-8')
            return col

        return[to_unicode(col) for col in row]

class Apidatadelete(Resource):
    def __init__(self):
        # Initialize The Flsak Request Parser and add arguments as in an expected request
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True, help="The keyword delete", location="json")
        conn = None
        cursor = None
        conn = mysql.connect(converter_class=MyConverter,host=HOST, database=DATABASE,user=USER, password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        super(Apidatadelete, self).__init__()
    def delete(self, user):
        args = self.reqparse.parse_args()
        datauser=args['username']
        if user == None or datauser == "":
            app.logger.warning("Enter Name to Delete")
            return "Enter Name to Delete" ,404
        if user != datauser:
            app.logger.warning("Enter data username and url username mismatch ")
            return "Enter data username and url username mismatch " ,404
        conn = mysql.connect(converter_class=MyConverter,host=HOST, database=DATABASE,user=USER, password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = 'MyUsers'".format(DATABASE))
        r = cursor.fetchall()
        if r[0][0] < 1 :
            return "NO table"
        cursor.execute("SELECT username FROM MyUsers where username='{}' ".format(datauser))
        result1 = cursor.fetchall()
        cursor.execute("DELETE FROM MyUsers WHERE username='{}' ".format(str(datauser)))
        conn.commit()
        cursor.execute("SELECT username FROM MyUsers where username='{}' ".format(datauser))
        result = cursor.fetchall()
        if result == [] and result1 != []:
            app.logger.info("DATA -- Successfull Deleted...")
            return  jsonify({"Data Deleted ":datauser})
        else:
            app.logger.warning("DATA -- Not Deleted...")
            return jsonify({"Data already deleted or doesn't exsist":result})
class Apigetdata(Resource):
    def __init__(self):
        # Initialize The Flsak Request Parser and add arguments as in an expected request
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True, help="The Keyword all", location="json")
        conn = None
        cursor = None
        conn = mysql.connect(converter_class=MyConverter,host=HOST, database=DATABASE,user=USER, password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        super(Apigetdata, self).__init__()
    def get(self,user):
        duser = user
        if duser is None:
            abort(404)
        conn = mysql.connect(converter_class=MyConverter,host=HOST,database=DATABASE, user=USER, password=PASSWORD)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{}' AND table_name = 'MyUsers'".format(DATABASE))
        r = cursor.fetchall()
        if r[0][0] < 1 :
            return "NO table"

        json_data=[]
        resultjson = []
        if duser == "all":
            cursor.execute("SELECT * FROM MyUsers ")
            row_headers=[x[0] for x in cursor.description]
            result = cursor.fetchall()
            for x in result:
                json_data.append(dict(zip(row_headers,x)))
        else:
            cursor.execute("SELECT * FROM MyUsers where username='{}' ".format(duser))
            row_headers=[x[0] for x in cursor.description]
            result = cursor.fetchall()
            for x in result:
                json_data.append(dict(zip(row_headers,x)))

        if json_data != [] :
            resultjson= str(json_data)[1:-1].strip()
        elif json_data == []:
            resultjason = "NO DATA"
        else:
            resultjason = json_data
        if duser in resultjson or duser == "all":
            if resultjson == []:
                app.logger.info("DATA -- Found For request "+duser+" Output: NO DATA ")
                return  jsonify({"data":resultjson})
            else:
                app.logger.info("DATA -- Found For request "+duser+" Output: "+resultjson)
                return  jsonify({"data":resultjson})
        else:
            app.logger.info("DATA -- NOT Found in Database "+ duser)
            return  jsonify({"message":"data not found in db" , "value" : duser})
class Apipostdata(Resource):

    def __init__(self):
        # Initialize The Flsak Request Parser and add arguments as in an expected request
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True, help="The Username", location="json")
        conn = None
        cursor = None
        conn = mysql.connect(converter_class=MyConverter,host=HOST,database=DATABASE, user=USER, password=PASSWORD)
        cursor = conn.cursor()
        super(Apipostdata, self).__init__()

    def post(self,user):
        args = self.reqparse.parse_args()
        datauser=args['username']
        if user == None and datauser == "":
            abort(404)
        if user != datauser:
            app.logger.warning("Entered data username and url username mismatch ")
            return "Enter data username and url username mismatch " ,404
        conn = mysql.connect(converter_class=MyConverter,host=HOST,database=DATABASE, user=USER, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE  IF NOT EXISTS MyUsers ( userid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(100) ,submission_date DATE)")
        cursor.execute("INSERT INTO MyUsers(username,submission_date)VALUES('{}',NOW())".format(datauser))
        conn.commit()
        cursor.close()
        conn.close()
        resultjson= str(args).strip()
        app.logger.info("DATA -- Successfully Posted the Data "+ resultjson +" in database")
        return jsonify({"Data posted ":resultjson})


api.add_resource(Apipostdata, "/find/create/<string:user>")
api.add_resource(Apigetdata, "/find/user/<string:user>")
api.add_resource(Apidatadelete, "/find/delete/<string:user>")

if __name__ == '__main__':
    app.run(use_reloader=True,host="0.0.0.0",port=8080)

