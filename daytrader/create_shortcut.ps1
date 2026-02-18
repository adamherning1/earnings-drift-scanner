$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Day Trading Dashboard.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c cd /d C:\Users\adamh\.openclaw\workspace\daytrader && python app.py && pause"
$Shortcut.WorkingDirectory = "C:\Users\adamh\.openclaw\workspace\daytrader"
$Shortcut.Save()
Write-Host "Desktop shortcut created!"
