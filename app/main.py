"""
Aplicación principal de Flet - Versión corregida
"""
import flet as ft

def main(page: ft.Page):
    """Función principal de la aplicación Flet"""
    page.title = "Sistema de Inventario - Laboratorio"
    page.window_width = 1200
    page.window_height = 800
    
    # Interfaz temporal simple
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "🧪 Sistema de Control de Inventario de Laboratorio",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700  # Corregido: Colors con mayúscula
                ),
                ft.Divider(height=20),
                ft.Text(
                    "✅ Base de datos inicializada correctamente",
                    size=16,
                    color=ft.Colors.GREEN_700  # Corregido: Colors con mayúscula
                ),
                ft.Text(
                    "✅ Bodegas fijas creadas: W01, W022, W03, W04",
                    size=16,
                    color=ft.Colors.GREEN_700  # Corregido: Colors con mayúscula
                ),
                ft.Text(
                    "🚧 Interfaz completa en desarrollo...",
                    size=16,
                    color=ft.Colors.ORANGE_700  # Corregido: Colors con mayúscula
                ),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Probar Conexión BD",
                    on_click=lambda _: test_database_connection(page)
                ),
                ft.ElevatedButton(
                    "Probar Modelo Client",
                    on_click=lambda _: test_client_model(page)
                ),
                ft.ElevatedButton(
                    "Probar Modelo Mine",
                    on_click=lambda _: test_mine_model(page)
                ),
                ft.ElevatedButton(
                    "Probar Modelo Batch",
                    on_click=lambda _: test_batch_model(page)
                ),
                ft.ElevatedButton(
                    "Probar Modelo Sample",
                    on_click=lambda _: test_sample_model(page)
                )
            ]),
            padding=30,
            alignment=ft.alignment.center
        )
    )

def test_database_connection(page):
    """Probar conexión a la base de datos"""
    print("🔍 Iniciando prueba de conexión a BD...")  # Debug
    
    try:
        from app.models.database import DatabaseManager
        from app.models.warehouse import Warehouse
        
        print("📡 Obteniendo sesión de BD...")  # Debug
        session = DatabaseManager.get_session()
        
        # Probar consulta simple
        print("🔎 Consultando bodegas...")  # Debug
        warehouses = session.query(Warehouse).all()
        print(f"📊 Encontradas {len(warehouses)} bodegas")  # Debug
        
        # Mostrar resultado
        if warehouses:
            warehouse_list = "\n".join([f"- {w.code}: {w.name}" for w in warehouses])
            message = f"🎉 Conexión exitosa!\n\nBodegas encontradas:\n{warehouse_list}"
            print(f"✅ {message}")  # Debug - Mostrar en consola
            color = ft.Colors.GREEN_800  # Corregido: Colors con mayúscula
            bgcolor = ft.Colors.GREEN_50  # Corregido: Colors con mayúscula
        else:
            message = "⚠️ Conexión exitosa pero no se encontraron bodegas"
            print(f"⚠️ {message}")  # Debug - Mostrar en consola
            color = ft.Colors.ORANGE_800  # Corregido: Colors con mayúscula
            bgcolor = ft.Colors.ORANGE_50  # Corregido: Colors con mayúscula
        
        page.add(
            ft.Container(
                content=ft.Text(
                    message,
                    size=14,
                    color=color
                ),
                bgcolor=bgcolor,
                padding=20,
                border_radius=10
            )
        )
        
        print("🔐 Cerrando sesión de BD...")  # Debug
        DatabaseManager.close_session(session)
        print("✅ Prueba de conexión completada exitosamente")  # Debug
        
    except Exception as e:
        error_msg = f"❌ Error de conexión:\n{str(e)}"
        print(f"💥 {error_msg}")  # Debug - Mostrar error en consola
        
        page.add(
            ft.Container(
                content=ft.Text(
                    error_msg,
                    size=14,
                    color=ft.Colors.RED_800  # Corregido: Colors con mayúscula
                ),
                bgcolor=ft.Colors.RED_50,  # Corregido: Colors con mayúscula
                padding=20,
                border_radius=10
            )
        )
    
    page.update()
    print("🔄 Página actualizada")

