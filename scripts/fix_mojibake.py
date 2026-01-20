import os
import glob

TEMPLATE_DIR = r"c:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra\ordenes_trabajo\templates"

def fix_mojibake():
    files = glob.glob(os.path.join(TEMPLATE_DIR, '**', '*.html'), recursive=True)
    count = 0
    
    for filepath in files:
        try:
            # Read as UTF-8 (it IS valid UTF-8 now, but with wrong chars)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # The "Mojibake" heuristic: 
            # These characters "Ã“" are actually bytes 0xC3 0x93 interpreted as CP1252 chars.
            # We want to get back the bytes 0xC3 0x93 and treat them as UTF-8.
            
            # We assume the content was Latin-1 (or CP1252) erroneously converted to UTF-8
            # So we reverse it: encode to latin1 => get raw bytes => decode as utf-8
            
            fixed_content = content.encode('cp1252').decode('utf-8')
            
            # Write back the corrected content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
                
            print(f"Repaired: {os.path.basename(filepath)}")
            count += 1
        except UnicodeEncodeError:
            # If encoding to cp1252 fails, it means there are chars that don't belong to the mojibake set
            # This might be already correct or mixed content. 
            print(f"Skipping {os.path.basename(filepath)} (Could not reverse-encode)")
        except UnicodeDecodeError:
             print(f"Skipping {os.path.basename(filepath)} (Bytes not valid UTF-8 after reverse)")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print(f"Finished. Repaired {count} files.")

if __name__ == "__main__":
    fix_mojibake()
