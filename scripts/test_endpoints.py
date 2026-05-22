import urllib.request
import urllib.error
import ssl

def test_endpoints():
    # Ignore SSL verification for testing
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    urls = [
        "http://localhost:8000",
        "https://localhost:8000",
        "http://localhost:8080",
        "https://localhost:8080",
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                print(f"  Status Code: {response.status}")
                print(f"  Headers: {dict(response.headers)}")
                body = response.read(100) # Read first 100 bytes
                print(f"  Body (first 100 bytes): {body}")
        except urllib.error.HTTPError as e:
            print(f"  HTTPError: {e.code} - {e.reason}")
            print(f"  Headers: {dict(e.headers)}")
        except Exception as e:
            print(f"  Exception: {type(e).__name__} - {e}")
        print("-" * 50)

if __name__ == '__main__':
    test_endpoints()
