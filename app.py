import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import urllib3
import json
from urllib.parse import urlencode
import certifi

class Pelicula:
    def __init__(self, id, titulo, genero, precio, stock, poster_url=None):
        self.id = id
        self.titulo = titulo
        self.genero = genero
        self.precio = precio
        self.stock = stock
        self.poster_url = poster_url

class Venta:
    def __init__(self, id_venta, pelicula, cantidad, fecha=None):
        self.id_venta = id_venta
        self.pelicula = pelicula
        self.cantidad = cantidad
        self.fecha = fecha if fecha else datetime.now()
        self.total = pelicula.precio * cantidad

class SistemaPeliculas:
    def __init__(self):
        self.peliculas = []
        self.ventas = []
        self.siguiente_id_venta = 1
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.api_key = "b87c6c9f"
        self.base_url = "http://www.omdbapi.com/"

    def obtener_peliculas_populares(self):
        print("Iniciando búsqueda de películas...")  # Debug
        # Buscar películas por año (últimos años)
        años = range(2020, 2024)  # Películas de 2020 a 2023
        
        for año in años:
            print(f"Buscando películas del año {año}")  # Debug
            campos = {
                "apikey": self.api_key,
                "s": "movie",  # Cambiado de "*" a "movie" para mejor búsqueda
                "type": "movie",
                "y": str(año)
            }
            
            try:
                response = self.http.request(
                    'GET',
                    f"{self.base_url}?{urlencode(campos)}"
                )
                
                if response.status == 200:
                    resultados = json.loads(response.data.decode('utf-8'))
                    print(f"Respuesta de la API para {año}:", resultados)  # Debug
                    
                    if resultados.get("Response") == "True":
                        peliculas_encontradas = resultados.get("Search", [])
                        print(f"Encontradas {len(peliculas_encontradas)} películas para {año}")  # Debug
                        
                        # Limitar a 5 películas por año para evitar exceder límites de API
                        for pelicula_basica in peliculas_encontradas[:5]:
                            campos_detalle = {
                                "apikey": self.api_key,
                                "i": pelicula_basica["imdbID"]
                            }
                            
                            response_detalle = self.http.request(
                                'GET',
                                f"{self.base_url}?{urlencode(campos_detalle)}"
                            )
                            
                            if response_detalle.status == 200:
                                pelicula = json.loads(response_detalle.data.decode('utf-8'))
                                if pelicula.get("Response") == "True":
                                    try:
                                        rating = float(pelicula.get("imdbRating", "0"))
                                        precio = 9.99 + (rating * 0.5)
                                    except:
                                        precio = 14.99
                                    
                                    # Agregar película y confirmar
                                    nueva_pelicula = self.agregar_pelicula(
                                        pelicula["Title"],
                                        pelicula.get("Genre", "No especificado"),
                                        precio,
                                        10,  # stock inicial
                                        pelicula.get("Poster", "")
                                    )
                                    print(f"Película agregada: {nueva_pelicula.titulo}")  # Debug
                    else:
                        print(f"No se encontraron resultados para el año {año}")  # Debug
                    
            except Exception as e:
                print(f"Error al obtener películas del año {año}: {str(e)}")  # Debug

    def obtener_generos(self, genre_ids):
        url = f"{self.base_url}/genre/movie/list"
        campos = {
            "api_key": self.api_key,
            "language": "es-ES"
        }
        
        try:
            response = self.http.request(
                'GET',
                f"{url}?{urlencode(campos)}"
            )
            
            if response.status == 200:
                datos = json.loads(response.data.decode('utf-8'))
                generos = datos["genres"]
                nombres_generos = []
                for genre_id in genre_ids:
                    for genero in generos:
                        if genero["id"] == genre_id:
                            nombres_generos.append(genero["name"])
                return ", ".join(nombres_generos)
            return "Género desconocido"
        except:
            return "Género desconocido"

    def agregar_pelicula(self, titulo, genero, precio, stock, poster_url=None):
        id_pelicula = len(self.peliculas) + 1
        pelicula = Pelicula(id_pelicula, titulo, genero, precio, stock, poster_url)
        self.peliculas.append(pelicula)
        return pelicula

    def realizar_venta(self, id_pelicula, cantidad):
        pelicula = next((p for p in self.peliculas if p.id == id_pelicula), None)
        if not pelicula:
            return "Película no encontrada"
        if pelicula.stock < cantidad:
            return "Stock insuficiente"
        
        pelicula.stock -= cantidad
        venta = Venta(self.siguiente_id_venta, pelicula, cantidad)
        self.ventas.append(venta)
        self.siguiente_id_venta += 1
        return venta

    def listar_peliculas(self):
        return self.peliculas

    def listar_ventas(self):
        return self.ventas

    def probar_api_key(self):
        try:
            campos = {
                "apikey": self.api_key,
                "s": "Star Wars",
                "type": "movie"
            }
            
            print(f"Probando API con URL: {self.base_url}?{urlencode(campos)}")  # Debug
            
            response = self.http.request(
                'GET',
                f"{self.base_url}?{urlencode(campos)}"
            )
            
            print(f"Código de respuesta: {response.status}")  # Debug
            
            if response.status == 200:
                resultados = json.loads(response.data.decode('utf-8'))
                print(f"Respuesta de la API: {resultados}")  # Debug
                if resultados.get("Response") == "True":
                    return True, "API key válida"
                else:
                    return False, resultados.get("Error", "Error desconocido")
            elif response.status == 401:
                return False, "API key no válida o no activada. Por favor, verifica tu email de confirmación."
            else:
                return False, f"Error de HTTP: {response.status}"
        except Exception as e:
            return False, f"Error al probar API key: {str(e)}"

