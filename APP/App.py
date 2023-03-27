"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import os
import re
import tempfile
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from tabulate import tabulate

from mailer import Mailer
from conexion import *
from queries import (
    query_cliente,
    query_dir,
    query_productos,
    query_factura,
    query_lista_productos,
)


def abrir_archivo(archivo, texto):
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=tempfile.gettempdir()) as temp_file:
        temp_file.write(archivo.encode())
        temp_file.flush()
        escribir_archivo(temp_file, texto)


def conectar():
    try:
        conn = Conexion()
        return conn
    except oracledb.DatabaseError:
        mostrar_popup_bb_dd()
        return


def configurar_ventana(ventana, texto, ancho, alto, x, y):
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    button = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
    button.grid(row=1, column=0, sticky="s")
    ventana.bind("<Return>", lambda event=None: button.invoke())
    texto.config(state='disabled')
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(0, weight=1)


def copiar_al_portapapeles(texto):
    texto.clipboard_clear()
    texto.clipboard_append(texto.selection_get())


def ejecutar_consulta(conn, consulta, param=None):
    if param:
        conn.cur.execute(consulta, param)
    else:
        conn.cur.execute(consulta)
    return conn.cur.fetchall()


def escribir_archivo(temp_file, texto):
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        for linea in f:
            texto.insert(tk.END, linea)


def generar_archivo(archivo, results, headers, colalign=None):
    return archivo + "\n" + tabulate(results, headers=headers, colalign=colalign) + "\n"


def mostrar_popup_error(tipo):
    if tipo in "factura":
        messagebox.showerror("Error", f"No se ha encontrado ninguna {tipo} con ese número.")
    else:
        messagebox.showerror("Error", f"No se ha encontrado ningún {tipo} con ese número.")


def mostrar_popup_bb_dd():
    messagebox.showerror("Error", "No se ha podido conectar con la base de datos.")


def validar_mail(dir_email):
    # Expresión regular para comprobar la dirección de correo electrónico
    patron = r'^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'

    # Comprobar si la dirección de correo electrónico es válida
    if re.match(patron, dir_email):
        return True
    else:
        messagebox.showerror("Error", "La dirección de correo electrónico no es válida.")
        return False


