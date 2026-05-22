import subprocess
import json

def get_process_commandlines():
    cmd = 'powershell -Command "Get-CimInstance Win32_Process | select ProcessId, Name, CommandLine | ConvertTo-Json -Compress"'
    try:
        out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        data = json.loads(out)
        target_pids = {9152, 4840, 11160, 20228}
        
        # In case ConvertTo-Json returns a single dict instead of a list when there's only 1 item (though here there are many)
        if isinstance(data, dict):
            data = [data]
            
        for item in data:
            pid = item.get('ProcessId')
            if pid in target_pids:
                print(f"PID: {pid}")
                print(f"Name: {item.get('Name')}")
                print(f"CommandLine: {item.get('CommandLine')}")
                print("-" * 50)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    get_process_commandlines()
