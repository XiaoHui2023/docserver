# run.bat helper: start docserver-sync, stop stale instances, and keep the
# launched process tree inside a Windows Job that is killed when this script exits.
param(
  [Parameter(Mandatory)][string]$PidFile,
  [Parameter(Mandatory)][string]$CommandLine
)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class DocserverJobObject {
  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
    public long PerProcessUserTimeLimit;
    public long PerJobUserTimeLimit;
    public uint LimitFlags;
    public UIntPtr MinimumWorkingSetSize;
    public UIntPtr MaximumWorkingSetSize;
    public uint ActiveProcessLimit;
    public IntPtr Affinity;
    public uint PriorityClass;
    public uint SchedulingClass;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct IO_COUNTERS {
    public ulong ReadOperationCount;
    public ulong WriteOperationCount;
    public ulong OtherOperationCount;
    public ulong ReadTransferCount;
    public ulong WriteTransferCount;
    public ulong OtherTransferCount;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
    public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
    public IO_COUNTERS IoInfo;
    public UIntPtr ProcessMemoryLimit;
    public UIntPtr JobMemoryLimit;
    public UIntPtr PeakProcessMemoryUsed;
    public UIntPtr PeakJobMemoryUsed;
  }

  private const int JobObjectExtendedLimitInformation = 9;
  private const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;

  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
  private static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

  [DllImport("kernel32.dll", SetLastError = true)]
  private static extern bool SetInformationJobObject(
    IntPtr hJob,
    int jobObjectInfoClass,
    IntPtr lpJobObjectInfo,
    uint cbJobObjectInfoLength
  );

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool CloseHandle(IntPtr hObject);

  public static IntPtr CreateKillOnCloseJob() {
    IntPtr job = CreateJobObject(IntPtr.Zero, null);
    if (job == IntPtr.Zero) {
      throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
    }

    JOBOBJECT_EXTENDED_LIMIT_INFORMATION info = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    int length = Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION));
    IntPtr ptr = Marshal.AllocHGlobal(length);
    try {
      Marshal.StructureToPtr(info, ptr, false);
      if (!SetInformationJobObject(job, JobObjectExtendedLimitInformation, ptr, (uint)length)) {
        throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
      }
      return job;
    }
    finally {
      Marshal.FreeHGlobal(ptr);
    }
  }
}
'@

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
    Write-Host "Stopping previous docserver-sync (PID $oldId)..."
    Stop-SyncTree $oldId
  }
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$job = [DocserverJobObject]::CreateKillOnCloseJob()
$proc = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $CommandLine -PassThru -NoNewWindow
if (-not $proc) {
  [DocserverJobObject]::CloseHandle($job) | Out-Null
  Write-Error 'Unable to start docserver-sync'
  exit 1
}
if (-not [DocserverJobObject]::AssignProcessToJobObject($job, $proc.Handle)) {
  Write-Warning 'Unable to assign docserver-sync to Windows Job; falling back to taskkill cleanup on exit.'
}

Set-Content -LiteralPath $PidFile -Value $proc.Id -NoNewline

try {
  $proc.WaitForExit()
  exit $proc.ExitCode
}
finally {
  Stop-SyncTree $proc.Id
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
  [DocserverJobObject]::CloseHandle($job) | Out-Null
}
