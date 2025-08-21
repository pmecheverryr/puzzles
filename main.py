import base64
import io
import os
import platform
import random
import subprocess
from typing import List, Tuple, Optional

import flet as ft
from PIL import Image, ImageOps
from flet_audio import Audio


def main(page: ft.Page):
    page.title = "Juego de Puzzles"
    page.scroll = "adaptive"
    page.window_min_width = 420
    page.window_min_height = 600
    page.window.height = 700
    page.window.width = 500

    path_image = None
    md_text = ""
    with open("credits_images.md", "r", encoding="utf-8") as f:
        md_text = f.read()
        f.close()

    # ---------- Estado ----------
    tiles: List[Tuple[int, str]] = []   # [(id_original, b64)]
    moves = 0
    drag_from: Optional[int] = None
    image_data: Optional[bytes] = None
    game_locked = False

    # ---------- UI base ----------
    gv = ft.GridView(expand=True, spacing=2, run_spacing=2)
    txt_moves = ft.Text("Movimientos: 0")
    dd_size = ft.Dropdown(
        label="Tamaño",
        options=[ft.dropdown.Option("2"), ft.dropdown.Option("3"), ft.dropdown.Option("4")],
        value="2",
        width=100,
    )

    audio_win = Audio(
        src="assets/sounds/clang_and_wobble.ogg",
        autoplay=False
    )
    page.overlay.append(audio_win)

    # ---------- Modal personalizado (en vez de AlertDialog) ----------
    modal_title = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
    modal_body = ft.Container()
    modal_actions = ft.Row([], alignment=ft.MainAxisAlignment.END, spacing=10)

    # fondo semitransparente
    scrim = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
        expand=True,
        visible=False,
        on_click=lambda e: hide_modal(),
    )

    # tarjeta central
    modal_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=20,
        border_radius=10,
        content=ft.Column(
            controls=[
                modal_title,
                ft.Divider(height=10),
                modal_body,
                ft.Divider(height=10),
                modal_actions,
            ],
            tight=True,
            spacing=10,
        ),
        width=440,
    )

    # overlay del modal (encima de todo)
    modal_overlay = ft.Stack(
        controls=[
            scrim,
            ft.Container(content=modal_card, expand=True, alignment=ft.alignment.center),
        ],
        expand=True,
        visible=False,
    )

    def show_modal(title: str, body_ctrl: ft.Control, actions: list[ft.Control]):
        modal_title.value = title
        modal_body.content = body_ctrl
        modal_actions.controls = actions
        scrim.visible = True
        modal_overlay.visible = True
        page.update()

    def hide_modal():
        scrim.visible = False
        modal_overlay.visible = False
        page.update()

    # ---------- Utilidades imagen ----------
    def pil_to_base64(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def bytes_to_base64(data: bytes) -> str:
        return base64.b64encode(data).decode()

    # ---------- Construir puzzle ----------
    def build_puzzle_from_bytes(data: bytes, size: int):
        nonlocal tiles, moves, image_data, game_locked
        game_locked = False    # <--- DESBLOQUEA
        image_data = data
        moves = 0
        txt_moves.value = "Movimientos: 0"

        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image).convert("RGB")

        # base cuadrada razonable (GridView escala las celdas)
        grid_size_px = 400
        image = image.resize((grid_size_px, grid_size_px))

        w, h = image.size
        piece_w, piece_h = w // size, h // size

        tiles = []
        for r in range(size):
            for c in range(size):
                crop = image.crop((
                    c * piece_w,
                    r * piece_h,
                    (c + 1) * piece_w,
                    (r + 1) * piece_h
                ))
                tiles.append((r * size + c, pil_to_base64(crop)))

        random.shuffle(tiles)
        render_grid()

    # ---------- Render & lógica ----------
    def render_grid(highlight=False):
        nonlocal drag_from
        gv.controls.clear()
        gv.runs_count = int(dd_size.value)

        for idx, (_, img_b64) in enumerate(tiles):
            border_color = ft.Colors.AMBER if highlight else ft.Colors.GREY_400

            def set_drag_from(e, i=idx):
                nonlocal drag_from, game_locked
                if game_locked:  # <--- evita iniciar arrastre
                    return
                drag_from = i

            opacity_val = 0.6 if game_locked else 1.0
            draggable = ft.Draggable(
                group=None if game_locked else "tiles",  # <--- opcional
                content=ft.Container(
                    content=ft.Image(src_base64=img_b64, fit=ft.ImageFit.COVER),
                    border=ft.border.all(1, border_color),
                    border_radius=4,
                    expand=True,
                    opacity=opacity_val  # <--- atenuar
                ),
                on_drag_start=set_drag_from,
            )

            def accept(e, target_idx=idx):
                nonlocal tiles, moves, drag_from, game_locked
                if game_locked:  # <--- ignora drops
                    return
                if drag_from is None:
                    return
                src_idx = drag_from
                if src_idx != target_idx:
                    tiles[src_idx], tiles[target_idx] = tiles[target_idx], tiles[src_idx]
                    moves += 1
                    txt_moves.value = f"Movimientos: {moves}"
                drag_from = None
                render_grid()
                check_win()

            gv.controls.append(
                ft.DragTarget(
                    group="tiles",
                    content=ft.Container(content=draggable, expand=True),
                    on_accept=accept,
                )
            )
        page.update()

    def check_win():
        nonlocal game_locked
        if tiles and all(tiles[i][0] == i for i in range(len(tiles))):
            audio.play_victory()
            game_locked = True
            render_grid(highlight=True)
            # mostrar modal de victoria
            body = ft.Text(f"Movimientos: {moves}", size=16)
            actions = [
                ft.TextButton("Cerrar", on_click=lambda e: hide_modal()),
                ft.FilledButton("🔄 Jugar de nuevo", on_click=lambda e: (hide_modal(), restart_game())),
            ]
            show_modal("🎉 ¡Ganaste!", body, actions)

    def restart_game(_=None):
        nonlocal game_locked
        game_locked = False  # <--- DESBLOQUEA
        if image_data:
            build_puzzle_from_bytes(image_data, int(dd_size.value))

    # Carpeta con tus imágenes del juego
    ASSET_IMAGES_DIR = os.path.join("assets", "puzzles")

    # extensiones válidas
    VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    def list_asset_images() -> list[str]:
        """Devuelve rutas (relativas) a imágenes dentro de assets/puzzles."""
        base = ASSET_IMAGES_DIR
        if not os.path.isdir(base):
            return []
        files = []
        for name in os.listdir(base):
            path = os.path.join(base, name)
            ext = os.path.splitext(name)[1].lower()
            if os.path.isfile(path) and ext in VALID_EXTS:
                # ruta relativa para abrir con open() y para servir como asset
                files.append(path)
        return files

    def pick_random_asset_image() -> bytes | None:
        """Elige una imagen aleatoria de assets/puzzles y devuelve sus bytes."""
        imgs = list_asset_images()
        if not imgs:
            return None
        choice = random.choice(imgs)
        with open(choice, "rb") as f:
            return f.read()

    def new_game(_=None):
        """Carga una imagen aleatoria desde assets/puzzles y arma un puzzle nuevo."""
        nonlocal image_data, moves  # si usas estas variables fuera
        data = pick_random_asset_image()
        if data is None:
            # si no hay imágenes en assets/puzzles, remezcla la actual como fallback
            if tiles:
                moves = 0
                txt_moves.value = "Movimientos: 0"
                random.shuffle(tiles)
                render_grid()
                # notify("No se encontraron imágenes en assets/puzzles. Se remezcló el puzzle actual.")
                return
            # notify("No se encontraron imágenes en assets/puzzles.")
            return

        image_data = data  # guarda como “actual”
        build_puzzle_from_bytes(image_data, int(dd_size.value))
        # notify("¡Nuevo juego aleatorio listo!")

    # ---------- Carga de imagen (macOS vs otros) ----------
    def pick_file_mac() -> Optional[str]:
        script = '''
        tell application "System Events"
            activate
            set theFile to choose file with prompt "Selecciona una imagen:" of type {"public.image"}
            POSIX path of theFile
        end tell
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception as ex:
            print("Error AppleScript:", ex)
            return None

    def on_file_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        path = e.files[0].path
        if not path:
            return
        with open(path, "rb") as f:
            data = f.read()
        build_puzzle_from_bytes(data, int(dd_size.value))

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)
    page.update()

    def load_image(_):
        nonlocal path_image
        if platform.system() == "Darwin":  # macOS → AppleScript
            path = pick_file_mac()
            if path:
                with open(path, "rb") as f:
                    data = f.read()
                    path_image = path
                build_puzzle_from_bytes(data, int(dd_size.value))
        else:  # Otros sistemas → FilePicker
            file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE
            )

    # ---------- Previsualización ----------
    def preview_image(_=None):
        if not image_data:
            return
        img_b64 = bytes_to_base64(image_data)
        body = ft.Container(
            content=ft.Image(src_base64=img_b64, fit=ft.ImageFit.CONTAIN),
            width=400, height=400,
        )
        actions = [ft.FilledButton("Cerrar", on_click=lambda e: hide_modal())]
        show_modal("Imagen completa", body, actions)

    # ---------- Layout raíz con modal encima ----------
    header = ft.Row(
[
            ft.ElevatedButton("🎲 🌄 Imagen aleatoria", on_click=new_game),
            ft.ElevatedButton(" 📷 Galería", on_click=load_image),
            ft.ElevatedButton(" 👁 Previsualizar", on_click=preview_image),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    toolbar = ft.Row(
        [
            dd_size,
            txt_moves,
            ft.ElevatedButton("🔄 Jugar de nuevo", on_click=restart_game),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        # wrap=True,
    )

    main_column = ft.Column(
        [
            header,
            ft.Divider(height=10),
            toolbar,
            ft.Container(expand=True, content=gv),
            ft.Divider(height=10)
        ],
        expand=True,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("Juego de Puzzles"),
        center_title=True,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(ft.Icons.INFO, on_click=lambda e: show_modal(
                "Información",
                ft.Column(
                    [
                        ft.Markdown(
                            md_text,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=lambda e: page.launch_url(e.data),
                            selectable=True,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                [ft.TextButton("Cerrar", on_click=lambda e: hide_modal())]
            )),
        ],
    )

    page.add(ft.Container(padding=12, content=ft.Stack([main_column, modal_overlay], expand=True), expand=True))
    new_game()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")