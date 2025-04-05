
import tkinter as tk
from tkinter import messagebox
import subprocess

def run_script():
    username = username_entry.get()
    if not username:
        messagebox.showerror("Input Error", "Please enter a username.")
        return

    script = f"""
$username = \"{username}\"
$profilePath = Join-Path -Path \"C:\\Users\" -ChildPath $username

if (Test-Path $profilePath) {{
    Rename-Item -Path $profilePath -NewName \"$username.old\" -Force
}} else {{
    Write-Error \"User profile path not found: $profilePath\"
    exit
}}

$profileRegPath = \"HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\"
$sidFound = $false

Get-ChildItem $profileRegPath | ForEach-Object {{
    $regSID = $_.PSChildName
    $regProfilePath = (Get-ItemProperty -Path $_.PsPath).ProfileImagePath

    if ($regProfilePath -like \"*\\$username\") {{
        $desktopPath = [Environment]::GetFolderPath(\"Desktop\")
        $regBackupPath = Join-Path $desktopPath \"$username-ProfileSID-Backup.reg\"
        $tempRegPath = \"$env:TEMP\\sidbackup.reg\"

        reg export \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\$regSID\" $regBackupPath /y
        reg export \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\$regSID\" $tempRegPath /y
        reg delete \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\$regSID\" /f
        reg import $tempRegPath

        (Get-Content $tempRegPath) -replace \"ProfileList\\\\$regSID\", \"ProfileList\\\\$regSID.old\" | Set-Content \"$env:TEMP\\sidbackup_old.reg\"
        reg import \"$env:TEMP\\sidbackup_old.reg\"

        Remove-Item $tempRegPath
        Remove-Item \"$env:TEMP\\sidbackup_old.reg\"

        $sidFound = $true
    }}
}}

if (-not $sidFound) {{
    Write-Warning \"No matching SID registry entry found for user: $username\"
}}

try {{
    Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope LocalMachine -Force
}} catch {{}}
"""

    command = ["powershell", "-Command", script]
    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", f"Profile for user '{username}' has been fixed.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Set up GUI
root = tk.Tk()
root.title("Windows User Profile Fixer")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Enter broken username:").grid(row=0, column=0, sticky="w")
username_entry = tk.Entry(frame, width=30)
username_entry.grid(row=1, column=0, pady=5)

run_button = tk.Button(frame, text="Fix Profile", command=run_script)
run_button.grid(row=2, column=0, pady=10)

root.mainloop()