def test_sample_model(page):
    """Probar el modelo Sample"""
    print("🔍 Iniciando prueba del modelo Sample...")
    
    try:
        from app.models.database import DatabaseManager
        from app.models.batch import Batch
        from app.models.sample import Sample
        from app.models.audit_log import AuditLog
        from datetime import date
        
        print("📡 Obteniendo sesión de BD...")
        session = DatabaseManager.get_session()
        
        # Obtener un lote existente
        print("🔎 Buscando lote existente...")
        batch = session.query(Batch).first()
        if not batch:
            print("❌ No se encontraron lotes")
            return
        print(f"✅ Lote encontrado: {batch.batch_number} (ID: {batch.id})")
        
        # Crear muestras de prueba
        print("🧪 Creando muestras de prueba...")
        
        # Verificar si ya existen
        existing_sample1 = session.query(Sample).filter_by(sample_code="SAM-001").first()
        existing_sample2 = session.query(Sample).filter_by(sample_code="SAM-002").first()
        
        if not existing_sample1:
            sample1 = Sample(
                batch_id=batch.id,
                sample_code="SAM-001",
                description="Muestra de oro - análisis inicial",
                extraction_date=date.today(),
                quantity=50.0,
                unit="g",
                status="EXTRACTED"
            )
            session.add(sample1)
            
            # Crear log de auditoría
            audit1 = AuditLog.create_log(
                action="CREATE",
                table_name="samples",
                record_id=0,  # Se actualizará después del commit
                new_values={"sample_code": "SAM-001", "quantity": 50.0},
                summary="Nueva muestra extraída para análisis"
            )
            session.add(audit1)
            session.commit()
            audit1.record_id = sample1.id
            print(f"✅ Muestra SAM-001 creada (ID: {sample1.id})")
        else:
            print(f"✅ Muestra SAM-001 ya existe (ID: {existing_sample1.id})")
        
        if not existing_sample2:
            sample2 = Sample(
                batch_id=batch.id,
                sample_code="SAM-002",
                description="Muestra de cobre - control de calidad",
                extraction_date=date.today(),
                quantity=75.0,
                unit="g",
                status="TESTED",
                tested_date=date.today(),
                test_results="Au: 15.2 g/t, Cu: 2.8%",
                lab_notes="Análisis completado según protocolo estándar"
            )
            session.add(sample2)
            
            # Crear log de auditoría
            audit2 = AuditLog.create_log(
                action="CREATE",
                table_name="samples", 
                record_id=0,
                new_values={"sample_code": "SAM-002", "status": "TESTED"},
                summary="Muestra analizada con resultados"
            )
            session.add(audit2)
            session.commit()
            audit2.record_id = sample2.id
            print(f"✅ Muestra SAM-002 creada (ID: {sample2.id})")
        else:
            print(f"✅ Muestra SAM-002 ya existe (ID: {existing_sample2.id})")
        
        # Consultar todas las muestras
        print("🔎 Consultando todas las muestras...")
        samples = session.query(Sample).all()
        print(f"📊 Encontradas {len(samples)} muestras")
        
        # Consultar logs de auditoría
        print("📋 Consultando logs de auditoría...")
        audit_logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
        print(f"📊 Últimos {len(audit_logs)} logs de auditoría")
        
        # Mostrar resultado
        if samples:
            sample_list = "\n".join([
                f"- {s.sample_code}: {s.quantity}{s.unit} - {s.status}"
                for s in samples
            ])
            audit_list = "\n".join([
                f"- {log.action} en {log.table_name}[{log.record_id}]"
                for log in audit_logs
            ])
            
            message = f"🎉 Modelos Sample y AuditLog funcionando!\n\nMuestras:\n{sample_list}\n\nÚltimos logs:\n{audit_list}"
            print(f"✅ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.INDIGO_800
                    ),
                    bgcolor=ft.Colors.INDIGO_50,
                    padding=20,
                    border_radius=10
                )
            )
        else:
            message = "⚠️ No se encontraron muestras"
            print(f"⚠️ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.ORANGE_800
                    ),
                    bgcolor=ft.Colors.ORANGE_50,
                    padding=20,
                    border_radius=10
                )
            )
        
        print("🔐 Cerrando sesión de BD...")
        DatabaseManager.close_session(session)
        print("✅ Prueba de modelo Sample completada")
        
    except Exception as e:
        error_msg = f"❌ Error en modelo Sample:\n{str(e)}"
        print(f"💥 {error_msg}")
        
        page.add(
            ft.Container(
                content=ft.Text(
                    error_msg,
                    size=14,
                    color=ft.Colors.RED_800
                ),
                bgcolor=ft.Colors.RED_50,
                padding=20,
                border_radius=10
            )
        )
    
    page.update()
    print("🔄 Página actualizada")

