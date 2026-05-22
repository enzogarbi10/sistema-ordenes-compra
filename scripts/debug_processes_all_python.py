import subprocess
import json

def get_all_python_processes():
    cmd = 'powershell -Command "Get-CimInstance Win32_Process | select ProcessId, ParentProcessId, Name, CommandLine, ExecutablePath, CreationDate | ConvertTo-Json -Compress"'
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        data = json.loads(out)
        
        if isinstance(data, dict):
            data = [data]
            
        print("ALL PYTHON PROCESSES:")
        for item in data:
            name = item.get('Name', '').lower()
            if 'python' in name:
                print(f"PID: {item.get('ProcessId')}")
                print(f"Parent PID: {item.get('ParentProcessId')}")
                print(f"CommandLine: {item.get('CommandLine')}")
                print(f"ExecutablePath: {item.get('ExecutablePath')}")
                print(f"CreationDate: {item.get('CreationDate')}")
                print("-" * 50)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    get_all_python_processes()
