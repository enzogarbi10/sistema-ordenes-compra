from rembg import remove, new_session
from PIL import Image
import traceback

input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772546535643.jpg'
output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'

try:
    session = new_session('u2net')
    img = Image.open(input_path)
    # Using alpha matting to fix the dirty edges and shadow
    output_img = remove(
        img, 
        session=session, 
        alpha_matting=True, 
        alpha_matting_foreground_threshold=240, 
        alpha_matting_background_threshold=10, 
        alpha_matting_erode_size=10
    )
    
    # Let's crop the transparent padding
    box = output_img.getbbox()
    if box:
        output_img = output_img.crop(box)
    
    output_img.save(output_path)
    print("Done rembg with matting and cropping.")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
