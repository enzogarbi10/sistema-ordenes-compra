from PIL import Image
import numpy as np

def process_logo():
    img_path = r"C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772551588755.png"
    out_path = r"c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png"
    
    img = Image.open(img_path).convert('RGBA')
    data = np.array(img).astype(float)
    
    r = data[:,:,0]
    g = data[:,:,1]
    b = data[:,:,2]
    
    # Measure distance from white
    dist = (255 - r) + (255 - g) + (255 - b)
    
    # Mapping distance to alpha.
    # We want dist=0 to be alpha=0.
    # dist=80 to be alpha=255.
    alpha = dist * (255.0 / 80.0) 
    alpha = np.clip(alpha, 0, 255)
    
    # Store new alpha
    data[:,:,3] = alpha
    
    # Unmultiply the white background to remove the halo
    a_norm = alpha / 255.0
    # Avoid zero division
    a_norm_safe = a_norm.copy()
    a_norm_safe[a_norm_safe == 0] = 1.0
    
    r_fg = (r / 255.0 - (1.0 - a_norm_safe)) / a_norm_safe * 255.0
    g_fg = (g / 255.0 - (1.0 - a_norm_safe)) / a_norm_safe * 255.0
    b_fg = (b / 255.0 - (1.0 - a_norm_safe)) / a_norm_safe * 255.0
    
    data[:,:,0] = np.clip(r_fg, 0, 255)
    data[:,:,1] = np.clip(g_fg, 0, 255)
    data[:,:,2] = np.clip(b_fg, 0, 255)
    
    out = Image.fromarray(data.astype(np.uint8), 'RGBA')
    
    # Try cropping top and bottom a bit to remove pure empty space
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
        
    out.save(out_path)
    print("Logo processed and saved.")

if __name__ == '__main__':
    process_logo()
