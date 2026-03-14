$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

& "D:\AnaConda\python.exe" -m uvicorn webapp:app --host 127.0.0.1 --port 8000 --reload
