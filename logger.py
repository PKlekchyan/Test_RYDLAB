import time


class Logger(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
        return cls.instance

    def log_error(self, class_name, method_name, error_message):
        string = ' | '.join([str(time.asctime()), "ERROR", str(class_name), str(method_name), str(error_message)])
        with open("log.txt", "a", encoding='utf-8') as file:
            file.write(string + "\n")

    def log_success(self, model, name, id_sw, id_odoo):
        string = ' | '.join([str(time.asctime()), "SUCCESS", str(model), str(name), "ID_SW - "+str(id_sw), "ID_Odoo - "+str(id_odoo)])
        with open("log.txt", "a", encoding='utf-8') as file:
            file.write(string + "\n")
