from PIL import Image
import numpy as np

def clean_logo():
    input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772546535643.jpg'
    output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
    
    img = Image.open(input_path).convert('RGB')
    data = np.array(img).astype(float)
    
    # We will build an alpha channel and a new color image for the foreground.
    # We use distance to background color to determine alpha.
    
    # Identify background: pixels where max(R,G,B) is high and min(R,G,B) is high, 
    # and difference between channels is small.
    R = data[:, :, 0]
    G = data[:, :, 1]
    B = data[:, :, 2]
    
    # Calculate "greyness" of the background.
    max_c = np.max(data, axis=2)
    min_c = np.min(data, axis=2)
    diff = max_c - min_c
    
    # Background is roughly when B > 150 and diff < 30 (grey/white)
    # The logo has small B (orange has B~36, brown has B~32).
    # Except the text might have some dark grey that we want to keep.
    
    # Let's estimate alpha from the Blue channel
    # Let's assume baseline B background is around 204 (grey squares) or 255 (white squares)
    # We can smooth the background by applying a median filter or just estimating locally.
    # Actually, B channel directly relates to alpha because foreground B is ~35.
    
    # alpha = (Bg - B_pixel) / (Bg - 35)
    # To be safe, we estimate Bg pixel-wise by looking at the neighborhood, but it's a checkerboard.
    # Just setting alpha = max(0, min(1, (240 - B) / 200 )) might work roughly.
    
    # A better approach: The text is almost black, the "M" is dark brown, the mountain part is orange.
    # If we just change all near-white/grey to transparent.
    # Let's try to remove anything where R, G, B > 180 and difference between them is < 20.
    
    # Let's do a proper chroma keying:
    # We will compute the color distance from white and from the grey checkerboard color.
    # Checkerboard colors are typically: 255,255,255 and roughly 204,204,204.
    
    # Create output image
    out_img = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            r, g, b = data[y, x]
            
            # Check if it's very bright and grey
            if min(r, g, b) > 170 and max(r,g,b) - min(r,g,b) < 30:
                # Fully transparent background
                alpha = 0
            else:
                # If it's somewhat greyish but darker, maybe an edge.
                if max(r,g,b) - min(r,g,b) < 30 and min(r,g,b) > 100:
                    # Edge transition to grey
                    alpha = max(0, min(255, int( (170 - min(r,g,b)) / 70.0 * 255 )))
                    if alpha < 0: alpha = 0
                else:
                    # It has color (orange) or is dark (text)
                    alpha = 255
                    
                # To remove the "halo", if alpha < 255, we should push the color towards the estimated foreground.
                # If it's orange-ish, make it pure orange. If dark, make it dark.
                if alpha > 0 and alpha < 255:
                    if r > g + 20: # Orange edge
                        r, g, b = 227, 116, 36
                    else: # Dark brown/text edge
                        r, g, b = 43, 35, 32
            
            out_img[y, x] = [r, g, b, alpha]
            
    # Also we should probably crop it
    img_out = Image.fromarray(out_img)
    box = img_out.getbbox()
    if box:
        img_out = img_out.crop(box)
    
    img_out.save(output_path)
    print("Logo cleaned and saved.")

if __name__ == '__main__':
    clean_logo()
