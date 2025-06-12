"""
Vista mejorada para gestión de muestras - CRUD completo con tabla simple
"""
import flet as ft
from datetime import datetime, date
from app.services.sample_service import SampleService
from app.services.client_service import ClientService
from app.services.mine_service import MineService
from app.services.warehouse_service import WarehouseService
from app.services.batch_service import BatchService

class SamplesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.samples = []
        self.filtered_samples = []
        self.selected_sample = None
        
        # Controles de filtro
        self.filter_code = ft.TextField(
            label="Filtrar por código",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.apply_filters,
            width=200
        )
        
        self.filter_status = ft.Dropdown(
            label="Filtrar por estado",
            width=150,
            on_change=self.apply_filters,
            options=[
                ft.dropdown.Option("", "Todos"),
                ft.dropdown.Option("EXTRAIDA", "Extraída"),
                ft.dropdown.Option("ANALIZADA", "Analizada"),
                ft.dropdown.Option("ALMACENADA", "Almacenada"),
                ft.dropdown.Option("DEVUELTA", "Devuelta")
            ]
        )

        # Controles principales
        self.btn_new = ft.ElevatedButton(
            "Nueva Muestra",
            icon=ft.Icons.ADD,
            on_click=self.handle_new_click,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
        
        self.btn_edit = ft.ElevatedButton(
            "Editar",
            icon=ft.Icons.EDIT,
            on_click=self.handle_edit_click,
            disabled=True,
            bgcolor=ft.Colors.ORANGE_600,
            color=ft.Colors.WHITE
        )
        
        self.btn_delete = ft.ElevatedButton(
            "Eliminar",
            icon=ft.Icons.DELETE,
            on_click=self.confirm_delete_sample,
            disabled=True,
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE
        )
        
        self.btn_refresh = ft.ElevatedButton(
            "Actualizar",
            icon=ft.Icons.REFRESH,
            on_click=self.refresh_data,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
        
        # Tabla de muestras
        self.samples_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción",color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha Extracción", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Lote", color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cliente", color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Bodega", color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            heading_row_color=ft.Colors.PURPLE,
            heading_row_height=40,
            data_row_max_height=40,
            show_checkbox_column=False,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_100),
        )
        
        # Contenedor scrollable para la tabla
        self.table_container = ft.Container(
            content=ft.Column([
                self.samples_table
            ], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=10,
            expand=True
        )
        
        # Contenedor de estadísticas
        self.stats_container = ft.Container(
            content=ft.Text("Cargando estadísticas...", size=12, color=ft.Colors.GREY_600),
            bgcolor=ft.Colors.PURPLE_50,
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.PURPLE)
        )
        
        # Cargar datos iniciales
        self.load_samples()
    
    def get_view(self):
        """Obtener la vista principal"""
        return ft.Container(
            content=ft.Column([
                # Encabezado con estadísticas
                ft.Container(
                    content=ft.Row([
                        # Título y icono
                        ft.Row([
                            ft.Icon(ft.Icons.SCIENCE, size=40, color=ft.Colors.BLUE_600),
                            ft.Text(
                                "Gestión Muestras de Mineral",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            )
                        ], spacing=10),
                        
                        # Estadísticas en la esquina superior derecha
                        self.stats_container
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Barra de herramientas
                ft.Container(
                    content=ft.Row([
                        # Filtros
                        self.filter_code,
                        self.filter_status,
                        ft.VerticalDivider(width=20),
                        # Botones
                        self.btn_new,
                        self.btn_edit,
                        self.btn_delete,
                        self.btn_refresh
                    ], wrap=True, spacing=10),
                    bgcolor=ft.Colors.GREY_50,
                    padding=15,
                    border_radius=10
                ),
                
                # Tabla de muestras
                self.table_container
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def update_stats(self):
        """Actualizar estadísticas del inventario (solo registros activos)"""
        try:
            # Obtener estadísticas del servicio (solo activos)
            stats = SampleService.get_active_sample_stats()
            
            # Crear texto de estadísticas - SIN mostrar inactivos
            stats_text = f"📊 Total Activos: {stats['total_active']} | ⛏️ Extraídos: {stats['extracted']} | 🧪 Analizados: {stats['tested']} | 📦 Almacenados: {stats['stored']} "
            
            # Actualizar contenedor
            self.stats_container.content = ft.Text(
                stats_text, 
                size=12, 
                color=ft.Colors.BLUE_800,
                #weight=ft.FontWeight.BOLD
            )
            
            print(f"📊 DEBUG: Estadísticas activos: {stats}")
            
        except Exception as e:
            print(f"❌ ERROR actualizando estadísticas: {e}")
            self.stats_container.content = ft.Text(
                "❌ Error cargando estadísticas", 
                size=12, 
                color=ft.Colors.RED_600
            )
    
    def load_samples(self):
        """Cargar todas las muestras activas (active_status = 1)"""
        try:
            # El servicio ya filtra por active_status = 1 automáticamente
            self.samples = SampleService.get_all_samples()
            
            print(f"INFO:app.ui.samples_view:Cargadas {len(self.samples)} muestras activas")
            
            self.apply_filters()
            
            # Actualizar estadísticas después de cargar
            self.update_stats()
            
        except Exception as e:
            print(f"❌ ERROR cargando muestras: {str(e)}")
            self.show_error(f"Error cargando muestras: {str(e)}")
    
    def apply_filters(self, e=None):
        """Aplicar filtros a la lista"""
        filtered = self.samples
        
        # Filtro por código
        if self.filter_code.value:
            filtered = [s for s in filtered if self.filter_code.value.lower() in s.sample_code.lower()]
        
        # Filtro por estado
        if self.filter_status.value:
            filtered = [s for s in filtered if s.status == self.filter_status.value]
        
        self.filtered_samples = filtered
        self.render_table()
    
    def render_table(self):
        """Renderizar tabla de muestras"""
        self.samples_table.rows.clear()
        
        if not self.filtered_samples:
            # Mostrar mensaje cuando no hay datos
            self.samples_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay muestras para mostrar", 
                                          size=14, color=ft.Colors.GREY_600, italic=True)),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )
        else:
            for sample in self.filtered_samples:
                # Crear fila de datos
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(sample.sample_code, size=12, weight=ft.FontWeight.BOLD),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(sample.description or "Sin descripción", size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(f"{sample.quantity} {sample.unit}", size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    self.get_status_text(sample.status),
                                    size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD
                                ),
                                bgcolor=self.get_status_color(sample.status),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12
                            ),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(str(sample.extraction_date) if sample.extraction_date else "N/A", size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(getattr(sample, 'batch_number', 'N/A'), size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(getattr(sample, 'client_name', 'N/A'), size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                        ft.DataCell(
                            ft.Text(getattr(sample, 'warehouse_name', 'N/A'), size=12),
                            on_tap=lambda e, s=sample: self.select_sample(s)
                        ),
                    ],
                    selected=self.selected_sample and self.selected_sample.id == sample.id,
                )
                
                self.samples_table.rows.append(row)
        
        self.page.update()
    
    def select_sample(self, sample):
        """Seleccionar una muestra"""
        print(f"🎯 DEBUG: SELECCIONANDO MUESTRA: {sample.sample_code}")
        self.selected_sample = sample
        self.btn_edit.disabled = False
        self.btn_delete.disabled = False
        print(f"🎯 DEBUG: Botones habilitados - Edit: {not self.btn_edit.disabled}, Delete: {not self.btn_delete.disabled}")
        self.render_table()  # Re-renderizar para mostrar selección
    
    def get_status_color(self, status):
        """Obtener color según estado"""
        colors = {
            "EXTRAIDA": ft.Colors.ORANGE_300,
            "ANALIZADA": ft.Colors.GREEN_300,
            "ALMACENADA": ft.Colors.BLUE_300,
            "DEVUELTA": ft.Colors.RED_300
        }
        return colors.get(status, ft.Colors.GREY_400)
    
    def get_status_text(self, status):
        """Obtener texto según estado"""
        texts = {
            "EXTRAIDA": "Extraída",
            "ANALIZADA": "Analizada",
            "ALMACENADA": "Almacenada",
            "DEVUELTA": "Devuelta"
        }
        return texts.get(status, "Desconocido")
    
    def handle_new_click(self, e):
        """Manejar clic en botón Nueva Muestra"""
        print("🔥 DEBUG: CLIC DETECTADO EN BOTÓN NUEVA MUESTRA!")
        try:
            self.show_new_sample_dialog(e)
        except Exception as ex:
            print(f"❌ ERROR en handle_new_click: {str(ex)}")
    
    def handle_edit_click(self, e):
        """Manejar clic en botón Editar"""
        print("🔥 DEBUG: CLIC DETECTADO EN BOTÓN EDITAR!")
        try:
            self.show_edit_sample_dialog(e)
        except Exception as ex:
            print(f"❌ ERROR en handle_edit_click: {str(ex)}")
    
    def refresh_data(self, e=None):
        """Actualizar datos"""
        self.selected_sample = None
        self.btn_edit.disabled = True
        self.btn_delete.disabled = True
        self.load_samples()
        self.show_success("🔄 Datos actualizados correctamente")
    
    def show_new_sample_dialog(self, e):
        """Mostrar diálogo para nueva muestra"""
        print("🟢 DEBUG: ENTRANDO A show_new_sample_dialog")
        try:
            self.show_sample_dialog(None)
        except Exception as ex:
            print(f"❌ ERROR en show_new_sample_dialog: {str(ex)}")
    
    def show_edit_sample_dialog(self, e):
        """Mostrar diálogo para editar muestra"""
        print("🟡 DEBUG: ENTRANDO A show_edit_sample_dialog")
        try:
            if self.selected_sample:
                print(f"🔍 DEBUG: Muestra seleccionada: {self.selected_sample.sample_code}")
                self.show_sample_dialog(self.selected_sample)
            else:
                print("⚠️ DEBUG: No hay muestra seleccionada")
                self.show_error("Por favor selecciona una muestra para editar")
        except Exception as ex:
            print(f"❌ ERROR en show_edit_sample_dialog: {str(ex)}")
    
    def show_sample_dialog(self, sample):
        """Mostrar diálogo de muestra (crear/editar)"""
        is_edit = sample is not None
        title = "✏️ Editar Muestra" if is_edit else "➕ Nueva Muestra"
        
        print(f"DEBUG: Abriendo diálogo - {'Editar' if is_edit else 'Nuevo'}")
        
        # Campos del formulario
        code_field = ft.TextField(
            label="Código de Muestra *",
            value=sample.sample_code if is_edit else "",
            prefix_icon=ft.Icons.QR_CODE,
            width=200
        )
        
        description_field = ft.TextField(
            label="Descripción",
            value=sample.description if is_edit else "",
            multiline=True,
            max_lines=3,
            expand=True,
        )

        seal_code_field = ft.TextField(
            label="Sello de seguridad",
            value=sample.seal_code if is_edit else "",
            multiline=True,
            max_lines=3,
            width=400
        )
        
        quantity_field = ft.TextField(
            label="Cantidad *",
            value=str(sample.quantity) if is_edit else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.SCALE,
            width=150
        )
        
        unit_dropdown = ft.Dropdown(
            label="Unidad",
            value=sample.unit if is_edit else "g",
            width=100,
            options=[
                ft.dropdown.Option("g", "Gramos"),
                ft.dropdown.Option("kg", "Kilogramos"),
                ft.dropdown.Option("ml", "Mililitros"),
                ft.dropdown.Option("l", "Litros")
            ]
        )
        
        status_dropdown = ft.Dropdown(
            label="Estado",
            value=sample.status if is_edit else "EXTRACTED",
            width=150,
            options=[
                ft.dropdown.Option("EXTRAIDA", "Extraída"),
                ft.dropdown.Option("ANALIZADA", "Analizada"),
                ft.dropdown.Option("ALMACENADA", "Almacenada"),
                ft.dropdown.Option("DEVUELTA", "Devuelta")
            ]
        )
        
        extraction_date_field = ft.TextField(
            label="Fecha de Extracción *",
            value=sample.extraction_date.strftime("%Y-%m-%d") if is_edit and sample.extraction_date else date.today().strftime("%Y-%m-%d"),
            keyboard_type=ft.KeyboardType.DATETIME,
            width=200
        )
        
        # Dropdowns relacionados
        batch_dropdown = ft.Dropdown(label="Lote *", width=200)
        client_dropdown = ft.Dropdown(label="Cliente", width=200)
        warehouse_dropdown = ft.Dropdown(label="Bodega *", width=200)
        
        # Cargar datos para dropdowns
        try:
            # Lotes - datos de ejemplo si el servicio falla
            try:
                batches = BatchService.get_all_batches()
                batch_dropdown.options = [ft.dropdown.Option(str(b.id), f"{b.batch_number} - {b.description}") for b in batches]
            except:
                batch_dropdown.options = [ft.dropdown.Option("1", "Lote-001 - Ejemplo")]
            
            if is_edit and hasattr(sample, 'batch_id') and sample.batch_id:
                batch_dropdown.value = str(sample.batch_id)
            
            # Clientes
            try:
                clients = ClientService.get_all_clients()
                client_dropdown.options = [ft.dropdown.Option(str(c.id), f"{c.code} - {c.name}") for c in clients]
            except:
                client_dropdown.options = [ft.dropdown.Option("1", "CLI-001 - Cliente Ejemplo")]
            
            if is_edit and hasattr(sample, 'client_id') and sample.client_id:
                client_dropdown.value = str(sample.client_id)
            
            # Bodegas
            try:
                warehouses = WarehouseService.get_all_warehouses()
                warehouse_dropdown.options = [ft.dropdown.Option(str(w.id), f"{w.code} - {w.name}") for w in warehouses]
            except:
                warehouse_dropdown.options = [ft.dropdown.Option("1", "BOD-001 - Bodega Principal")]
            
            if is_edit and hasattr(sample, 'warehouse_id') and sample.warehouse_id:
                warehouse_dropdown.value = str(sample.warehouse_id)
        
        except Exception as e:
            print(f"ERROR cargando datos para dropdowns: {str(e)}")
            # Valores por defecto
            batch_dropdown.options = [ft.dropdown.Option("1", "Lote-001 - Ejemplo")]
            client_dropdown.options = [ft.dropdown.Option("1", "CLI-001 - Cliente Ejemplo")]
            warehouse_dropdown.options = [ft.dropdown.Option("1", "BOD-001 - Bodega Principal")]
        
        def save_sample(e):
            """Guardar muestra"""
            print("DEBUG: Intentando guardar muestra...")
            try:
                # Validar campos requeridos
                if not code_field.value:
                    self.show_error("El código de muestra es requerido")
                    return
                
                if not batch_dropdown.value:
                    self.show_error("El lote es requerido")
                    return
                
                if not warehouse_dropdown.value:
                    self.show_error("La bodega es requerida")
                    return
                
                # Preparar datos
                sample_data = {
                    'sample_code': code_field.value,
                    'description': description_field.value,
                    'batch_id': int(batch_dropdown.value),
                    'client_id': int(client_dropdown.value) if client_dropdown.value else None,
                    'warehouse_id': int(warehouse_dropdown.value),
                    'quantity': float(quantity_field.value or 0),
                    'unit': unit_dropdown.value,
                    'status': status_dropdown.value,
                    'extraction_date': datetime.strptime(extraction_date_field.value, "%Y-%m-%d"),
                    'seal_code': seal_code_field.value,
                    'storage_location': storage_location_field.value,
                    'observations': ""
                }
                
                print(f"DEBUG: Datos a guardar: {sample_data}")
                
                # Crear o actualizar
                if is_edit:
                    SampleService.update_sample(sample.id, sample_data)
                    self.show_success("✅ Muestra actualizada correctamente")
                else:
                    SampleService.create_sample(sample_data)
                    self.show_success("✅ Muestra creada correctamente")
                
                # Cerrar diálogo y recargar
                dialog.open = False
                self.page.update()
                self.load_samples()
                
            except Exception as ex:
                print(f"ERROR guardando muestra: {str(ex)}")
                self.show_error(f"Error guardando muestra: {str(ex)}")
        
        def cancel_dialog(e):
            """Cancelar diálogo"""
            print("DEBUG: Cancelando diálogo...")
            dialog.open = False
            self.page.update()
        
        # Crear diálogo
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([code_field, extraction_date_field , status_dropdown], expand=True, spacing=10),
                    ft.Divider(),
                    ft.Row([client_dropdown, warehouse_dropdown, batch_dropdown], spacing=10),
                    ft.Row([quantity_field, unit_dropdown, seal_code_field], spacing=10),
                    ft.Divider(),
                    #storage_location_field,
                    description_field,
                    #observations_field
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                width=700,
                height=550
            ),
            actions=[
                ft.ElevatedButton("❌ Cancelar",  bgcolor=ft.Colors.GREY_100, on_click=lambda _: self.close_dialog(dialog)),
                ft.ElevatedButton("💾 Guardar", on_click=save_sample, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        print("DEBUG: Agregando diálogo a overlay...")
        self.page.overlay.append(dialog)
        dialog.open = True
        print("DEBUG: Actualizando página...")
        self.page.update()
        print("DEBUG: Diálogo debería estar visible ahora")
    
    def confirm_delete_sample(self, e):
        """Confirmar eliminación de muestra"""
        if not self.selected_sample:
            return
        
        def delete_sample(e):
            try:
                SampleService.delete_sample(self.selected_sample.id)
                self.show_success("✅ Muestra eliminada correctamente")
                dialog.open = False
                self.page.update()
                self.selected_sample = None
                self.btn_edit.disabled = True
                self.btn_delete.disabled = True
                self.load_samples()
            except Exception as ex:
                self.show_error(f"Error eliminando muestra: {str(ex)}")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🗑️ Confirmar Eliminación"),
            content=ft.Text(f"¿Está seguro de eliminar la muestra '{self.selected_sample.sample_code}'?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("❌ Cancelar", on_click=lambda _: self.close_dialog(dialog)),
                ft.ElevatedButton("🗑️ Eliminar", on_click=delete_sample, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        """Cerrar diálogo"""
        dialog.open = False
        self.page.update()
    
    def show_success(self, message):
        """Mostrar mensaje de éxito"""
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()
    
    def show_error(self, message):
        """Mostrar mensaje de error"""
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()