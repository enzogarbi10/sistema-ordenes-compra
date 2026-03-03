from PIL import Image, ImageFilter
import numpy as np

def render_black_bg_logo():
    input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772546535643.jpg'
    output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
    
    img = Image.open(input_path).convert('RGB')
    data = np.array(img).astype(float)
    
    # We will blend to black #000000
    out_img = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    
    # Logo colors:
    # Text/Dark mountain: ~40, 30, 30
    # Orange: ~230, 115, 35
    # The checkerboard is white(255) and grey(~204)
    # The B channel of the logo is almost 0 (<= 40 everywhere)
    # The B channel of the background is >= 150
    # So we can calculate the alpha of the FOREGROUND simply by comparing B channel to the grey background!
    
    # But wait, there's a drop shadow in the original logo! 
    # Drop shadow has B channel roughly equal to R and G, but darker than 204.
    # To keep the shadow, we can just replace the checkerboard pattern with pure black.
    
    # Let's try to just make the grey/white become black transparently.
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            r, g, b = data[y, x]
            
            # Simple heuristic: if it's very bright (B > 150), it's background. Background becomes black.
            # We want to interpolate correctly. But since it's on a black navbar, we don't even need transparency!
            # We can literally just output an image with a black background!
            
            # Distance from grey: max(r,g,b) - min(r,g,b)
            chroma = max(r,g,b) - min(r,g,b)
            
            # If it's fairly desaturated AND bright, it's the checkerboard.
            if chroma < 40 and min(r,g,b) > 120:
                # Replace checkerboard with Black
                # But we want to preserve shadows: darker greys should become darker black?
                # Actually, if we just set it to transparent, and use the chroma key...
                r, g, b, a = 0, 0, 0, 0
            else:
                # Foreground pixel
                # If it's a mixed edge pixel (e.g., halfway between orange and white)
                # It will have B ~ 100, R ~ 240, G ~ 180
                # We can subtract the white component.
                if b > 50 and chroma > 40:
                    # Remove the white/grey addition
                    factor = (255 - b) / 205.0
                    factor = max(0, min(1, factor))
                    # Edge towards orange
                    r = int(227 + (r - 227) * factor)
                    g = int(116 + (g - 116) * factor)
                    b = int(36 + (b - 36) * factor)
                a = 255
                
            out_img[y, x] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), a]
            
    img_out = Image.fromarray(out_img)
    # Smooth the edges slightly
    # img_out = img_out.filter(ImageFilter.SMOOTH_MORE)
    
    box = img_out.getbbox()
    if box:
        img_out = img_out.crop(box)
    
    img_out.save(output_path)
    print("Rendered and saved.")

if __name__ == '__main__':
    render_black_bg_logo()