class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ventas de Películas")
        self.root.geometry("1200x700")
        self.sistema = SistemaPeliculas()
        self.carrito = []

        # Inicializar la interfaz antes de cargar las películas
        self.inicializar_interfaz()
        self.inicializar_peliculas()

    def inicializar_interfaz(self):
        # Configurar estilo
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.configure("TButton", padding=5, font=('Arial', 10))  # Reducido el padding
        style.configure("TLabel", font=('Arial', 11))
        style.configure("TLabelframe", font=('Arial', 11, 'bold'))
        
        # Frame principal con dos columnas
        self.frame_principal = ttk.Frame(self.root, padding="10")  # Reducido el padding
        self.frame_principal.pack(fill=tk.BOTH, expand=True)  # Cambiado a pack para mejor distribución
        
        # Crear frames para las columnas
        self.frame_izquierdo = ttk.Frame(self.frame_principal)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.frame_derecho = ttk.Frame(self.frame_principal)
        self.frame_derecho.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Lista de películas
        self.frame_peliculas = ttk.LabelFrame(self.frame_izquierdo, text="Películas Disponibles")
        self.frame_peliculas.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para películas con scrollbar
        self.tree_peliculas = ttk.Treeview(self.frame_peliculas, columns=('ID', 'Título', 'Género', 'Precio', 'Stock'), height=15)
        self.scrollbar_peliculas = ttk.Scrollbar(self.frame_peliculas, orient="vertical", command=self.tree_peliculas.yview)
        self.tree_peliculas.configure(yscrollcommand=self.scrollbar_peliculas.set)
        
        # Configurar columnas de películas
        self.tree_peliculas.column('#0', width=0, stretch=tk.NO)  # Ocultar primera columna
        self.tree_peliculas.column('ID', width=50, anchor=tk.CENTER)
        self.tree_peliculas.column('Título', width=200)
        self.tree_peliculas.column('Género', width=100)
        self.tree_peliculas.column('Precio', width=70, anchor=tk.CENTER)
        self.tree_peliculas.column('Stock', width=50, anchor=tk.CENTER)
        
        # Configurar encabezados
        self.tree_peliculas.heading('ID', text='ID')
        self.tree_peliculas.heading('Título', text='Título')
        self.tree_peliculas.heading('Género', text='Género')
        self.tree_peliculas.heading('Precio', text='Precio')
        self.tree_peliculas.heading('Stock', text='Stock')
        
        # Empaquetar Treeview y scrollbar
        self.tree_peliculas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_peliculas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón de agregar al carrito
        ttk.Button(self.frame_izquierdo, text="Agregar al Carrito", command=self.agregar_al_carrito).pack(pady=5)
        
        # Botón para agregar película
        ttk.Button(self.frame_izquierdo, text="Agregar Película", command=self.agregar_pelicula).pack(pady=5)
        
        # Frame del carrito
        self.frame_carrito = ttk.LabelFrame(self.frame_derecho, text="Carrito de Compras")
        self.frame_carrito.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para carrito
        self.tree_carrito = ttk.Treeview(self.frame_carrito, columns=('ID', 'Título', 'Cantidad', 'Precio Unit.', 'Subtotal'), height=10)
        self.scrollbar_carrito = ttk.Scrollbar(self.frame_carrito, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=self.scrollbar_carrito.set)
        
        # Configurar columnas del carrito
        self.tree_carrito.column('#0', width=0, stretch=tk.NO)
        self.tree_carrito.column('ID', width=50, anchor=tk.CENTER)
        self.tree_carrito.column('Título', width=200)
        self.tree_carrito.column('Cantidad', width=70, anchor=tk.CENTER)
        self.tree_carrito.column('Precio Unit.', width=70, anchor=tk.CENTER)
        self.tree_carrito.column('Subtotal', width=80, anchor=tk.CENTER)
        
        # Configurar encabezados del carrito
        self.tree_carrito.heading('ID', text='ID')
        self.tree_carrito.heading('Título', text='Título')
        self.tree_carrito.heading('Cantidad', text='Cantidad')
        self.tree_carrito.heading('Precio Unit.', text='Precio')
        self.tree_carrito.heading('Subtotal', text='Subtotal')
        
        # Empaquetar Treeview y scrollbar del carrito
        self.tree_carrito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_carrito.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para controles del carrito
        self.frame_controles = ttk.Frame(self.frame_derecho)
        self.frame_controles.pack(fill=tk.X, pady=5)
        
        # Total
        self.label_total = ttk.Label(self.frame_controles, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.label_total.pack(side=tk.LEFT, padx=5)
        
        # Botones del carrito
        ttk.Button(self.frame_controles, text="Eliminar del Carrito", command=self.eliminar_del_carrito).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.frame_controles, text="Generar Factura", command=self.generar_factura).pack(side=tk.LEFT, padx=5)
        
        self.actualizar_lista_peliculas()

    def inicializar_peliculas(self):
        try:
            print("Iniciando carga de películas...")  # Debug
            
            # Probar la API key primero
            exito, mensaje = self.sistema.probar_api_key()
            if not exito:
                print("No se pudo conectar a la API, cargando datos predeterminados.")  # Debug
                self.cargar_datos_predeterminados()  # Cargar datos predeterminados
                return
            
            # Continuar con la carga de películas
            self.sistema.obtener_peliculas_populares()
            cantidad_peliculas = len(self.sistema.peliculas)
            print(f"Total de películas cargadas: {cantidad_peliculas}")  # Debug
            
            if cantidad_peliculas == 0:
                messagebox.showwarning(
                    "Advertencia", 
                    "No se pudieron cargar películas desde la API.\n"
                    "Verifique su conexión a internet y la API key."
                )
            
            self.actualizar_lista_peliculas()
        except Exception as e:
            print(f"Error en inicializar_peliculas: {str(e)}")  # Debug
            messagebox.showerror("Error", f"Error al cargar las películas: {str(e)}")

    def cargar_datos_predeterminados(self):
        # Cargar películas predeterminadas
        peliculas_predeterminadas = [
            Pelicula(1, "Inception", "Ciencia Ficción", 9.99, 10),
            Pelicula(2, "The Godfather", "Drama", 8.99, 5),
            Pelicula(3, "The Dark Knight", "Acción", 7.99, 8),
            Pelicula(4, "Pulp Fiction", "Drama", 10.99, 12),
            Pelicula(5, "Forrest Gump", "Drama", 6.99, 15),
            Pelicula(6, "The Matrix", "Ciencia Ficción", 8.49, 7),
            Pelicula(7, "Titanic", "Romance", 9.49, 3),
            Pelicula(8, "Jurassic Park", "Aventura", 11.99, 4),
            Pelicula(9, "The Shawshank Redemption", "Drama", 7.49, 9),
            Pelicula(10, "Avatar", "Ciencia Ficción", 12.99, 6),
        ]
        self.sistema.peliculas.extend(peliculas_predeterminadas)
        self.actualizar_lista_peliculas()

    def actualizar_lista_peliculas(self):
        for item in self.tree_peliculas.get_children():
            self.tree_peliculas.delete(item)
        
        for pelicula in self.sistema.listar_peliculas():
            self.tree_peliculas.insert('', 'end', values=(
                pelicula.id,
                pelicula.titulo,
                pelicula.genero,
                f"${pelicula.precio:.2f}",
                pelicula.stock
            ))

    def agregar_al_carrito(self):
        seleccion = self.tree_peliculas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una película")
            return
            
        cantidad = self.pedir_cantidad()
        if not cantidad:
            return
            
        item = self.tree_peliculas.item(seleccion[0])
        valores = item['values']
        
        # Verificar stock
        if cantidad > valores[4]:  # valores[4] es el stock
            messagebox.showerror("Error", "Stock insuficiente")
            return
            
        subtotal = cantidad * float(valores[3].replace('$', ''))
        
        self.tree_carrito.insert('', 'end', values=(
            valores[0],  # ID
            valores[1],  # Título
            cantidad,
            valores[3],  # Precio unitario
            f"${subtotal:.2f}"
        ))
        
        self.actualizar_total()

    def eliminar_del_carrito(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un item del carrito")
            return
            
        self.tree_carrito.delete(seleccion[0])
        self.actualizar_total()

    def pedir_cantidad(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Cantidad")
        dialog.geometry("300x200")  # Aumentar la altura de la ventana
        dialog.transient(self.root)
        dialog.grab_set()  # Hace la ventana modal
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        cantidad = tk.StringVar()
        ttk.Label(frame, text="Ingrese la cantidad:", font=('Arial', 11)).pack(pady=5)
        entry = ttk.Entry(frame, textvariable=cantidad, font=('Arial', 11))
        entry.pack(pady=10)
        entry.focus()
        
        def aceptar():
            dialog.destroy()
        
        ttk.Button(frame, text="Aceptar", command=aceptar, style="Accent.TButton").pack(pady=10)
        
        dialog.wait_window()
        try:
            return int(cantidad.get())
        except:
            return None

    def actualizar_total(self):
        total = 0
        for item in self.tree_carrito.get_children():
            valores = self.tree_carrito.item(item)['values']
            total += float(valores[4].replace('$', ''))
        
        self.label_total.config(text=f"Total: ${total:.2f}")

    def generar_factura(self):
        if not self.tree_carrito.get_children():
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
            
        # Procesar la venta
        for item in self.tree_carrito.get_children():
            valores = self.tree_carrito.item(item)['values']
            id_pelicula = valores[0]
            cantidad = valores[2]
            venta = self.sistema.realizar_venta(id_pelicula, cantidad)
            
        # Mostrar factura
        factura = tk.Toplevel(self.root)
        factura.title("Factura")
        factura.geometry("400x500")
        
        texto_factura = tk.Text(factura, height=25, width=45)
        texto_factura.pack(padx=10, pady=10)
        
    
        # Encabezado de la factura
        texto_factura.insert('end', "FACTURA DE VENTA\n")
        texto_factura.insert('end', f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        texto_factura.insert('end', "-" * 40 + "\n\n")
        
        # Detalles de la compra
        for item in self.tree_carrito.get_children():
            valores = self.tree_carrito.item(item)['values']
            texto_factura.insert('end', f"Película: {valores[1]}\n")
            texto_factura.insert('end', f"Cantidad: {valores[2]}\n")
            texto_factura.insert('end', f"Precio unitario: {valores[3]}\n")
            texto_factura.insert('end', f"Subtotal: {valores[4]}\n")
            texto_factura.insert('end', "-" * 40 + "\n")
            
        texto_factura.insert('end', f"\nTotal: {self.label_total.cget('text')}")
        texto_factura.config(state='disabled')
        
        # Limpiar carrito después de la venta
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        self.actualizar_total()
        self.actualizar_lista_peliculas()

    def agregar_pelicula(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Película")
        dialog.geometry("300x400")  # Aumentar la altura de la ventana

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Variables para los campos de entrada
        titulo = tk.StringVar()
        genero = tk.StringVar()
        precio = tk.DoubleVar()
        stock = tk.IntVar()

        # Etiquetas y campos de entrada
        ttk.Label(frame, text="Título:", font=('Arial', 11)).pack(pady=5)
        ttk.Entry(frame, textvariable=titulo, font=('Arial', 11)).pack(pady=5)

        ttk.Label(frame, text="Género:", font=('Arial', 11)).pack(pady=5)
        ttk.Entry(frame, textvariable=genero, font=('Arial', 11)).pack(pady=5)

        ttk.Label(frame, text="Precio:", font=('Arial', 11)).pack(pady=5)
        ttk.Entry(frame, textvariable=precio, font=('Arial', 11)).pack(pady=5)

        ttk.Label(frame, text="Stock:", font=('Arial', 11)).pack(pady=5)
        ttk.Entry(frame, textvariable=stock, font=('Arial', 11)).pack(pady=5)

        # Botón para agregar la película
        ttk.Button(frame, text="Agregar", command=lambda: self.aceptar_agregar_pelicula(dialog, titulo, genero, precio, stock)).pack(pady=20)

        dialog.wait_window()

    def aceptar_agregar_pelicula(self, dialog, titulo, genero, precio, stock):
        # Validar y agregar la película
        if titulo.get() and genero.get() and precio.get() >= 0 and stock.get() >= 0:
            nueva_pelicula = self.sistema.agregar_pelicula(
                titulo.get(),
                genero.get(),
                precio.get(),
                stock.get()
            )
            messagebox.showinfo("Éxito", f"Película '{nueva_pelicula.titulo}' agregada exitosamente.")
            dialog.destroy()
            self.actualizar_lista_peliculas()  # Actualizar la lista de películas
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()