def test_batch_model(page):
    """Probar el modelo Batch con relaciones a Mine y Warehouse"""
    print("🔍 Iniciando prueba del modelo Batch...")
    
    try:
        from app.models.database import DatabaseManager
        from app.models.client import Client
        from app.models.mine import Mine
        from app.models.warehouse import Warehouse
        from app.models.batch import Batch
        from app.models.batch_warehouse import BatchWarehouse
        from datetime import date
        
        print("📡 Obteniendo sesión de BD...")
        session = DatabaseManager.get_session()
        
        # Obtener o crear datos necesarios
        print("🔎 Buscando datos existentes...")
        
        # Obtener cliente y mina
        mine = session.query(Mine).first()
        if not mine:
            print("➕ Creando cliente y mina para los lotes...")
            client = Client(name="Minera Test", code="TEST001")
            session.add(client)
            session.commit()
            
            mine = Mine(name="Mina Test", code="TEST_MINE", client_id=client.id)
            session.add(mine)
            session.commit()
            print(f"✅ Mina creada: {mine.name} (ID: {mine.id})")
        else:
            print(f"✅ Mina encontrada: {mine.name} (ID: {mine.id})")
        
        # Obtener bodegas (necesitamos múltiples)
        warehouses = session.query(Warehouse).limit(2).all()
        if len(warehouses) < 2:
            print("⚠️ Se necesitan al menos 2 bodegas para la prueba")
            warehouses = session.query(Warehouse).all()
        print(f"✅ Bodegas disponibles: {len(warehouses)}")
        
        # Buscar lotes existentes primero
        print("🔎 Buscando lotes existentes...")
        existing_batch1 = session.query(Batch).filter_by(batch_number="LOTE-001").first()
        existing_batch2 = session.query(Batch).filter_by(batch_number="LOTE-002").first()
        
        batch1 = existing_batch1
        batch2 = existing_batch2
        
        # Crear lotes solo si no existen
        if not existing_batch1:
            print("➕ Creando lote LOTE-001...")
            batch1 = Batch(
                mine_id=mine.id,
                batch_number="LOTE-001",
                description="Lote de mineral de cobre",
                extraction_date=date.today(),
                total_quantity=1000.0,
                unit="kg"
            )
            session.add(batch1)
            session.commit()
            print(f"✅ Lote 001 creado con ID: {batch1.id}")
        else:
            print(f"✅ Lote 001 ya existe (ID: {existing_batch1.id})")
        
        if not existing_batch2:
            print("➕ Creando lote LOTE-002...")
            batch2 = Batch(
                mine_id=mine.id,
                batch_number="LOTE-002",
                description="Lote de mineral de oro",
                extraction_date=date.today(),
                total_quantity=500.0,
                unit="kg"
            )
            session.add(batch2)
            session.commit()
            print(f"✅ Lote 002 creado con ID: {batch2.id}")
        else:
            print(f"✅ Lote 002 ya existe (ID: {existing_batch2.id})")
        
        # Verificar distribución existente
        print("🔎 Verificando distribuciones existentes...")
        existing_distributions = session.query(BatchWarehouse).filter(
            BatchWarehouse.batch_id.in_([batch1.id, batch2.id])
        ).all()
        
        if not existing_distributions:
            print("📦 Distribuyendo lotes en bodegas...")
            
            # Lote 1: distribuido en 2 bodegas
            if len(warehouses) >= 2:
                bw1 = BatchWarehouse(
                    batch_id=batch1.id,
                    warehouse_id=warehouses[0].id,
                    quantity_stored=600.0,
                    notes="Almacenamiento principal"
                )
                bw2 = BatchWarehouse(
                    batch_id=batch1.id,
                    warehouse_id=warehouses[1].id,
                    quantity_stored=400.0,
                    notes="Almacenamiento secundario"
                )
                session.add_all([bw1, bw2])
                print(f"✅ Lote 1 distribuido: {bw1.quantity_stored}kg en {warehouses[0].code}, {bw2.quantity_stored}kg en {warehouses[1].code}")
            
            # Lote 2: solo en una bodega
            bw3 = BatchWarehouse(
                batch_id=batch2.id,
                warehouse_id=warehouses[0].id,
                quantity_stored=500.0,
                notes="Almacenamiento único"
            )
            session.add(bw3)
            session.commit()
            print(f"✅ Lote 2 almacenado: {bw3.quantity_stored}kg en {warehouses[0].code}")
        else:
            print(f"✅ Distribuciones ya existen: {len(existing_distributions)} registros")
        
        # Consultar distribución
        print("🔎 Consultando distribución de lotes...")
        batch_warehouses = session.query(BatchWarehouse).all()
        print(f"📊 Encontradas {len(batch_warehouses)} distribuciones")
        
        # Consultar todos los lotes
        print("🔎 Consultando todos los lotes...")
        batches = session.query(Batch).all()
        print(f"📊 Encontrados {len(batches)} lotes")
        
        # Mostrar resultado
        if batch_warehouses:
            distribution_list = "\n".join([
                f"- {bw.batch_number}: {bw.quantity_stored}kg en {bw.warehouse_code}"
                for bw in batch_warehouses
            ])
            message = f"🎉 Modelo Batch M:N funcionando!\n\nDistribución por bodegas:\n{distribution_list}"
            print(f"✅ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.TEAL_800
                    ),
                    bgcolor=ft.Colors.TEAL_50,
                    padding=20,
                    border_radius=10
                )
            )
        else:
            message = "⚠️ No se encontraron distribuciones de lotes"
            print(f"⚠️ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.ORANGE_800
                    ),
                    bgcolor=ft.Colors.ORANGE_50,
                    padding=20,
                    border_radius=10
                )
            )
        
        print("🔐 Cerrando sesión de BD...")
        DatabaseManager.close_session(session)
        print("✅ Prueba de modelo Batch completada")
        
    except Exception as e:
        error_msg = f"❌ Error en modelo Batch:\n{str(e)}"
        print(f"💥 {error_msg}")
        
        page.add(
            ft.Container(
                content=ft.Text(
                    error_msg,
                    size=14,
                    color=ft.Colors.RED_800
                ),
                bgcolor=ft.Colors.RED_50,
                padding=20,
                border_radius=10
            )
        )
    
    page.update()
    print("🔄 Página actualizada")

