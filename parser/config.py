
class Config:

    ip_address = '71.82.19.242'
    mongo_username = 'admin'
    mongo_password = '***REMOVED***'
    mongo_port = '27017'

    @staticmethod
    def get_mongo_address():
        return 'mongodb://' + Config.mongo_username + ":" + Config.mongo_password + '@' + Config.ip_address + ":" + Config.mongo_port + "/"
