"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import re
import tempfile
import tkinter as tk
from tkinter import ttk

from tabulate import tabulate

from conexion import *
from mailer import Mailer
from queries import (
    query_cliente,
    query_dir,
    query_productos,
    query_factura,
    query_lista_productos,
)


def connect():
    try:
        conn = Conexion()
        return conn
    except oracledb.DatabaseError:
        mostrar_popup_bb_dd()
        return


def copy_to_clipboard(texto):
    texto.clipboard_clear()
    texto.clipboard_append(texto.selection_get())


def create_input_window(titulo, etiqueta, validation=None):
    def get_entry_data():
        valor.set(entry_input.get())
        if validation is None or validation(valor.get()):
            ventana_input.destroy()
            return None
        else:
            messagebox.showerror("Error", "La dirección de correo electrónico introducida no es válida.")
            pedir_mail()

    ventana_input = tk.Toplevel()
    ventana_input.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
    ventana_input.title(titulo)
    ventana_input.resizable(False, False)
    ventana_input.geometry(f"{400}x{60}+{100}+{290}")

    valor = tk.StringVar()

    label_input = ttk.Label(ventana_input, text=etiqueta)
    label_input.grid(column=0, row=0, padx=5, pady=5)

    entry_input = tk.Entry(ventana_input, width=35)
    entry_input.grid(column=0, row=1, padx=10)
    entry_input.focus()

    button_aceptar = ttk.Button(ventana_input, text="Aceptar", command=get_entry_data)
    entry_input.bind("<Return>", lambda event: button_aceptar.invoke())
    button_aceptar.grid(column=1, row=1)

    button_cancelar = ttk.Button(ventana_input, text="Cancelar", command=ventana_input.destroy)
    entry_input.bind("<Escape>", lambda event: button_cancelar.invoke())
    button_cancelar.grid(column=2, row=1)

    ventana_input.wait_window()

    return valor.get()


def execute_query(conn, consulta, param=None):
    if param:
        conn.cur.execute(consulta, param)
    else:
        conn.cur.execute(consulta)
    return conn.cur.fetchall()


def generate_file(archivo, results, headers, col_align=None):
    return archivo + "\n" + tabulate(results, headers=headers, colalign=col_align, ) + "\n"


def generate_mail(texto, n_fact, filename):
    mail = pedir_mail()
    if mail:
        from generador_pdf import PDFGenerator
        pdf = PDFGenerator(texto, filename=filename, title=f"Factura {n_fact} para", mail=f"{mail}")
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


def mostrar_popup_error(tipo):
    if tipo in "factura":
        messagebox.showerror("Error", f"No se ha encontrado ninguna {tipo} con ese número.")
    else:
        messagebox.showerror("Error", f"No se ha encontrado ningún {tipo} con ese número.")


def mostrar_popup_bb_dd():
    messagebox.showerror("Error", "No se ha podido conectar con la base de datos.")


def open_file(archivo, texto):
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=tempfile.gettempdir()) as temp_file:
        temp_file.write(archivo.encode())
        temp_file.flush()
        write_file(temp_file, texto)


def pedir_input(search_type, letra):
    # search_type: Pedido, Albarán, Factura
    titulo = "Datos de la búsqueda"
    etiqueta = f"Introducir número de {search_type} (XXX): "
    valor = create_input_window(titulo, etiqueta)

    if valor is None:
        return None

    return f"{valor}-{letra}"


def pedir_mail():
    titulo = "Introducción de datos"
    etiqueta = "Introducir dirección de correo electrónico: "
    validation = lambda valid_value: validar_mail(valid_value)
    valor = create_input_window(titulo, etiqueta, validation)

    if valor is None or valor == "":
        return None

    messagebox.showinfo("Confirmación", "Pulsa aceptar para enviar el correo.")

    return valor


def validar_mail(dir_email):
    # Expresión regular para comprobar la dirección de correo electrónico
    patron = r'^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'

    # Comprobar si la dirección de correo electrónico es válida
    if re.match(patron, dir_email):
        return True
    else:
        return False


def window_config(ventana, texto, ancho, alto, x, y, padding=False):
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    button = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
    button.grid(row=1, column=0, sticky="s")
    ventana.bind("<Return>", lambda event=None: button.invoke())
    texto.config(state='disabled')
    if padding:
        texto.config(padx=80, pady=20)
    else:
        texto.config(padx=20, pady=20)
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(0, weight=1)


def write_file(temp_file, texto):
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        for linea in f:
            texto.insert(tk.END, linea)