def test_mine_model(page):
    """Probar el modelo Mine con relación a Client"""
    print("🔍 Iniciando prueba del modelo Mine...")
    
    try:
        from app.models.database import DatabaseManager
        from app.models.client import Client
        from app.models.mine import Mine
        
        print("📡 Obteniendo sesión de BD...")
        session = DatabaseManager.get_session()
        
        # Obtener un cliente existente (o crear uno)
        print("🔎 Buscando cliente existente...")
        client = session.query(Client).first()
        
        if not client:
            print("➕ Creando cliente para las minas...")
            client = Client(
                name="Minera Chile S.A.",
                code="MINCHI001",
                contact_person="María González",
                email="maria@minerachile.com"
            )
            session.add(client)
            session.commit()
            print(f"✅ Cliente creado con ID: {client.id}")
        else:
            print(f"✅ Cliente encontrado: {client.name} (ID: {client.id})")
        
        # Buscar minas existentes primero
        print("🔎 Buscando minas existentes...")
        existing_mine1 = session.query(Mine).filter_by(code="ELD001").first()
        existing_mine2 = session.query(Mine).filter_by(code="ESP002").first()
        
        # Crear minas solo si no existen
        if not existing_mine1:
            print("➕ Creando mina El Dorado...")
            mine1 = Mine(
                name="Mina El Dorado",
                code="ELD001",
                location="Región de Atacama",
                description="Mina de oro y cobre",
                client_id=client.id
            )
            session.add(mine1)
            session.commit()
            print(f"✅ Mina El Dorado creada con ID: {mine1.id}")
        else:
            print(f"✅ Mina El Dorado ya existe (ID: {existing_mine1.id})")
        
        if not existing_mine2:
            print("➕ Creando mina La Esperanza...")
            mine2 = Mine(
                name="Mina La Esperanza",
                code="ESP002",
                location="Región de Antofagasta",
                description="Mina de cobre",
                client_id=client.id
            )
            session.add(mine2)
            session.commit()
            print(f"✅ Mina La Esperanza creada con ID: {mine2.id}")
        else:
            print(f"✅ Mina La Esperanza ya existe (ID: {existing_mine2.id})")
        
        # Consultar todas las minas
        print("🔎 Consultando todas las minas...")
        mines = session.query(Mine).all()
        print(f"📊 Encontradas {len(mines)} minas")
        
        # Mostrar resultado
        if mines:
            mine_list = "\n".join([f"- {m.code}: {m.name} (Cliente ID: {m.client_id})" for m in mines])
            message = f"🎉 Modelo Mine funcionando!\n\nMinas encontradas:\n{mine_list}"
            print(f"✅ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.PURPLE_800
                    ),
                    bgcolor=ft.Colors.PURPLE_50,
                    padding=20,
                    border_radius=10
                )
            )
        else:
            message = "⚠️ No se encontraron minas"
            print(f"⚠️ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.ORANGE_800
                    ),
                    bgcolor=ft.Colors.ORANGE_50,
                    padding=20,
                    border_radius=10
                )
            )
        
        print("🔐 Cerrando sesión de BD...")
        DatabaseManager.close_session(session)
        print("✅ Prueba de modelo Mine completada")
        
    except Exception as e:
        error_msg = f"❌ Error en modelo Mine:\n{str(e)}"
        print(f"💥 {error_msg}")
        
        page.add(
            ft.Container(
                content=ft.Text(
                    error_msg,
                    size=14,
                    color=ft.Colors.RED_800
                ),
                bgcolor=ft.Colors.RED_50,
                padding=20,
                border_radius=10
            )
        )
    
    page.update()
    print("🔄 Página actualizada")  # Debug

