import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class Pelicula:
    def __init__(self, id, titulo, genero, precio, stock):
        self.id = id
        self.titulo = titulo
        self.genero = genero
        self.precio = precio
        self.stock = stock

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

    def agregar_pelicula(self, titulo, genero, precio, stock):
        id_pelicula = len(self.peliculas) + 1
        pelicula = Pelicula(id_pelicula, titulo, genero, precio, stock)
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

class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ventas de Películas")
        self.root.geometry("1200x700")  # Ajustado el tamaño de la ventana
        self.sistema = SistemaPeliculas()
        self.carrito = []
        
        # Inicializar películas de ejemplo
        self.inicializar_peliculas()
        
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
        self.sistema.agregar_pelicula("El Padrino", "Drama", 15.99, 10)
        self.sistema.agregar_pelicula("Matrix", "Ciencia Ficción", 12.99, 15)
        self.sistema.agregar_pelicula("Titanic", "Romance", 14.99, 8)
        self.sistema.agregar_pelicula("El Señor de los Anillos", "Fantasía", 16.99, 12)
        self.sistema.agregar_pelicula("Jurassic Park", "Aventura", 13.99, 20)
        self.sistema.agregar_pelicula("El Rey León", "Animación", 11.99, 25)
        self.sistema.agregar_pelicula("Pulp Fiction", "Drama", 14.99, 10)
        self.sistema.agregar_pelicula("Avatar", "Ciencia Ficción", 17.99, 15)

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
        dialog.geometry("300x150")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()
