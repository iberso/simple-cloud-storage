import base64
from http import HTTPStatus
import json
from urllib import response
from nameko.web.handlers import http
from werkzeug.wrappers import Response
from nameko.rpc import RpcProxy
from dependencies.user.sessionwrapper import SessionProvider

class SCSGatewayService:
    name = "gateway_service"
    user_rpc = RpcProxy('user_service')
    storage_rpc = RpcProxy('storage_service')

    session_provider = SessionProvider()

    @http('POST','/user/register')
    def add_user(self,request):
        data = request.get_json()
        rpc_response = self.user_rpc.add_user(data['username'],data['password'])
        print(rpc_response['status'] == 'error')
        
        if rpc_response['status'] == 'error':
            return Response(json.dumps(rpc_response),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})
        else:
            return Response(json.dumps(rpc_response),status=HTTPStatus.OK,headers={'Content-Type':'application/json'})

    @http('POST','/user/login')
    def login(self,request):
        data = request.get_json()
        res = self.user_rpc.login_user(data['username'],data['password'])
        response = {'status':res['status'],'message':res['message']}
        if(res['status'] == 'error'):
            return Response(str(response),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})
        else:
            session_id = self.session_provider.set_session(res['data'])
            re = Response(str(response),status=HTTPStatus.OK,headers={'Content-Type':'application/json'})
            re.set_cookie('SESSID', session_id)
            return re
        
    @http('POST','/user/logout')
    def logout(self,request):
        hasil = {'status':'Error','message':""} 
        cookies = request.cookies
        if cookies:
            hasil['message'] = "user logged out successfully"
            res = self.session_provider.delete_session(cookies['SESSID'])
            response = Response(str(hasil),status=HTTPStatus.CREATED,headers={'Content-Type':'application/json'})
            response.delete_cookie('SESSID')
        else:
            response = Response(str(hasil),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})
        return response

    @http('GET','/user/<id_user>')
    def fetch_user(self,request,id_user):
        http_response = {
                            'message':'',
                            'data':''
                        }
        rpc_response = json.loads(self.user_rpc.fetch_user(id_user))
        http_response['message'] = rpc_response['message']
        http_response['data'] = rpc_response['data']

        return Response(json.dumps(http_response),status=rpc_response['status'],headers={'Content-Type':'application/json'})

    @http('POST','/file/upload')
    def upload_file(self,request):
        http_response = {
                'message':''
            }

        cookies = request.cookies
        if cookies.get('SESSID') is None:
            http_response['message'] = "You need to login to use this service"
            return Response(json.dumps(http_response),status=HTTPStatus.FORBIDDEN,headers={'Content-Type':'application/json'})
        
        user_data = self.session_provider.get_session(cookies['SESSID'])

        if request.files.get('file') is not None and user_data['id'] is not None:        
            file = request.files.get('file')
            user_id = user_data['id']
            decodedFile = base64.b64encode((file.read()))
            
            raw_data = { 
                'user_id': user_id,
                'base64Content':decodedFile.decode('ascii'),
                'mimetype':file.mimetype,
                'filename':file.filename
            }
            rpc_response = json.loads(self.storage_rpc.upload_file(json.dumps(raw_data)))

            http_response['message'] = rpc_response['message']
            return Response(json.dumps(http_response),status=rpc_response['status'],headers={'Content-Type':'application/json'})
        else:
            http_response['message'] = "Error, file and user_id cannot be empty"
            return Response(json.dumps(http_response),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})

    @http('GET','/file/download/<id_file>')
    def download_file(self,request,id_file):
        http_response = {
                'message':''
            }
        cookies = request.cookies
        if cookies.get('SESSID') is None:
            http_response['message'] = "You need to login to use this service"
            return Response(json.dumps(http_response),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})
        
        user_data = self.session_provider.get_session(cookies['SESSID'])

        raw_data = {
            'user_id':str(user_data['user_id']),
            'file_id':str(id_file)
        }
        rpc_response = json.loads(self.storage_rpc.download_file(json.dumps(raw_data)))
        if rpc_response['status'] == 200:
            return Response(base64.b64decode(rpc_response['data']['base64Content']),status=HTTPStatus.OK,headers={'Content-Type':rpc_response['data']['mime_type']})
        else:
            return Response(json.dumps(rpc_response),status=rpc_response['status'],headers={'Content-Type':'application/json'})

    @http('GET','/file/<id_file>/access')
    def fetch_file_access(self,request,id_file):
        http_response = {
                'message':'',
                'data':''
            }
        rpc_response = json.loads(self.storage_rpc.fetch_file_access(id_file))

        http_response['message'] = rpc_response['message']
        http_response['data'] = rpc_response['data']
        return Response(json.dumps(http_response),status=rpc_response['status'],headers={'Content-Type':'application/json'})

    @http('PUT','/file/<id_file>/share/<id_share_to>')
    def sharing_file(self,request,id_file,id_share_to):
        http_response = {
                'message':''
            }
        cookies = request.cookies
        if cookies.get('SESSID') is None:
            http_response['message'] = "You need to login to use this service"
            return Response(json.dumps(http_response),status=HTTPStatus.BAD_REQUEST,headers={'Content-Type':'application/json'})
        
        user_data = self.session_provider.get_session(cookies['SESSID'])

        raw_data = {
            'user_id':str(user_data['user_id']),
            'file_id':str(id_file),
            'share_to':str(id_share_to)
        }
        rpc_response = json.loads(self.storage_rpc.sharing_file(json.dumps(raw_data))) 
        return Response(json.dumps(rpc_response),status=rpc_response['status'],headers={'Content-Type':'application/json'})


        