def test_client_model(page):
    """Probar el modelo Client"""
    print("🔍 Iniciando prueba del modelo Client...")
    
    try:
        from app.models.database import DatabaseManager
        from app.models.client import Client
        
        print("📡 Obteniendo sesión de BD...")
        session = DatabaseManager.get_session()
        
        # Buscar cliente existente primero
        print("🔎 Buscando cliente existente...")
        existing_client = session.query(Client).filter_by(code="MIN001").first()
        
        if existing_client:
            print(f"✅ Cliente ya existe: {existing_client.name} (ID: {existing_client.id})")
        else:
            # Crear un cliente de prueba solo si no existe
            print("➕ Creando cliente de prueba...")
            test_client = Client(
                name="Minera Ejemplo S.A.",
                code="MIN001",
                contact_person="Juan Pérez",
                email="contacto@mineraejemplo.com",
                phone="+56 9 1234 5678",
                address="Av. Minera 123, Santiago, Chile"
            )
            
            session.add(test_client)
            session.commit()
            print(f"✅ Cliente creado con ID: {test_client.id}")
        
        # Consultar todos los clientes
        print("🔎 Consultando todos los clientes...")
        clients = session.query(Client).all()
        print(f"📊 Encontrados {len(clients)} clientes")
        
        # Mostrar resultado
        if clients:
            client_list = "\n".join([f"- {c.code}: {c.name}" for c in clients])
            message = f"🎉 Modelo Client funcionando!\n\nClientes encontrados:\n{client_list}"
            print(f"✅ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.BLUE_800
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=20,
                    border_radius=10
                )
            )
        else:
            message = "⚠️ No se encontraron clientes"
            print(f"⚠️ {message}")
            
            page.add(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=14,
                        color=ft.Colors.ORANGE_800
                    ),
                    bgcolor=ft.Colors.ORANGE_50,
                    padding=20,
                    border_radius=10
                )
            )
        
        print("🔐 Cerrando sesión de BD...")
        DatabaseManager.close_session(session)
        print("✅ Prueba de modelo Client completada")
        
    except Exception as e:
        error_msg = f"❌ Error en modelo Client:\n{str(e)}"
        print(f"💥 {error_msg}")
        
        page.add(
            ft.Container(
                content=ft.Text(
                    error_msg,
                    size=14,
                    color=ft.Colors.RED_800
                ),
                bgcolor=ft.Colors.RED_50,
                padding=20,
                border_radius=10
            )
        )
    
    page.update()
    print("🔄 Página actualizada")