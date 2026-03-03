from PIL import Image
import numpy as np

def flawless_logo_extraction():
    input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772546535643.jpg'
    output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
    
    img = Image.open(input_path).convert('RGB')
    data = np.array(img).astype(float)
    
    R = data[:, :, 0]
    G = data[:, :, 1]
    B = data[:, :, 2]
    
    # 1. Calculate Alpha strictly using the Blue channel.
    # Foreground Blue is ~35. Background Blue is >200.
    # We define B < 40 as solid foreground (alpha=255)
    # We define B > 160 as solid background (alpha=0)
    # Between 40 and 160 is the antialiased edge.
    
    alpha = 255 - ((B - 40) * (255.0 / (160.0 - 40.0)))
    alpha = np.clip(alpha, 0, 255)
    
    # 2. Reconstruct the pure Foreground color on the edges to eliminate any "halo"
    # To do this, we undo the white/grey addition.
    # The mixed pixel C = alpha*F + (1-alpha)*Bg.
    # We know the Background is roughly grey R=G=B=Bg.
    # We can guess Bg from the local neighborhood, or just assume Bg = B / (1 - alpha) if alpha < 1.
    # Wait, simpler: if it's an edge (alpha between 0 and 255), we force the pixel to either pure Orange or pure Brown.
    # How to know if an edge belongs to Orange or Brown? Compare R and G!
    # Orange has R > 200, G > 100. Brown has R < 60, G < 50.
    # Even mixed with white(255), Orange has much higher R relative to G.
    
    out_img = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            r, g, b = data[y, x]
            a = alpha[y, x]
            
            if a == 0:
                # Background
                out_img[y, x] = [0, 0, 0, 0]
                continue
            
            if a < 250:
                # It's an edge. Let's force it to the nearest Foreground color
                # If R > G + 20 AND R is generally high, it's the Orange mountain.
                if r - g > 30:
                    out_r, out_g, out_b = 227, 116, 36  # Pure Orange
                else:
                    out_r, out_g, out_b = 43, 35, 32    # Pure Dark Brown
            else:
                out_r, out_g, out_b = r, g, b
                
            out_img[y, x] = [int(out_r), int(out_g), int(out_b), int(a)]
            
    img_out = Image.fromarray(out_img, 'RGBA')
    
    box = img_out.getbbox()
    if box:
        img_out = img_out.crop(box)
    
    img_out.save(output_path)
    print("Flawless extraction done.")

if __name__ == '__main__':
    flawless_logo_extraction()