class App:
    def __init__(self, app_root):
        self.menu = None
        self.root = app_root
        self.root.configure(borderwidth=0, highlightthickness=0)
        app_root.title("Gestor de pedidos, albaranes y facturas")
        app_root.geometry("400x200+100+25")
        app_root.resizable(False, False)

        self.configure_root_grid()
        self.crear_widgets()
        self.crear_menu()

    def configurar_menu_contextual(self, ventana, texto):
        self.menu = tk.Menu(ventana, tearoff=0)
        self.menu.add_command(label="Copiar", command=lambda: copy_to_clipboard(texto))
        texto.bind("<Button-3>", lambda event: self.menu.post(event.x_root, event.y_root))

    def configure_root_grid(self):
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)

    def crear_botonera(self):
        botones = [
            ("Lista de productos", self.lista_productos),
            ("Pedidos", self.pedidos),
            ("Albaranes", self.albaranes),
            ("Facturas", self.facturas),
        ]

        for i, (texto, comando) in enumerate(botones):
            button = ttk.Button(self.root, text=texto, command=comando)
            button.grid(column=i, row=2, sticky="nsew")

        correo = ttk.Button(self.root, text="Enviar factura por correo electrónico", command=self.enviar_factura)
        correo.grid(column=0, row=4, columnspan=4, sticky="nsew")

        cerrar = ttk.Button(self.root, text="Cerrar", command=self.root.destroy)
        cerrar.grid(column=0, row=5, columnspan=4, sticky="nsew")

    def crear_menu(self):
        # Crear barra de menú
        menu_bar = tk.Menu(self.root)

        # Crear menú Archivo
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.root.destroy)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

        # Crear menú Ayuda
        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

        # Añadir barra de menú a la ventana principal
        self.root.config(menu=menu_bar)

    def crear_ventana(self, titulo):
        ventana = tk.Toplevel(self.root)
        ventana.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
        ventana.title(titulo)
        ventana.resizable(False, False)
        texto = tk.Text(ventana)
        texto.grid(row=0, column=0, sticky="nsew")
        ventana.focus()
        return ventana, texto

    def mostrar_acerca_de(self):
        from PIL import Image, ImageTk
        acerca_de = tk.Toplevel(self.root)
        acerca_de.title("Acerca de")
        acerca_de.geometry("450x330+520+50")
        acerca_de.resizable(False, False)
        acerca_de.focus()

        image = Image.open(os.path.join(application_path, 'chen_logo_trans.png'))
        image_resized = image.resize((60, 60), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image_resized)

        titulo = tk.Label(acerca_de, text="\nGESTOR DE PEDIDOS, ALBARANES Y FACTURAS", font=("Calibri", 16, "bold"))
        titulo.pack()

        logo = tk.Label(acerca_de, image=photo)
        logo.pack(fill="both", expand=True)

        logo.image = photo

        titulo2 = tk.Label(acerca_de, text="ALIMENTACIÓN CHEN", font=("Calibri", 20, "bold"))
        titulo2.pack()

        description = tk.Label(acerca_de, text="\nEsta es una aplicación para la gestión de la base de datos de la "
                                               "empresa <<Alimentación Chen>> dentro del proyecto final de la "
                                               "asignatura Bases de Datos. \n", wraplength=350)
        description.pack()

        autor = tk.Label(acerca_de, text="Daniel Alonso Lázaro @ https://github.com/GyllenhaalSP.")
        autor.pack()

        where = tk.Label(acerca_de, text="IES Juan de la Cierva - DAW1V - 2022/2023 - BB.DD.")
        where.pack()

        cerrar = ttk.Button(acerca_de, text="Cerrar", command=acerca_de.destroy)
        acerca_de.bind("<Return>", lambda event=None: cerrar.invoke())
        cerrar.pack(pady=10)

    def crear_widgets(self):
        label = ttk.Label(
            self.root, text="¿A qué deseas acceder?", font=("Arial Bold", 25)
        )
        label.grid(column=0, row=0, columnspan=4)

        self.crear_botonera()

    def enviar_factura(self):
        self.facturas(True)

    def lista_productos(self):
        conn = connect()
        try:
            conn.cur.execute(query_lista_productos())
            results = conn.cur.fetchall()
            columnas = ['CÓDIGO', 'PRODUCTO', 'IVA', 'PRECIO']

            ventana, texto = self.crear_ventana("Lista de productos")
            self.configurar_menu_contextual(ventana, texto)

            archivo = tabulate(results, headers=columnas)

            open_file(archivo, texto)

            window_config(ventana, texto, 500, 680, 510, 25, True)
        except oracledb.DatabaseError:
            mostrar_popup_bb_dd()
        finally:
            conn.desconectar()

    def pedidos(self):
        conn = connect()
        num_pedido = pedir_input("Pedido", "P")
        ventana, texto = self.crear_ventana("Pedido")
        self.configurar_menu_contextual(ventana, texto)
        try:
            consulta = f"""SELECT N_PED, TO_CHAR(FECHA_PED, 'dd/mm/yyyy') 
                FROM CAB_PED
                WHERE UPPER(N_PED) LIKE UPPER('{num_pedido}')
                ORDER BY N_PED
                """
            results = execute_query(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("pedido")
                return
            archivo = generate_file("", results, ['Nº PEDIDO', 'FECHA PEDIDO'])

            consulta = query_cliente(num_pedido, "CAB_PED", "P", "N_PED")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(num_pedido, "CAB_PED", "P", "N_PED")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'])

            consulta = query_productos(num_pedido, "CAB_PED", "L", "LIN_PED")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['PRODUCTO', 'CANTIDAD', 'PRECIO UNITARIO'])

            open_file(archivo, texto)

            window_config(ventana, texto, 500, 600, 510, 25)
        except IndexError:
            mostrar_popup_error("pedido")
            ventana.destroy()
        finally:
            conn.desconectar()

    def albaranes(self):
        conn = connect()
        alb = pedir_input("Albarán", "A")
        ventana, texto = self.crear_ventana("Albarán")
        self.configurar_menu_contextual(ventana, texto)
        try:
            consulta = f"""SELECT N_ALB, TO_CHAR(FECHA_ALB, 'dd/mm/yyyy') 
            FROM CAB_ALB
            WHERE UPPER(N_ALB) LIKE UPPER('{alb}')
            ORDER BY N_ALB
            """
            results = execute_query(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("albarán")
                return
            archivo = generate_file("", results, ['Nº ALBARÁN', 'FECHA ALBARÁN'])

            consulta = query_cliente(alb, "CAB_ALB", "A", "N_ALB")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(alb, "CAB_ALB", "A", "N_ALB")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'],
                                    col_align=("left", "center", "center", "center", "center"))

            consulta = query_productos(alb, "CAB_ALB", "L", "LIN_ALB")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['PRODUCTO', 'CANTIDAD', 'PRECIO UNITARIO'],
                                    col_align=("left", "right", "right"))

            open_file(archivo, texto)

            window_config(ventana, texto, 500, 600, 510, 25)
        except IndexError:
            ventana.destroy()
            mostrar_popup_error("albarán")
        finally:
            conn.desconectar()

    def facturas(self, mail=False):
        conn = connect()
        if mail:
            messagebox.showinfo("Facturas", "Introducir el número de factura y seguidamente el mail.")
        factura = pedir_input("Factura", "F")
        ventana, texto = self.crear_ventana("Factura")
        self.configurar_menu_contextual(ventana, texto)

        try:
            consulta = f"""SELECT DISTINCT CF.N_FACT, CA.N_ALB, TO_CHAR(FECHA_FACT, 'dd/mm/yyyy') 
            FROM CAB_FACT CF, CAB_ALB CA
            WHERE UPPER(CF.N_FACT) LIKE UPPER('{factura}')
            AND CF.N_FACT = CA.N_FACT
            ORDER BY CF.N_FACT
            """
            results = execute_query(conn, consulta)
            if not results:
                ventana.destroy()
                mostrar_popup_error("factura")
                return
            archivo = generate_file("", results, ['Nº FACTURA', 'Nº ALBARÁN', 'FECHA FACTURA'])

            consulta = query_cliente(factura, "CAB_FACT", "", "")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['NOMBRE CLIENTE'])

            consulta = query_dir(factura, "CAB_FACT", "", "")
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['DIRECCIÓN', 'Nº', 'CP', 'PROVINCIA', 'CCAA'],
                                    col_align=("left", "center", "center", "center", "center"))

            consulta = query_factura(factura)
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results,
                                    ['PRODUCTO', '% DE IVA', 'CANTIDAD', 'PRECIO UNITARIO', 'PRECIO TOTAL',
                                     'PRECIO CON IVA'],
                                    col_align=("left", "right", "right", "right", "right"))

            consulta = f"""SELECT DISTINCT SUM(ROUND((P.PRECIO * LA.CANT), 2)) AS TOTAL,
                SUM(ROUND(((P.PRECIO * LA.CANT) * I.IVA), 2)) AS "TOTAL CON IVA"
                FROM IVA I, PRODUCTO P, LIN_ALB LA, CAB_ALB CA, CAB_FACT CF
                WHERE UPPER(CF.N_FACT) LIKE UPPER('{factura}')
                AND I.COD_IVA = P.COD_IVA
                AND P.COD_PROD = LA.COD_PROD
                AND CF.N_FACT = CA.N_FACT
                AND CA.N_ALB = LA.N_ALB            
                """
            results = execute_query(conn, consulta)
            archivo = generate_file(archivo, results, ['TOTAL', 'TOTAL CON IVA'], col_align=("right", "right"))

            open_file(archivo, texto)

            window_config(ventana, texto, 800, 760, 510, 25)

            if mail:
                generate_mail(archivo, factura, f"Factura {factura}.pdf")
                ventana.destroy()

        except IndexError:
            ventana.destroy()
            mostrar_popup_error("factura")
        finally:
            conn.desconectar()


if __name__ == "__main__":
    root = tk.Tk()
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    elif __file__:
        application_path = os.path.dirname(__file__)
    root.iconbitmap(default=os.path.join(application_path, 'SQL.ico'))
    app = App(root)
    root.mainloop()
