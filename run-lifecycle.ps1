# run.bat 用：启动 docserver-sync 并在脚本退出/中断时结束整棵进程树。
param(
  [Parameter(Mandatory)][string]$PidFile,
  [Parameter(Mandatory)][string]$CommandLine
)

function Stop-SyncTree([int]$ProcessId) {
  if ($ProcessId -le 0) { return }
  $alive = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if (-not $alive) { return }
  & taskkill.exe /PID $ProcessId /T /F 2>$null | Out-Null
}

if (Test-Path -LiteralPath $PidFile) {
  $oldText = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($oldText -match '^\d+$') {
    $oldId = [int]$oldText
    Write-Host "停止上次未退出的 docserver-sync (PID $oldId)…"
    Stop-SyncTree $oldId
  }
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$proc = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $CommandLine -PassThru -NoNewWindow
if (-not $proc) {
  Write-Error '无法启动 docserver-sync'
  exit 1
}

Set-Content -LiteralPath $PidFile -Value $proc.Id -NoNewline

try {
  $proc.WaitForExit()
  exit $proc.ExitCode
}
finally {
  Stop-SyncTree $proc.Id
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}
