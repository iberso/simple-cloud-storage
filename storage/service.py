from http import HTTPStatus
import json
from nameko.rpc import rpc
import databasewrapper
import requests

class StorageService:
    name = 'storage_service'
    database = databasewrapper.Database()

    @rpc
    def upload_file(self, data):
        database_respones = self.database.upload_file(data)
        return database_respones
    
    @rpc
    def download_file(self,data):
        req_download = json.loads(data)
        fetch_response = requests.get('http://localhost:8000/file/'+req_download['file_id']+'/access')
        
        database_respones = {
            "message":"",
            "data":[],
            "status":""
        }

        if fetch_response.status_code == 200:
            fetch_file_data = fetch_response.json()
            if req_download['user_id'] == fetch_file_data['data']['owner']['id']:
                #kalau success berarti user yg sedang login bisa download filenya sendiri
                database_respones = self.database.download_file(req_download['file_id'])
                return database_respones
            elif req_download['user_id'] == fetch_file_data['data']['share_to']['id']:
                #bukan file owner dan kudu cek apakah file yg di req disharingkan ke user ini
                database_respones = self.database.download_file(req_download['file_id'])
                return database_respones
            else:
                #bukan file owner dan tidak dishare kan
                database_respones['message'] = "You don't have permission to access this file"
                database_respones['status'] = HTTPStatus.FORBIDDEN
                return json.dumps(database_respones)
        else:
            #file tidak ditemukan
            fetch_file_data = fetch_response.json()
            print(json.dumps(fetch_response.json()))
            database_respones['message'] = fetch_file_data['message']
            database_respones['status'] = fetch_response.status_code
            return json.dumps(database_respones)

    @rpc
    def sharing_file(self,data):
        req_sharing = json.loads(data)
        fetch_response = requests.get('/file/'+req_sharing['file_id']+'/access')
        
        database_respones = {
            "message":"",
            "data":[],
            "status":""
        }

        if fetch_response.status_code == 200:
            fetch_file_data = fetch_response.json()
            if req_sharing['user_id'] == fetch_file_data['data']['owner']['id']:
                database_respones = self.database.sharing_file(req_sharing['file_id'],req_sharing['share_to'])
                return database_respones
            else:
                #bukan file owner dan tidak dishare kan
                database_respones['message'] = "You don't have permission to access this file"
                database_respones['status'] = HTTPStatus.FORBIDDEN
                return json.dumps(database_respones)
        else:
            #file tidak ditemukan
            fetch_file_data = fetch_response.json()
            print(json.dumps(fetch_response.json()))
            database_respones['message'] = fetch_file_data['message']
            database_respones['status'] = fetch_response.status_code
            return json.dumps(database_respones)

    @rpc
    def fetch_file_access(self,id_file):
        database_response = self.database.fetch_file_access(id_file)
        data = json.loads(database_response)
        if(data['status'] != 404):
            fetch_response = requests.get('/user/'+data['data']['owner']['id'])
            if fetch_response.status_code == 200:
                print("hai1")
                fetch_owner = fetch_response.json()
                data['data']['owner']['name'] = fetch_owner['data']['username']
            
                fetch_response_sharing = requests.get('/user/'+data['data']['share_to']['id'])
                if fetch_response_sharing.status_code == 200:
                    print("hai2")
                    fetch_sharing = fetch_response_sharing.json()
                    data['data']['to_share']['name'] = fetch_sharing['data']['username']

        # database_response = {
        #     "message":"",
        #     "data":[],
        #     "status":""
        # }
        return database_response