from rembg import remove
from PIL import Image

try:
    input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772545352335.jpg'
    output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
    input_img = Image.open(input_path)
    output_img = remove(input_img)
    output_img.save(output_path)
    print("Done")
except Exception as e:
    print(f"Error: {e}")
