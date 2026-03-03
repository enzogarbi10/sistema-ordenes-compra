from PIL import Image

output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
try:
    img = Image.open(output_path)
    box = img.getbbox()
    if box:
        cropped_img = img.crop(box)
        cropped_img.save(output_path)
        print("Cropped successfully")
    else:
        print("No bounding box found")
except Exception as e:
    print(f"Error: {e}")
