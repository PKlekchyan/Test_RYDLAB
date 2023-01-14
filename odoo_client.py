import xmlrpc.client
from logger import Logger


class OdooClient:
    uid = None
    models = None

    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.__init_client()

    def __init_client(self):
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        except xmlrpc.client.Fault as ex:
            Logger().log_error(str(self.__class__.__name__), '__init_client', str(ex))
        except TypeError as ex:
            Logger().log_error(str(self.__class__.__name__), '__init_client', str(ex))
            return None

    def create_record(self, model, data):
        try:
            odoo_id = self.models.execute_kw(self.db, self.uid, self.password, model, 'create', data)
            return odoo_id
        except xmlrpc.client.Fault as ex:
            Logger().log_error(str(self.__class__.__name__), 'create_record', str(ex))
            return None
        except TypeError as ex:
            Logger().log_error(str(self.__class__.__name__), 'create_record', str(ex))
            return None