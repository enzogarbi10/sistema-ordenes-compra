import subprocess
import json

def get_detailed_process_info():
    cmd = 'powershell -Command "Get-CimInstance Win32_Process | select ProcessId, ParentProcessId, Name, CommandLine, ExecutablePath, CreationDate | ConvertTo-Json -Compress"'
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        data = json.loads(out)
        target_pids = {9152, 4840, 11160, 20228}
        
        if isinstance(data, dict):
            data = [data]
            
        for item in data:
            pid = item.get('ProcessId')
            if pid in target_pids:
                print(f"PID: {pid}")
                print(f"Parent PID: {item.get('ParentProcessId')}")
                print(f"Name: {item.get('Name')}")
                print(f"CommandLine: {item.get('CommandLine')}")
                print(f"ExecutablePath: {item.get('ExecutablePath')}")
                print(f"CreationDate: {item.get('CreationDate')}")
                print("-" * 50)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    get_detailed_process_info()
