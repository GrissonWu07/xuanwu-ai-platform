$serviceName = "XuanWuNearLinkBridge"
$displayName = "XuanWu NearLink Bridge"
$root = Split-Path -Parent $PSScriptRoot
$python = "python"
$script = Join-Path $root "service_wrapper.py"

New-Service -Name $serviceName -BinaryPathName "`"$python`" `"$script`"" -DisplayName $displayName -StartupType Automatic
Start-Service -Name $serviceName
