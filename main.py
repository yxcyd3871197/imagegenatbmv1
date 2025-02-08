from flask import Flask, request, jsonify, send_file, abort
from PIL import Image, ImageDraw, ImageFont
from functools import wraps
import os, logging

app = Flask(__name__)
API_KEY = os.getenv('API_KEY', 'IhrGeheimerAPIKey')
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
    logging.info(f"Current working directory: {os.getcwd()}")

    # Prüfe, ob das fonts-Verzeichnis existiert
    fonts_dir = 'fonts'
    if os.path.exists(fonts_dir):
        logging.info(f"Contents of fonts directory: {os.listdir(fonts_dir)}")
    else:
        logging.error("Fonts directory does not exist!")

    try:
        # Eingabedaten
        file = request.files['image']
        text = request.form.get('text', 'Kein Text angegeben')
        font_name = request.form.get('font', 'RobotoSlab-Regular.ttf')

        # Falls der Font-Name keine Endung hat, ergänze ".ttf"
        if not font_name.endswith(".ttf"):
            font_name += ".ttf"

        font_path = os.path.join(fonts_dir, font_name)

        # Prüfen, ob der Font existiert
        if not os.path.exists(font_path):
            logging.error(f"Schriftart {font_path} nicht gefunden.")
            return jsonify({'error': f'Schriftart {font_name} nicht gefunden.'}), 400

        # Textfeld-Parameter
        text_field_width = int(request.form.get('text_field_width', 800))
        text_field_height = int(request.form.get('text_field_height', 200))
        text_field_x = int(request.form.get('text_field_x', 0))
        text_field_y = int(request.form.get('text_field_y', 0))
        font_color = request.form.get('font_color', 'black')

        # **NEU: Overlay-Parameter**
        overlay_file = request.files.get('overlay_image')
        overlay_x = int(request.form.get('overlay_x', 0))
        overlay_y = int(request.form.get('overlay_y', 0))
        overlay_width = int(request.form.get('overlay_width', 100))
        overlay_height = int(request.form.get('overlay_height', 100))

        # Bild öffnen
        image = Image.open(file).convert("RGBA")
        draw = ImageDraw.Draw(image)
        max_font_size, font_size = 100, 100

        # Dynamische Schriftgrößenanpassung
        while font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if text_width <= text_field_width and text_height <= text_field_height:
                break
            font_size -= 1

        if font_size == 0:
            logging.error("Text passt nicht in das vorgesehene Feld.")
            return jsonify({'error': 'Text passt nicht in das vorgesehene Feld.'}), 400

        # Zentrierte Position berechnen
        x_offset = text_field_x + (text_field_width - text_width) // 2
        y_offset = text_field_y + (text_field_height - text_height) // 2

        # Text auf das Bild zeichnen
        draw.text((x_offset, y_offset), text, fill=font_color, font=font)
        logging.info(f"Text gezeichnet: '{text}' mit Schriftart {font_name} auf Position ({x_offset}, {y_offset})")

        # **NEU: Overlay hinzufügen**
        if overlay_file:
            overlay = Image.open(overlay_file).convert("RGBA")
            overlay = overlay.resize((overlay_width, overlay_height))
            image.paste(overlay, (overlay_x, overlay_y), overlay)
            logging.info(f"Overlay hinzugefügt auf Position ({overlay_x}, {overlay_y}) mit Größe {overlay_width}x{overlay_height}")

        # Bild speichern und senden
        output_path = 'output_image.png'
        image.save(output_path, format='PNG')
        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        logging.error(f"Fehler bei der Bildverarbeitung: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
