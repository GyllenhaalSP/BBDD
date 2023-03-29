"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import configparser
import os
import sys
from tkinter import messagebox

import oracledb


class Conexion:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        oracledb.init_oracle_client()
        self.config = read_db_config(os.path.join(application_path, 'db_connection_config.ini'), 'default')
        try:
            show_message("Conectando a la BB.DD...", 'info', 1500)
            self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']), self.config['service-name'])
            self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
            self.cur = self.conn.cursor()
        except oracledb.DatabaseError:
            show_message("Imposible conectar a la BB.DD.\nReintentando en 20 segundos...", 'error', 2000)
            self.config = read_db_config("db_connection_config.ini", 'try1')
            try:
                self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']), self.config['service-name'])
                self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
                self.cur = self.conn.cursor()
            except oracledb.DatabaseError:
                show_message("Imposible conectar a la BB.DD.\nReintentando en 20 segundos...", 'error', 2000)
                self.config = read_db_config("db_connection_config.ini", 'try2')
                try:
                    self.dsn = oracledb.makedsn(self.config['ip'], int(self.config['port']),
                                                self.config['service-name'])
                    self.conn = oracledb.connect(self.config['user-login'] + self.dsn)
                    self.cur = self.conn.cursor()
                except oracledb.DatabaseError:
                    show_message("Imposible conectar a la BB.DD.", 'error', 3000)
                    sys.exit()

    def desconectar(self):
        self.conn.close()

    def query_fetchall(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()


def show_message(message, msg_type='info', timeout=2500):
    import tkinter as tk
    from tkinter import messagebox as msgb

    root = tk.Tk()
    root.withdraw()
    try:
        root.after(timeout, root.destroy)
        if msg_type == 'info':
            msgb.showinfo('Info', message, master=root)
        elif msg_type == 'warning':
            msgb.showwarning('Warning', message, master=root)
        elif msg_type == 'error':
            msgb.showerror('Error', message, master=root)
    except:
        pass


def read_db_config(config_file, section='default'):
    parser = configparser.ConfigParser()
    parser.read(config_file)

    db_config = {}

    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_config[item[0]] = item[1]
    else:
        messagebox.showerror('Error fatal', f'La sección "{section}" no se ha encontrado en el archivo {config_file}'
                                            f'.\nCompruebe que el archivo existe en el directorio raíz y que está '
                                            f'correctamente formado.')
        raise Exception(f'Section {section} not found in the {config_file} file')

    return db_config
