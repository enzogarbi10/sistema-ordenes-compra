import cv2
import numpy as np
import urllib.request
import os

def process_logo():
    input_path = r'C:\Users\ENZO\.gemini\antigravity\brain\7b06308a-7201-4cf0-8fdf-fcdf4eb3d55b\media__1772546535643.jpg'
    output_path = r'c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\static\img\logo.png'
    
    # We might need to install opencv-python if not present
    try:
        import cv2
    except ImportError:
        import subprocess
        subprocess.check_call(["py", "-m", "pip", "install", "opencv-python", "numpy"])
        import cv2
        
    img = cv2.imread(input_path)
    if img is None:
        print("Could not read image")
        return
        
    # Convert to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # We want to remove the checkerboard. The checkerboard is usually white (255,255,255) and light grey (e.g. 204,204,204 or 230,230,230)
    # Let's create a mask of anything that is NOT light (since the logo is dark brown and orange)
    # Orange is around (227, 116, 36)
    # Background is mostly > 200 in all channels, except grey might be around 200.
    # Orange has high Red (227), but lower Green and Blue.
    # So if R, G, B are all > 180, it's likely background.
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Background mask: low saturation AND high value
    # White/Grey have very low saturation (< 30) and high value (> 180)
    lower_bg = np.array([0, 0, 180])
    upper_bg = np.array([180, 40, 255])
    
    bg_mask = cv2.inRange(hsv, lower_bg, upper_bg)
    
    # The logo is the inverse of the background
    fg_mask = cv2.bitwise_not(bg_mask)
    
    # To fix the edges, we can do some morphological operations or grabcut
    # Let's try GrabCut for a cleaner edge
    mask = np.zeros(img.shape[:2], np.uint8)
    
    # bg_mask > 0 becomes cv2.GC_BGD (0) or cv2.GC_PR_BGD (2)
    # fg_mask > 0 becomes cv2.GC_FGD (1) or cv2.GC_PR_FGD (3)
    
    # Let's initialize mask: 
    # definitely background where bg_mask is solid
    mask[bg_mask > 0] = cv2.GC_PR_BGD
    mask[bg_mask > 240] = cv2.GC_BGD  # Try to be sure
    
    mask[fg_mask > 0] = cv2.GC_PR_FGD
    
    # Erode fg_mask to get sure foreground
    kernel = np.ones((3,3), np.uint8)
    sure_fg = cv2.erode(fg_mask, kernel, iterations=2)
    mask[sure_fg > 0] = cv2.GC_FGD
    
    bgdModel = np.zeros((1,65), np.float64)
    fgdModel = np.zeros((1,65), np.float64)
    
    rect = (10, 10, img.shape[1]-20, img.shape[0]-20)
    
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
    
    mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
    
    # Add alpha channel
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_rgba[:, :, 3] = mask2 * 255
    
    # Now, the edges might still be a bit harsh or have grey halos.
    # Let's try to remove any grey-ish pixels from the edges by feathering or filtering
    
    # Let's crop to bounding box
    coords = cv2.findNonZero(mask2)
    x, y, w, h = cv2.boundingRect(coords)
    cropped = img_rgba[y:y+h, x:x+w]
    
    cv2.imwrite(output_path, cropped)
    print("GrabCut completed.")

if __name__ == '__main__':
    process_logo()
