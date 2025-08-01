import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import win32clipboard
import os
entidad = "JG SecureTech"


fondo_transparente = True  # ← cambia esto a True si quieres fondo transparente
copiar_portapapeles = True  # ← si quieres que se copie al portapapeles

# --- DATOS DEL SELLO ---
nombre = " Tu nombre"
apellido = "Tu apellido"
email = "tu email"


fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
qr_datos = f"""Firmado por: {nombre} {apellido}
Fecha: {fecha}
Entidad: {entidad}
E-mail: {email}"""

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
    box_size=10,
    border=2,
)
qr.add_data(qr_datos)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

width, height = qr_img.size
pixels = qr_img.load()
for x in range(width):
    for y in range(height):
        r, g, b, a = pixels[x, y]
        if (r, g, b) == (0, 0, 0):
            ratio = x / width
            green = int(180 * (1 - ratio))
            pixels[x, y] = (0, green, 0, a)

# --- CREAR SELLO FINAL ---
ancho = 450
alto = 170
modo = "RGBA"
fondo_color = (255, 255, 255, 0) if fondo_transparente else (255, 255, 255, 255)
sello = Image.new(modo, (ancho, alto), fondo_color)
sello.paste(qr_img.resize((150, 150)), (10, 10))

# --- DIBUJAR TEXTO AL LADO ---
draw = ImageDraw.Draw(sello)
try:
    fuente = ImageFont.truetype("arial.ttf", 16)
except:
    fuente = ImageFont.load_default()

texto = [
    " ",
    "Firmado electrónicamente por:",
    nombre,
    apellido,
    f"Fecha: {fecha}"
]

x_text = 180
y_text = 20
for linea in texto:
    draw.text((x_text, y_text), linea, font=fuente, fill="black")
    y_text += 22

# --- GUARDAR SELLO PNG ---
import os

ruta_sello = "sello_firma.png"
if os.path.exists(ruta_sello):
    os.remove(ruta_sello)

sello.save(ruta_sello)
print("✅ Sello visual generado: sello_firma.png")


# --- COPIAR AL PORTAPAPELES ---
if copiar_portapapeles:
    output = io.BytesIO()
    sello.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # quitar encabezado BMP
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    print("📋 Sello copiado al portapapeles. ¡Ya puedes pegarlo con Ctrl+V!")
