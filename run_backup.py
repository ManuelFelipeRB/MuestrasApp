import flet as ft
import math

def main(page: ft.Page):
    page.title = "Gestíon de Contenedores"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_50
    
    # Función para navegar a diferentes rutas
    def navigate_to_project(project_route):
        def on_click(e):
            print(f"Navegando a: /{project_route}")  # Debug
            page.route = f"/{project_route}"
            page.update()
        return on_click
    
    # Header con título y filtro
    def create_header():
        return ft.Row([
            ft.Text(
                "Gestión de Contenedores",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK87
            ),
            ft.Container(expand=True),
            # ft.Row([
            #     ft.Text("Sort By:", size=14, color=ft.Colors.GREY_600),
            #     ft.Dropdown(
            #         value="Recent Containers",
            #         options=[
            #             ft.dropdown.Option("Recent Project"),
            #             ft.dropdown.Option("Name"),
            #             ft.dropdown.Option("Date Created"),
            #         ],
            #         width=150,
            #         text_size=14,
            #         border_color=ft.Colors.GREY_300,
            #     )
            # ])
        ])
    
###################### Crear TODAS las tarjeta de proyecto  ###########################################
    
    def create_project_card(title, description, color, avatars, project_route):

        def on_hover(e):
            container = e.control  # El Container que tiene el on_hover
            if e.data == "true":  # mouse está encima
                container.bgcolor = ft.Colors.GREY_50
                container.shadow = ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLACK54,
                    offset=ft.Offset(0, 2)
                )
            else:  # mouse se fue
                container.bgcolor = ft.Colors.WHITE
                container.shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2)
                )
            container.update()  # Usar container.update() en lugar de e.control.update()

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=4,
                            height=60,
                            bgcolor=color,
                            border_radius=2
                        ),
                        ft.Column([
                            ft.Text(
                                title,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK87
                            ),
                            ft.Text(
                                description,
                                size=12,
                                color=ft.Colors.GREY_600,
                                max_lines=2
                            )
                        ], expand=True, spacing=5)
                    ], spacing=15)
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.Row([
                        ft.CircleAvatar(
                            foreground_image_src=avatar,
                            radius=12
                        ) for avatar in avatars
                    ], spacing=-8),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.MORE_HORIZ,
                        icon_size=20,
                        icon_color=ft.Colors.GREY_400
                    )
                ])
            ], spacing=10),
            expand=True,
            on_hover=on_hover,
            height=180,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            # REMOVER: mouse_cursor=ft.MouseCursor.CLICK,  # ❌ Esto causa el error
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2)
            ),
            on_click=navigate_to_project(project_route)
        )

    
    # Crear gráfico circular (donut chart)
    def create_progress_chart():
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Stack([
                        ft.Container(
                            width=120,
                            height=120,
                            border_radius=60,
                            border=ft.border.all(8, ft.Colors.GREY_200)
                        ),
                        ft.Container(
                            width=120,
                            height=120,
                            border_radius=60,
                            border=ft.border.all(8, ft.Colors.TRANSPARENT),
                            gradient=ft.SweepGradient(
                                center=ft.alignment.center,
                                start_angle=0,
                                end_angle=math.pi * 1.5,
                                colors=[
                                    ft.Colors.BLUE_400,
                                    ft.Colors.PURPLE_400,
                                    ft.Colors.ORANGE_400,
                                ]
                            )
                        ),
                        ft.Container(
                            width=120,
                            height=120,
                            content=ft.Column([
                                ft.Text(
                                    "3",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK87
                                ),
                                ft.Text(
                                    "Completed",
                                    size=12,
                                    color=ft.Colors.WHITE
                                )
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )
                    ]),
                    alignment=ft.alignment.center
                ),
                ft.Container(height=20),
                ft.Column([
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.GREEN_400, border_radius=4),
                        ft.Text("Asignaciones", size=12, color=ft.Colors.GREY_700)
                    ], spacing=8),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.PURPLE_400, border_radius=4),
                        ft.Text("Gestión Inventario", size=12, color=ft.Colors.GREY_700)
                    ], spacing=8),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.ORANGE_400, border_radius=4),
                        ft.Text("Photoshoot", size=12, color=ft.Colors.GREY_700)
                    ], spacing=8),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.GREY_300, border_radius=4),
                        ft.Text("Branding", size=12, color=ft.Colors.GREY_700)
                    ], spacing=8),
                ], spacing=8)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )
    
    # Panel derecho con estadísticas
    def create_stats_panel():
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Total Project",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK87
                ),
                ft.Container(height=20),
                create_progress_chart()
            ]),
            width=300,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2)
            )
        )
    
    # Datos de los proyectos
    projects_data = [
        {
            "title": "Gestion Inventario",
            "description": "Composition banner book cover",
            "color": ft.Colors.PINK_400,
            "avatars": ["https://images.unsplash.com/photo-1494790108755-2616b332c4a2?w=50", 
                      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50"],
            "project_route": "Gestion_inventario"
        },
        {
            "title": "Ingresos",
            "description": "Editorial page content",
            "color": ft.Colors.BLUE_600,
            "avatars": ["https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50",
                      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50"],
            "project_route": "Ingresos"
        },
        {
            "title": "Asignaciones",
            "description": "Asignacion de contenedores a clientes",
            "color": ft.Colors.GREEN_200,
            "avatars": ["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50"],
            "project_route": "Asignaciones"
        },
        {
            "title": "Branding",
            "description": "Brainstorming shape",
            "color": ft.Colors.ORANGE_400,
            "avatars": ["https://images.unsplash.com/photo-1463453091185-61582044d556?w=50"],
            "project_route": "branding"
        },
        {
            "title": "Guidelines",
            "description": "Make a brand guidelines for brand campaign",
            "color": ft.Colors.LIGHT_BLUE_300,
            "avatars": ["https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50",
                      "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=50"],
            "project_route": "guidelines"
        },
        {
            "title": "Photoshoot",
            "description": "Get the photo ready for Ingresos",
            "color": ft.Colors.DEEP_PURPLE_400,
            "avatars": ["https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=50",
                      "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=50",
                      "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=50"],
            "project_route": "photoshoot"
        }
    ]
    
    # Layout principal
    main_content = ft.Column([
        create_header(),
        ft.Container(height=30),
        ft.Row([
            # Grid de proyectos
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        create_project_card(**projects_data[0]),
                        create_project_card(**projects_data[1]),
                        create_project_card(**projects_data[2])
                    ], spacing=20),
                    ft.Container(height=20),
                    ft.Row([
                        create_project_card(**projects_data[3]),
                        create_project_card(**projects_data[4]),
                        create_project_card(**projects_data[5])
                    ], spacing=20)
                ]),
                expand=True
            ),
            ft.Container(width=30),
            # Panel de estadísticas
            create_stats_panel()
        ], 
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START)
    ],
    scroll=ft.ScrollMode.AUTO)
    
    # Funciones de navegación para las rutas
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [main_content],
                    padding=20,
                    bgcolor=ft.Colors.GREY_50
                )
            )
        elif page.route == "/Gestion_inventario":
            page.views.append(
                ft.View(
                    "/Gestion_inventario",
                    [
                        ft.AppBar(title=ft.Text("Gestion Inventario Project"), bgcolor=ft.Colors.PINK_400),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Gestion Inventario Project", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de diseño gráfico"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )
        elif page.route == "/Ingresos":
            page.views.append(
                ft.View(
                    "/Ingresos",
                    [
                        ft.AppBar(title=ft.Text("Ingresos Project"), bgcolor=ft.Colors.BLUE_600),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ingresos Project", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de revista"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )

        elif page.route == "/Asignaciones":
            page.views.append(
                ft.View(
                    "/Asignaciones",  # ✅ Misma ruta
                    [
                        ft.AppBar(title=ft.Text("Asignacion de Contenedores"), bgcolor=ft.Colors.GREEN_200),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Asignacion de Contenedores a clientes", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de layouting"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )

        elif page.route == "/photoshoot":
            from app.ui.samples_view import SamplesView
            page.views.append(SamplesView(page).get_view())  # ✅ CORRECTO


        
        # Agrega más rutas según necesites...
        
        page.update()
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

# Para integrar en tu proyecto existente, simplemente copia las funciones necesarias
# y adapta el sistema de navegación a tu estructura de rutas actual

# Al final de tu archivo main:
if __name__ == "__main__":
    ft.app(target=main,  view=ft.AppView.WEB_BROWSER, port=8080)