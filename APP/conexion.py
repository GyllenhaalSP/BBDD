"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import configparser
import sys
import oracledb


class Conexion:
    def __init__(self):
        oracledb.init_oracle_client()
        self.config = read_db_config("db_connection_config.ini", 'default')
        try:
            self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']), self.config['service-name'])
            self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
            self.cur = self.conn.cursor()
        except oracledb.DatabaseError:
            self.config = read_db_config("db_connection_config.ini", 'try1')
            try:
                self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']), self.config['service-name'])
                self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
                self.cur = self.conn.cursor()
            except oracledb.DatabaseError:
                self.config = read_db_config("db_connection_config.ini", 'try2')
                try:
                    self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']),
                                                self.config['service-name'])
                    self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
                    self.cur = self.conn.cursor()
                except oracledb.DatabaseError:
                    sys.exit("Imposible conectar a la BB.DD.")

    def desconectar(self):
        self.conn.close()

    def query_fetchall(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()


def read_db_config(config_file, section='default'):
    parser = configparser.ConfigParser()
    parser.read(config_file)

    db_config = {}

    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_config[item[0]] = item[1]
    else:
        raise Exception(f'Section {section} not found in the {config_file} file')

    return db_config



