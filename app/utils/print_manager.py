import flet as ft
from datetime import datetime
import tempfile
import os
import webbrowser
import win32print
import win32api
from typing import Dict, List


class HtmlPrintManager:
    """Gestor de impresión usando HTML/CSS - Solución universal"""
    
    @staticmethod
    def print_sample_data(page: ft.Page, sample_data: Dict):
        """Imprimir usando HTML - Funciona siempre"""
        print_manager = HtmlPrintManager()
        print_manager._show_print_dialog(page, sample_data)
    
    def _show_print_dialog(self, page: ft.Page, sample_data: Dict):
        """Mostrar diálogo de impresión HTML"""
        
        self.selected_printer = None
        self.available_printers = self._get_available_printers()

        # Vista previa del contenido
        preview_content = self._generate_preview_content(sample_data)
        
        def execute_print(e):
            """Imprimir directamente sin abrir navegador"""
            try:
                print("🖨️ DEBUG: Imprimiendo directamente...")
                
                # Validar que hay impresora seleccionada
                printer_name = getattr(self, 'selected_printer', None) or (self.available_printers[0] if self.available_printers else None)

                if not printer_name:
                    self._show_error(page, "❌ No hay impresora seleccionada")
                    return

                # Validar que la impresora existe
                if printer_name != "Impresora predeterminada" and not self._validate_printer(printer_name):
                    self._show_error(page, f"❌ La impresora {printer_name} no está disponible")
                    return
                # Generar HTML
                html_content = self._generate_html_content(sample_data)
                
                # Imprimir directamente
                success = self._print_directly_to_printer(sample_data, printer_name)
                
                if success:
                    # Cerrar diálogo
                    print_dialog.open = False
                    page.update()
                    
                    self._show_success(page, f"🖨️ Impresión enviada a: {printer_name}")
                else:
                    self._show_error(page, "❌ Error al enviar a impresión")
                    
            except Exception as ex:
                print(f"❌ DEBUG: Error imprimiendo: {str(ex)}")
                self._show_error(page, f"Error: {str(ex)}")
            
        
        def close_dialog(e):
            """Cerrar diálogo"""
            print_dialog.open = False
            page.update()
        
        # Crear diálogo
        print_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PRINT, color=ft.Colors.BLUE_600),
                ft.Text("🖨️ Imprimir Etiqueta (HTML)", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Selecciona la impresora y configura las opciones de impresión:",
                        size=12,
                        color=ft.Colors.BLUE_700
                    ),
                    
                    # Selector de impresora
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🖨️ Seleccionar Impresora", 
                                size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                            ft.Dropdown(
                                width=400,
                                options=[ft.dropdown.Option(printer) for printer in self.available_printers],
                                value=self.available_printers[0] if self.available_printers else None,
                                on_change=lambda e: setattr(self, 'selected_printer', e.control.value)
                            )
                        ], spacing=5),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=10,
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.BLUE_200)
                    ),
                    
                    ft.Divider(),
                    
                    # Vista previa
                    ft.Container(
                        content=ft.Column([
                            ft.Text("👁️ Vista Previa", 
                                size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                            preview_content
                        ], spacing=10),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=15,
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.GREEN_200)
                    )
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                width=450,
                height=600  # Aumentar altura para el selector
            ),
            actions=[
                ft.ElevatedButton(
                    "❌ Cancelar", 
                    bgcolor=ft.Colors.GREY_100, 
                    on_click=close_dialog
                ),
                ft.ElevatedButton(
                    "🖨️ Imprimir Ahora", 
                    bgcolor=ft.Colors.BLUE_600, 
                    color=ft.Colors.WHITE,
                    on_click=execute_print
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Mostrar diálogo
        page.overlay.append(print_dialog)
        print_dialog.open = True
        page.update()
    

    def _print_directly_to_printer(self, sample_data: Dict, printer_name: str = None):
        """Impresión directa usando win32print - MÁS PROFESIONAL"""
        try:
            import win32print
            import win32ui
            from win32.lib import win32con
            
            # Usar impresora predeterminada si no se especifica
            if not printer_name or printer_name == "Impresora predeterminada":
                printer_name = win32print.GetDefaultPrinter()
            
            print(f"🖨️ DEBUG: Imprimiendo directamente en: {printer_name}")
            
            # Abrir impresora
            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                # Configurar trabajo de impresión
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_name)
                
                # Iniciar documento
                hdc.StartDoc("Etiqueta de Muestra")
                hdc.StartPage()
                
                # Configurar fuentes
                font_title = win32ui.CreateFont({
                    "name": "Arial",
                    "height": 60,
                    "weight": 700
                })
                
                font_normal = win32ui.CreateFont({
                    "name": "Arial", 
                    "height": 40,
                    "weight": 400
                })
                
                font_small = win32ui.CreateFont({
                    "name": "Arial",
                    "height": 30,
                    "weight": 400
                })
                
                # Posiciones
                x_start = 100
                y_pos = 100
                line_height = 60
                
                # Imprimir título
                hdc.SelectObject(font_title)
                hdc.TextOut(x_start, y_pos, "ETIQUETA DE MUESTRA")
                y_pos += line_height * 2
                
                # Imprimir código principal (más grande)
                hdc.SelectObject(font_title)
                hdc.TextOut(x_start, y_pos, f"CÓDIGO: {sample_data.get('sample_code', 'N/A')}")
                y_pos += line_height * 2
                
                # Imprimir datos
                hdc.SelectObject(font_normal)
                
                fields = [
                    ("Cliente:", sample_data.get('client_name', 'N/A')),
                    ("Fecha extracción:", sample_data.get('extraction_date', 'N/A')),
                    ("Almacén:", sample_data.get('warehouse_name', 'N/A')),
                    ("Lote:", sample_data.get('batch_name', 'N/A')),
                    ("Estado:", sample_data.get('status', 'N/A')),
                    ("Cantidad:", f"{sample_data.get('quantity', '')} {sample_data.get('unit', '')}"),
                    ("Código Sello:", sample_data.get('seal_code', 'N/A'))
                ]
                
                for label, value in fields:
                    hdc.TextOut(x_start, y_pos, f"{label} {value}")
                    y_pos += line_height
                
                # Footer
                y_pos += line_height
                hdc.SelectObject(font_small)
                hdc.TextOut(x_start, y_pos, f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
                # Finalizar
                hdc.EndPage()
                hdc.EndDoc()
                
            finally:
                win32print.ClosePrinter(hprinter)
                
            return True
            
        except Exception as ex:
            print(f"❌ ERROR impresión directa: {str(ex)}")
            return False
    
    def _generate_html_content(self, sample_data: Dict) -> str:
        """Generar HTML perfectamente formateado para impresión"""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Etiqueta de Muestra</title>
            <style>
                @page {{
                    size: A6;
                    margin: 0.5cm;
                }}
                
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    font-size: 12px;
                    line-height: 1.6;
                }}
                
                .label-container {{
                    border: 2px solid #333;
                    padding: 15px;
                    max-width: 300px;
                    margin: 0 auto;
                }}
                
                .header {{
                    background-color: #333;
                    color: white;
                    text-align: center;
                    padding: 8px;
                    margin: -15px -15px 15px -15px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                
                .code-section {{
                    background-color: #fff3cd;
                    border: 2px solid #333;
                    text-align: center;
                    padding: 10px;
                    margin: 15px 0;
                    font-size: 16px;
                    font-weight: bold;
                }}
                
                .data-section {{
                    margin: 15px 0;
                }}
                
                .field-row {{
                    display: flex;
                    margin: 8px 0;
                    border-bottom: 1px dotted #ccc;
                    padding-bottom: 4px;
                }}
                
                .field-label {{
                    font-weight: bold;
                    width: 120px;
                    flex-shrink: 0;
                }}
                
                .field-value {{
                    flex-grow: 1;
                    margin-left: 10px;
                }}
                
                .footer {{
                    background-color: #f8f9fa;
                    text-align: center;
                    padding: 5px;
                    margin: 15px -15px -15px -15px;
                    font-size: 10px;
                    color: #666;
                }}
                
                @media print {{
                    body {{
                        margin: 0;
                        padding: 10px;
                    }}
                    .no-print {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="no-print" style="text-align: center; margin-bottom: 20px;">
                <button onclick="window.print()" style="padding: 10px 20px; font-size: 14px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🖨️ Imprimir Etiqueta
                </button>
                <p style="color: #666; font-size: 12px;">Usa Ctrl+P o el botón de arriba para imprimir</p>
            </div>

            <div class="label-container">
                <div class="header">
                    ETIQUETA DE MUESTRA
                </div>
                
                <div class="code-section">
                    {sample_data.get('sample_code', 'N/A')}
                </div>
                
                <div class="data-section">
                    <div class="field-row">
                        <div class="field-label">Cliente:</div>
                        <div class="field-value">{sample_data.get('client_name', 'N/A')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Fecha extracción:</div>
                        <div class="field-value">{sample_data.get('extraction_date', 'N/A')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Almacén:</div>
                        <div class="field-value">{sample_data.get('warehouse_name', 'N/A')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Lote:</div>
                        <div class="field-value">{sample_data.get('batch_name', 'N/A')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Estado:</div>
                        <div class="field-value">{sample_data.get('status', 'N/A')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Cantidad:</div>
                        <div class="field-value">{sample_data.get('quantity', '')} {sample_data.get('unit', '')}</div>
                    </div>
                    <div class="field-row">
                        <div class="field-label">Código Sello:</div>
                        <div class="field-value">{sample_data.get('seal_code', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="footer">
                    Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_available_printers(self) -> List[str]:
        """Obtener lista de impresoras disponibles"""
        try:
            printers = []
            for printer in win32print.EnumPrinters(2):
                printers.append(printer[2])  # Nombre de la impresora
            return printers
        except:
            return ["Impresora predeterminada"]
        
    def _validate_printer(self, printer_name: str) -> bool:
        """Validar que la impresora existe y está disponible"""
        try:
            printers = win32print.EnumPrinters(2)
            printer_names = [printer[2] for printer in printers]
            
            print(f"🖨️ DEBUG: Impresoras disponibles: {printer_names}")
            
            if printer_name in printer_names:
                # Verificar estado de la impresora
                try:
                    handle = win32print.OpenPrinter(printer_name)
                    printer_info = win32print.GetPrinter(handle, 2)
                    win32print.ClosePrinter(handle)
                    
                    status = printer_info['Status']
                    print(f"📊 DEBUG: Estado impresora {printer_name}: {status}")
                    
                    return True
                except Exception as status_ex:
                    print(f"⚠️ DEBUG: No se pudo verificar estado: {status_ex}")
                    return True  # Asumir que funciona
            else:
                print(f"❌ DEBUG: Impresora {printer_name} no encontrada")
                return False
                
        except Exception as ex:
            print(f"❌ DEBUG: Error validando impresora: {str(ex)}")
            return False
    
    def _generate_preview_content(self, sample_data: Dict) -> ft.Container:
        """Vista previa idéntica al HTML"""
        return ft.Container(
            content=ft.Column([
                # Encabezado
                ft.Container(
                    content=ft.Text(
                        "ETIQUETA DE MUESTRA", 
                        size=14, 
                        weight=ft.FontWeight.BOLD, 
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    bgcolor=ft.Colors.GREY_800,
                    padding=ft.padding.symmetric(vertical=8),
                ),
                
                # Código principal
                ft.Container(
                    content=ft.Text(sample_data.get('sample_code', ''), 
                    size=16, weight=ft.FontWeight.BOLD, 
                    text_align=ft.TextAlign.CENTER),
                    bgcolor=ft.Colors.YELLOW_100,
                    padding=ft.padding.symmetric(vertical=10),
                    border=ft.border.all(2, ft.Colors.GREY_800)
                ),
                
                # Datos de la muestra
                ft.Container(
                    content=ft.Column([
                        self._create_field_row("Cliente:", sample_data.get('client_name', 'N/A')),
                        self._create_field_row("Fecha extracción:", sample_data.get('extraction_date', 'N/A')),
                        self._create_field_row("Almacén:", sample_data.get('warehouse_name', 'N/A')),
                        self._create_field_row("Lote:", sample_data.get('batch_name', 'N/A')),
                        self._create_field_row("Estado:", sample_data.get('status', 'N/A')),
                        self._create_field_row("Cantidad:", f"{sample_data.get('quantity', '')} {sample_data.get('unit', '')}"),
                        self._create_field_row("Código Sello:", sample_data.get('seal_code', 'N/A')),
                    ], spacing=8),
                    padding=15,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_400)
                ),
                
                # Footer
                ft.Container(
                    content=ft.Text(f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                   size=10, color=ft.Colors.GREY_600,
                                   text_align=ft.TextAlign.CENTER),
                    bgcolor=ft.Colors.GREY_100,
                    padding=ft.padding.symmetric(vertical=5),
                )
            ], spacing=0),
            width=280,
            border=ft.border.all(2, ft.Colors.GREY_800),
            border_radius=5
        )
    
    def _create_field_row(self, label: str, value: str) -> ft.Row:
        """Crear fila de campo"""
        return ft.Row([
            ft.Text(label, size=11, weight=ft.FontWeight.BOLD, width=120),
            ft.Text(str(value), size=11, expand=True)
        ], spacing=10)
    
    def _show_success(self, page: ft.Page, message: str):
        """Mostrar mensaje de éxito"""
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
    
    def _show_error(self, page: ft.Page, message: str):
        """Mostrar mensaje de error"""
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()


# Función de conveniencia
def print_sample_label_html(page: ft.Page, sample_data: Dict):
    """Imprimir etiqueta usando HTML"""
    HtmlPrintManager.print_sample_data(page, sample_data)