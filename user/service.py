from nameko.rpc import rpc
import databasewrapper

class UserService:
    name = 'user_service'
    database = databasewrapper.Database()

    @rpc
    def add_user(self, username, password):
        res = self.database.add_user(username,password)
        return res

    @rpc
    def login_user(self, username, password):
        res = self.database.login_user(username, password)
        return res

    @rpc
    def fetch_user(self,user_id):
        database_response = self.database.fetch_user(user_id)
        return database_response