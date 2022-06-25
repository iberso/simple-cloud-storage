from http import HTTPStatus
import json
from itsdangerous import base64_decode, base64_encode
from nameko.extensions import DependencyProvider
import mysql.connector
import uuid
from mysql.connector import Error
from mysql.connector import pooling

class DatabaseWrapper:
    connection = None

    def __init__(self, connection):
        self.connection = connection
    
    def upload_file(self, data):
        try:
            dataUpload = json.loads(data)
            cursor = self.connection.cursor(prepared=True)
            query = """
                    INSERT INTO files (id,owner,file_name,mime_type,Base64Content) 
                    VALUES (%s,%s,%s,%s,%s)
                    """
            cursor.execute(query,(str(uuid.uuid4()),dataUpload['user_id'],dataUpload['filename'],dataUpload['mimetype'],dataUpload['base64Content']))
            self.connection.commit()
            cursor.close()

            return json.dumps({
                'message':'Success Uploading File',
                'status':HTTPStatus.OK
            })
        except:
            return json.dumps({
                'message':'Error Uploading File',
                'status':HTTPStatus.BAD_REQUEST
            })
        
    def download_file(self,file_id):
        try:
            cursor = self.connection.cursor(prepared=True)
            query = "SELECT file_name,mime_type,Base64Content from files WHERE id=%s"
            cursor.execute(query,(file_id, ))
            row = cursor.fetchone()
            self.connection.commit()
            cursor.close()
            
            datafile = {
                'file_name': row[0],
                'mime_type':row[1],
                'base64Content':row[2]
            }
            return json.dumps({
                'message':"success",
                'data':datafile,
                'status':HTTPStatus.OK
            })
        except:
            return json.dumps({
                'message':"Database Error",
                'data':[],
                'status':HTTPStatus.BAD_REQUEST
            })
    
    def fetch_file_access(self,id_file):
        try:
            cursor = self.connection.cursor(prepared=True)
            queryy = """
            SELECT u.name,f.owner,f.sharing, 
                (SELECT name FROM users WHERE id = f.sharing) 
            FROM files f 
            JOIN users u 
            ON f.owner=u.id 
            WHERE f.id=%s"""

            query = """
            SELECT owner,sharing 
            FROM files WHERE id=%s
            """

            cursor.execute(query,(id_file, ))
            row = cursor.fetchone()
            self.connection.commit()
            cursor.close()
            data = {
                'owner':{
                    'id':row[0],
                    'name':""
                },
                'share_to':{
                    'id':row[1],
                    'name':""
                }
            }
            dataa = {
                'owner':{
                    'id':row[1],
                    'name':row[0]
                },
                'share_to':{
                    'id':row[2],
                    'name':row[3]
                }
            }

            return json.dumps({
                'data':data,
                'message':'success',
                'status':HTTPStatus.OK
            })
        except:
            return json.dumps({
                'data': [],
                'message':'File not Found',
                'status': HTTPStatus.NOT_FOUND
            })

    def sharing_file(self,file_id, share_to):
        try:
            cursor = self.connection.cursor(prepared=True)
            query = """
                    UPDATE files
                    SET sharing=%s
                    WHERE id=%s"""
            cursor.execute(query,(share_to, file_id, ))
            row = cursor.fetchone()
            self.connection.commit()
            cursor.close()
            return json.dumps({
                'message':"success",
                'status':HTTPStatus.OK
            })
        except:
            return json.dumps({
                'message':"Database Errorr",
                'status':HTTPStatus.BAD_REQUEST
            })

    def __del__(self):
        self.connection.close()



class Database(DependencyProvider):

    connection_pool = None

    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="database_pool",
                pool_size=5,
                pool_reset_session=True,
                host='localhost',
                database='dbsimplecloudstorage',
                user='root',
                password=''
            )
        except Error as e :
            print ("Error while connecting to MySQL` using Connection pool ", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())