class App:
    def __init__(self, app_root):
        self.menu = None
        self.root = app_root
        self.root.configure(borderwidth=0, highlightthickness=0)
        app_root.title("Gestor de pedidos, albaranes y facturas")
        app_root.geometry("400x200+100+50")
        app_root.resizable(False, False)

        self.configure_root_grid()
        self.crear_widgets()

    def configure_root_grid(self):
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)

    def crear_widgets(self):
        label = ttk.Label(
            self.root, text="¿A qué deseas acceder?", font=("Arial Bold", 25)
        )
        label.grid(column=0, row=0, columnspan=4)

        self.crear_botonera()

    def crear_botonera(self):
        botones = [
            ("Lista de productos", self.lista_productos),
            ("Pedidos", self.pedidos),
            ("Albaranes", self.albaranes),
            ("Facturas", self.facturas),
        ]

        for i, (texto, comando) in enumerate(botones):
            boton = ttk.Button(self.root, text=texto, command=comando)
            boton.grid(column=i, row=2, sticky="nsew")

        correo = ttk.Button(self.root, text="Enviar factura por correo electrónico", command=self.enviar_factura)
        correo.grid(column=0, row=4, columnspan=4, sticky="nsew")

        cerrar = ttk.Button(self.root, text="Cerrar", command=self.root.destroy)
        cerrar.grid(column=0, row=5, columnspan=4, sticky="nsew")

    def get_mail(self, texto, n_fact, filename):
        mail = self.pedir_mail()
        if mail:
            from generador_pdf import PDFGenerator
            pdf = PDFGenerator(texto, filename=filename, title=f"Factura {n_fact} para {mail}")
            pdf.generar_pdf()
            from configparser import ConfigParser
            config = ConfigParser()
            config.read(os.path.join(application_path, 'db_connection_config.ini'))
            send_mail = Mailer('facturasalimentacionchen@gmail.com', config['pass']['password'])
            send_mail.enviar_email(mail, texto, n_fact, filename)
            pdf.eliminar_pdf()
            messagebox.showinfo("Información", "Correo enviado correctamente.")
        else:
            messagebox.showinfo("Información", "No se ha enviado ningún correo.")

    def enviar_factura(self):
        self.facturas(True)

    def crear_ventana(self, titulo):
        ventana = tk.Toplevel(self.root)
        ventana.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
        ventana.title(titulo)
        ventana.resizable(False, False)
        texto = tk.Text(ventana)
        texto.grid(row=0, column=0, sticky="nsew")
        ventana.focus()
        return ventana, texto

    def configurar_menu_contextual(self, ventana, texto):
        self.menu = tk.Menu(ventana, tearoff=0)
        self.menu.add_command(label="Copiar", command=lambda: copiar_al_portapapeles(texto))
        texto.bind("<Button-3>", lambda event: self.menu.post(event.x_root, event.y_root))

    def lista_productos(self):
        conn = conectar()
        try:
            conn.cur.execute(query_lista_productos())
            results = conn.cur.fetchall()
            columnas = ['CÓDIGO', 'PRODUCTO', 'IVA', 'PRECIO']

            ventana, texto = self.crear_ventana("Lista de productos")
            self.configurar_menu_contextual(ventana, texto)

            archivo = tabulate(results, headers=columnas) + "\n\n"

            abrir_archivo(archivo, texto)

            configurar_ventana(ventana, texto, 400, 650, 600, 25)
        except oracledb.DatabaseError:
            mostrar_popup_bb_dd()
        finally:
            conn.desconectar()

    def pedidos(self):
        conn = conectar()
        num_pedido = self.pedir_input("Pedido", "P")
        ventana, texto = self.crear_ventana("Pedido")
        self.configurar_menu_contextual(ventana, texto)
        try:
            consulta = f"""SELECT N_PED, TO_CHAR(FECHA_PED, 'dd/mm/yyyy') 
                FROM CAB_PED
                WHERE UPPER(N_PED) LIKE UPPER('{num_pedido}')
                ORDER BY N_PED
                """
            results = ejecutar_consulta(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("pedido")
                return
            archivo = generar_archivo("", results, ['Nº PEDIDO', 'FECHA PEDIDO'])

            consulta = query_cliente(num_pedido, "CAB_PED", "P", "N_PED")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(num_pedido, "CAB_PED", "P", "N_PED")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'])

            consulta = query_productos(num_pedido, "CAB_PED", "L", "LIN_PED")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['PRODUCTO', 'CANTIDAD', 'PRECIO UNITARIO'])

            abrir_archivo(archivo, texto)

            configurar_ventana(ventana, texto, 500, 600, 600, 50)
        except IndexError:
            mostrar_popup_error("pedido")
            ventana.destroy()
        finally:
            conn.desconectar()

    def albaranes(self):
        conn = conectar()
        albaran = self.pedir_input("Albarán", "A")
        ventana, texto = self.crear_ventana("Albarán")
        self.configurar_menu_contextual(ventana, texto)
        try:
            consulta = f"""SELECT N_ALB, TO_CHAR(FECHA_ALB, 'dd/mm/yyyy') 
            FROM CAB_ALB
            WHERE UPPER(N_ALB) LIKE UPPER('{albaran}')
            ORDER BY N_ALB
            """
            results = ejecutar_consulta(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("albarán")
                return
            archivo = generar_archivo("", results, ['Nº ALBARÁN', 'FECHA ALBARÁN'])

            consulta = query_cliente(albaran, "CAB_ALB", "A", "N_ALB")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(albaran, "CAB_ALB", "A", "N_ALB")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'],
                                      colalign=("left", "center", "center", "center", "center"))

            consulta = query_productos(albaran, "CAB_ALB", "L", "LIN_ALB")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['PRODUCTO', 'CANTIDAD', 'PRECIO UNITARIO'],
                                      colalign=("left", "right", "right"))

            abrir_archivo(archivo, texto)

            configurar_ventana(ventana, texto, 500, 600, 600, 50)
        except IndexError:
            ventana.destroy()
            mostrar_popup_error("albarán")
        finally:
            conn.desconectar()

    def facturas(self, mail=False):
        conn = conectar()
        if mail:
            messagebox.showinfo("Facturas", "Introducir el número de factura y seguidamente el mail.")
        factura = self.pedir_input("Factura", "F")
        ventana, texto = self.crear_ventana("Factura")
        self.configurar_menu_contextual(ventana, texto)

        try:
            consulta = f"""SELECT CF.N_FACT, CA.N_ALB, TO_CHAR(FECHA_FACT, 'dd/mm/yyyy') 
            FROM CAB_FACT CF, CAB_ALB CA
            WHERE UPPER(CF.N_FACT) LIKE UPPER('{factura}')
            AND CF.N_FACT = CA.N_FACT
            ORDER BY CF.N_FACT
            """
            results = ejecutar_consulta(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("factura")
                return
            archivo = generar_archivo("", results, ['Nº FACTURA', 'Nº ALBARÁN', 'FECHA FACTURA'])

            consulta = query_cliente(factura, "CAB_FACT", "", "")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(factura, "CAB_FACT", "", "")
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'],
                                      colalign=("left", "center", "center", "center", "center"))

            consulta = query_factura(factura)
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results,
                                      ['PRODUCTO', 'PORCENTAJE DE IVA', 'CANTIDAD', 'PRECIO UNITARIO', 'PRECIO TOTAL',
                                       'PRECIO CON IVA'],
                                      colalign=("left", "right", "right", "right", "right"))

            consulta = f"""SELECT DISTINCT SUM(ROUND((P.PRECIO * LA.CANT), 2)) AS TOTAL,
                SUM(ROUND(((P.PRECIO * LA.CANT) * I.IVA), 2)) AS "TOTAL CON IVA"
                FROM IVA I, PRODUCTO P, LIN_ALB LA, CAB_ALB CA, CAB_FACT CF
                WHERE UPPER(CF.N_FACT) LIKE UPPER('{factura}')
                AND I.COD_IVA = P.COD_IVA
                AND P.COD_PROD = LA.COD_PROD
                AND CF.N_FACT = CA.N_FACT
                AND CA.N_ALB = LA.N_ALB            
                """
            results = ejecutar_consulta(conn, consulta)
            archivo = generar_archivo(archivo, results, ['TOTAL', 'TOTAL CON IVA'], colalign=("right", "right"))

            abrir_archivo(archivo, texto)

            configurar_ventana(ventana, texto, 800, 700, 550, 50)

            if mail:
                self.get_mail(archivo, factura, f"Factura {factura}.pdf")
                ventana.destroy()

        except IndexError:
            ventana.destroy()
            mostrar_popup_error("factura")
        finally:
            conn.desconectar()

    def pedir_input(self, tipo_busqueda, letra):
        # Función para obtener el número introducido en el entry
        def get_entry_data():
            num.set(entry_input.get())
            ventana_input.destroy()

        # Crear nueva ventana para ingresar el número de pedido
        ventana_input = tk.Toplevel(self.root)
        ventana_input.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
        ventana_input.title("Datos de la búsqueda")
        ventana_input.resizable(False, False)
        ventana_input.geometry(f"{300}x{60}+{100}+{50}")

        num = tk.StringVar()

        # Crear label y entry para el número de pedido
        label_input = ttk.Label(ventana_input, text=f"Introducir número de {tipo_busqueda} (XXX): ")
        label_input.grid(column=0, row=0, padx=5, pady=5)

        entry_input = tk.Entry(ventana_input,
                               width=len(f"Introducir número de {tipo_busqueda} (XXX): ") - 10)
        entry_input.grid(column=0, row=1)
        entry_input.focus()

        boton_buscar = ttk.Button(ventana_input, text="Buscar", command=get_entry_data)
        entry_input.bind("<Return>", lambda event: boton_buscar.invoke())
        boton_buscar.grid(column=1, row=1)

        ventana_input.wait_window()

        return f"{num.get()}-{letra}"

    def pedir_mail(self):
        # Función para obtener el mail introducido en el entry
        def get_entry_data():
            mail.set(entry_input.get())
            if validar_mail(mail.get()):
                messagebox.showinfo("Confirmación", "Pulsa aceptar para enviar el correo.")
                ventana_input.destroy()
            else:
                messagebox.showerror("Error", "La dirección de correo no es válida")
                ventana_input.destroy()

        # Crear nueva ventana para ingresar el número de pedido
        ventana_input = tk.Toplevel(self.root)
        ventana_input.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
        ventana_input.title("Introducir dirección de correo electrónico: ")
        ventana_input.resizable(False, False)
        ventana_input.geometry(f"{400}x{60}+{100}+{50}")

        mail = tk.StringVar()

        # Crear label y entry para el mail
        label_input = ttk.Label(ventana_input, text="Introducir dirección de correo electrónico: ")
        label_input.grid(column=0, row=0, padx=5, pady=5)

        entry_input = tk.Entry(ventana_input, width=35)
        entry_input.grid(column=0, row=1, padx=10)
        entry_input.focus()

        boton_buscar = ttk.Button(ventana_input, text="Enviar", command=get_entry_data)
        entry_input.bind("<Return>", lambda event: boton_buscar.invoke())
        boton_buscar.grid(column=1, row=1)

        boton_cancelar = ttk.Button(ventana_input, text="Cancelar", command=ventana_input.destroy)
        entry_input.bind("<Escape>", lambda event: boton_cancelar.invoke())
        boton_cancelar.grid(column=2, row=1)

        ventana_input.wait_window()

        return mail.get()


if __name__ == "__main__":
    root = tk.Tk()
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    elif __file__:
        application_path = os.path.dirname(__file__)
    root.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
    app = App(root)
    root.mainloop()
