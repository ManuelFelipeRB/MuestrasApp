import flet as ft
import math

def main(page: ft.Page):
    page.title = "My Projects"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_50
    
    # Función para navegar a diferentes rutas
    def navigate_to_project(project_name):
        def on_click(e):
            page.route = f"/{project_name.lower().replace(' ', '_')}"
            page.update()
        return on_click
    
    # Header con título y filtro
    def create_header():
        return ft.Row([
            ft.Text(
                "My Projects",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK87
            ),
            ft.Container(expand=True),
            ft.Row([
                ft.Text("Sort By:", size=14, color=ft.Colors.GREY_600),
                ft.Dropdown(
                    value="Recent Project",
                    options=[
                        ft.dropdown.Option("Recent Project"),
                        ft.dropdown.Option("Name"),
                        ft.dropdown.Option("Date Created"),
                    ],
                    width=150,
                    text_size=14,
                    border_color=ft.Colors.GREY_300,
                )
            ])
        ])
    
###################### Crear TODAS las tarjeta de proyecto  ###########################################
    def create_project_card(title, description, color, avatars, project_route):
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
            width=280,
            height=160,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
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
                                    color=ft.Colors.GREY_600
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
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.BLUE_400, border_radius=4),
                        ft.Text("Layouting", size=12, color=ft.Colors.GREY_700)
                    ], spacing=8),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=ft.Colors.PURPLE_400, border_radius=4),
                        ft.Text("Graphic Design", size=12, color=ft.Colors.GREY_700)
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
            "title": "Graphic Design",
            "description": "Composition banner book cover",
            "color": ft.Colors.PINK_400,
            "avatars": ["https://images.unsplash.com/photo-1494790108755-2616b332c4a2?w=50", 
                      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50"],
            "project_route": "graphic_design"
        },
        {
            "title": "Magazine",
            "description": "Editorial page content",
            "color": ft.Colors.BLUE_600,
            "avatars": ["https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50",
                      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50"],
            "project_route": "magazine"
        },
        {
            "title": "Layouting",
            "description": "Fix layout on page ads",
            "color": ft.Colors.LIGHT_BLUE_400,
            "avatars": ["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50"],
            "project_route": "layouting"
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
            "description": "Get the photo ready for magazine",
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
        elif page.route == "/graphic_design":
            page.views.append(
                ft.View(
                    "/graphic_design",
                    [
                        ft.AppBar(title=ft.Text("Graphic Design Project"), bgcolor=ft.Colors.PINK_400),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Graphic Design Project", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de diseño gráfico"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )
        elif page.route == "/magazine":
            page.views.append(
                ft.View(
                    "/magazine",
                    [
                        ft.AppBar(title=ft.Text("Magazine Project"), bgcolor=ft.Colors.BLUE_600),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Magazine Project", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de revista"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )

        elif page.route == "/layouting":
            page.views.append(
                ft.View(
                    "/layouting",  # ✅ Misma ruta
                    [
                        ft.AppBar(title=ft.Text("Layouting Project"), bgcolor=ft.Colors.AMBER_200),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Layouting Project", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Aquí iría el contenido específico del proyecto de layouting"),
                                ft.ElevatedButton("Volver", on_click=lambda _: page.go("/"))
                            ], spacing=20),
                            padding=20
                        )
                    ]
                )
            )
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
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)