import qrcode

# 1. La URL exacta de tu página web
url_menu = "https://losvillanos.pythonanywhere.com"

# 2. Configuramos el diseño del QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H, # Alta corrección de errores
    box_size=10, # Tamaño de los cuadritos
    border=4,    # Borde blanco alrededor
)

qr.add_data(url_menu)
qr.make(fit=True)

# 3. Creamos la imagen (puedes cambiar los colores si quieres)
imagen_qr = qr.make_image(fill_color="black", back_color="white")

# 4. Guardamos la imagen
imagen_qr.save("qr_los_villanos.png")
print("¡Código QR generado exitosamente como 'qr_los_villanos.png'!")