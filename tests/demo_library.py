"""Datos sintéticos para pruebas/capturas; nunca se instalan en la aplicación."""

import math
import wave
import cairo

ALBUMS = (
    ("Luz de invierno", "Elena Mar", "#d8a89d", "#722b3b"),
    ("Horizonte azul", "Atlas Sur", "#8faed1", "#23335d"),
    ("La ciudad duerme", "Los Días", "#d9c985", "#403e31"),
    ("Jardín interior", "Clara Norte", "#b5ba99", "#2e493d"),
    ("Después del sol", "Elena Mar", "#e9b16f", "#87382a"),
    ("Órbita", "Satélite", "#69697d", "#e6babc"),
    ("Cinta magnética", "Los Días", "#d2b7a3", "#343c4b"),
    ("Río lento", "Atlas Sur", "#a6c2be", "#31494d"),
    ("Aire de septiembre", "Clara Norte", "#c3b6c9", "#4d3b5c"),
    ("Noche clara", "Satélite", "#333d53", "#d2d6e1"),
)


def color(context, value):
    context.set_source_rgb(*(int(value[i:i+2], 16)/255 for i in (1,3,5)))


def seed(library, root):
    tags = {}
    for index, (album, artist, ground, ink) in enumerate(ALBUMS):
        folder = root / str(index)
        folder.mkdir()
        image = cairo.ImageSurface(cairo.FORMAT_RGB24, 512, 512)
        cr = cairo.Context(image)
        color(cr, ground)
        cr.paint()
        color(cr, ink)
        if index % 3 == 0:
            cr.arc(310, 270, 205, 0, math.tau)
            cr.fill()
            color(cr, ground)
            cr.rectangle(0, 240, 240, 70)
            cr.fill()
        elif index % 3 == 1:
            cr.move_to(0, 430)
            cr.line_to(330, 80)
            cr.line_to(512, 430)
            cr.fill()
        else:
            for position in range(6):
                cr.rectangle(60+position*68, 120+(position%2)*30, 30, 240)
            cr.fill()
        color(cr, ink)
        cr.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(24)
        cr.move_to(32, 50)
        cr.show_text(artist.upper())
        cr.set_font_size(17)
        cr.move_to(32, 478)
        cr.show_text(album)
        image.write_to_png(str(folder / "cover.png"))
        for number in range(2):
            audio = folder / f"Pista {number+1}.wav"
            with wave.open(str(audio), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(8000)
                output.writeframes(b"\x00\x00" * 8000 * 15)
            tags[str(audio.resolve())] = dict(title=("Un lugar para volver" if number == 0 else "Todo sigue aquí"),
                                            artist=artist, album=album, duration=15)
    return library.import_paths([root], lambda path: tags[str(path)])
