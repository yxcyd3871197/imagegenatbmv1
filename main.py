from flask import Flask, request, jsonify, send_file, abort
from PIL import Image, ImageDraw, ImageFont, ImageColor
from functools import wraps
import os, logging

app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
logging.basicConfig(level=logging.INFO)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        abort(401, description="Unauthorized: Invalid or missing API key")
    return decorated_function

@app.route('/process_image', methods=['POST'])
@require_api_key
def process_image():
    try:
        logging.info("🚀 API-Request erhalten.")

        # **📥 BILDER & TEXTE LADEN**
        file = request.files['image']
        overlay_file = request.files.get('overlay_image')
        text = request.form.get('text', 'Kein Text angegeben')
        font_name = request.form.get('font', 'RobotoSlab-Regular.ttf')
        font_color = request.form.get('font_color', '#000000')
        font_size = request.form.get('font_size')
        text_field_border_color = request.form.get('text_field_border_color', '#00000000') # Transparent default
        text_field_border_width = int(request.form.get('text_field_border_width', 0))
        text_align = request.form.get('text_align', 'left')
        # **📌 TEXTFELD PARAMETER**
        text_field_x = int(request.form.get('text_field_x', 0))
        text_field_y = int(request.form.get('text_field_y', 0))
        text_field_width = int(request.form.get('text_field_width', 800))
        text_field_height = int(request.form.get('text_field_height', 200))

        # **📌 OVERLAY PARAMETER**
        overlay_x = int(request.form.get('overlay_x', 0))
        overlay_y = int(request.form.get('overlay_y', 0))
        overlay_width = int(request.form.get('overlay_width', 100))
        overlay_height = int(request.form.get('overlay_height', 100))
        overlay_opacity = int(request.form.get('overlay_opacity', 255))  # Neu: Transparenz (0-255)

        # **📌 BORDER PARAMETER**
        overlay_border_color = request.form.get('overlay_border_color', '#000000')
        overlay_border_thickness = int(request.form.get('overlay_border_thickness', 5))
        overlay_corner_radius = int(request.form.get('overlay_corner_radius', 20))

        # 🖼 **HINTERGRUNDBILD LADEN**
        image = Image.open(file).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # **📌 SCHRIFT PRÜFEN**
        fonts_dir = 'fonts'
        font_path = os.path.join(fonts_dir, font_name)
        if not os.path.exists(font_path):
            return jsonify({'error': f'Schriftart {font_name} nicht gefunden.'}), 400

        # 🖍 **TEXT ZEICHNEN**
        if font_size:
            font = ImageFont.truetype(font_path, int(font_size))
        else:
            # Autofit Textfeld
            font_size = 100  # Startgröße
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            while text_width > text_field_width or text_height > text_field_height:
                font_size -= 1
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
        # Draw text field border
        if text_field_border_width > 0:
            draw.rectangle(
                [(text_field_x, text_field_y), (text_field_x + text_field_width, text_field_y + text_field_height)],
                outline=text_field_border_color,
                width=text_field_border_width
            )

        if font_size:
            font = ImageFont.truetype(font_path, int(font_size))
        else:
            # Autofit Textfeld
            font_size = 100  # Startgröße
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            while text_width > text_field_width or text_height > text_field_height:
                font_size -= 1
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

        if text_align == 'center':
            text_x = text_field_x + (text_field_width - text_width) / 2
        elif text_align == 'right':
            text_x = text_field_x + (text_field_width - text_width)
        else:  # left
            text_x = text_field_x

        draw.text((text_x, text_field_y), text, fill=font_color, font=font)

        logging.info("✅ Text erfolgreich gezeichnet.")
        # 🖼 **OVERLAY HANDHABEN**
        if overlay_file:
            overlay = Image.open(overlay_file).convert("RGBA")
            overlay = resize_keep_aspect_ratio(overlay, overlay_width, overlay_height)

            # **🟢 TRANSPARENZ ANWENDEN**
            if overlay_opacity < 255:
                overlay = apply_transparency(overlay, overlay_opacity)

            # **🖌 RAHMEN UM OVERLAY**
            overlay = add_border_to_overlay(overlay, overlay_border_thickness, overlay_border_color, overlay_corner_radius)

            image.paste(overlay, (overlay_x, overlay_y), overlay)
            logging.info(f"✅ Overlay erfolgreich hinzugefügt mit {overlay_opacity} Opazität.")

        # 📤 **BILD SPEICHERN & SENDEN**
        output_path = 'output_image.png'
        image.save(output_path, format='PNG')
        logging.info("✅ Bild erfolgreich erstellt!")
        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        logging.error(f"Fehler bei der Bildverarbeitung: {str(e)}")
        return jsonify({'error': str(e)}), 400
# **📌 FUNKTIONEN FÜR BILDVERARBEITUNG**


def resize_keep_aspect_ratio(image, max_width, max_height):
    """ Skaliert das Bild proportional auf die maximale Größe. """
    ratio = min(max_width / image.width, max_height / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.LANCZOS)

def apply_transparency(image, opacity):
    """ Setzt die Transparenz (0 = komplett unsichtbar, 255 = komplett sichtbar). """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    alpha = image.split()[3].point(lambda p: p * (opacity / 255))
    image.putalpha(alpha)
    return image

def add_border_to_overlay(overlay, thickness, color, radius):
    """ Erstellt einen mittig ausgerichteten Border um das Overlay-Bild herum. """
    # **🚀 Exakte Originalgröße beibehalten**
    new_size = (
        overlay.width + 2 * thickness,  
        overlay.height + 2 * thickness  
    )

    # Neues Bild für den Border
    border_layer = Image.new("RGBA", new_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(border_layer)

    # **🔹 Rahmen exakt um das Overlay setzen**
    draw.rounded_rectangle(
        [(thickness / 2, thickness / 2),  
         (new_size[0] - thickness / 2 - 1, new_size[1] - thickness / 2 - 1)],  
        radius=radius + (thickness / 2),  
        outline=color,
        width=thickness
    )

    # **🎯 Overlay exakt in die Mitte setzen**
    border_layer.paste(overlay, (thickness, thickness), overlay)

    return border_layer

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
