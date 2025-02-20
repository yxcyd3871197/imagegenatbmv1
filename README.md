Example API Form-data Request: 
POST http://localhost:8080/process_image
Headers:
    x-api-key: IhrGeheimerAPIKey
    Content-Type: multipart/form-data
Body (form-data):
    image: (Deine Bilddatei, z. B. image.png)
    overlay_image: (Deine Overlay-Datei, z. B. overlay.png)
    text: Your Text Here
    font: RobotoSlab-Regular.ttf
    font_color: #000000
    font_size: 100  (Falls leer, wird Auto-Fit genutzt)
    text_field_x: 0
    text_field_y: 0
    text_field_width: 800
    text_field_height: 200
    text_field_border_color: #000000
    text_field_border_width: 5
    overlay_x: 100
    overlay_y: 100
    overlay_width: 200
    overlay_height: 200
    overlay_opacity: 200
    overlay_border_color: #FF0000
    overlay_border_thickness: 10
    overlay_corner_radius: 25

   cURL-Request
curl -X POST http://localhost:8080/process_image \
    -H "x-api-key: IhrGeheimerAPIKey" \
    -H "Content-Type: multipart/form-data" \
    -F "image=@image.png" \
    -F "overlay_image=@overlay.png" \
    -F "text=Your Text Here" \
    -F "font=RobotoSlab-Regular.ttf" \
    -F "font_color=#000000" \
    -F "font_size=100" \
    -F "text_field_x=0" \
    -F "text_field_y=0" \
    -F "text_field_width=800" \
    -F "text_field_height=200" \
    -F "text_field_border_color=#000000" \
    -F "text_field_border_width=5" \
    -F "overlay_x=100" \
    -F "overlay_y=100" \
    -F "overlay_width=200" \
    -F "overlay_height=200" \
    -F "overlay_opacity=200" \
    -F "overlay_border_color=#FF0000" \
    -F "overlay_border_thickness=10" \
    -F "overlay_corner_radius=25" \
    -o result.png

