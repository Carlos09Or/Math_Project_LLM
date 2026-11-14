# smoke_offline.ps1 - Prueba de humo SIN RED (criterio 5 del Hito 1)
#
# Que hace:
#   1. Registra el estado de red ANTES (adaptadores + prueba de conexion a internet).
#   2. Si todavia hay internet, se detiene (a menos que uses -AllowOnline).
#   3. Comprueba que el servidor de Ollama local (puerto 11435) responde.
#   4. Corre los 9 items con run_experiment.py.
#   5. Registra el estado de red DESPUES y guarda todo en runs\<fecha>_network_state.json.
#
# NO cambia ninguna configuracion de red: tu apagas y enciendes el Wi-Fi.
# Uso:  powershell -ExecutionPolicy Bypass -File scripts\smoke_offline.ps1
#       (-CheckOnly solo muestra el estado de red y sale; -AllowOnline permite correr con internet)
param(
    [switch]$AllowOnline,
    [switch]$CheckOnly,
    [string]$Model = 'qwen3:0.6b-q4_K_M',
    [string]$HostUrl = 'http://127.0.0.1:11435'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONIOENCODING = 'utf-8'

function Test-Tcp([string]$ip, [int]$port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $c.BeginConnect($ip, $port, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne(3000, $false) -and $c.Connected) { $c.EndConnect($iar); return $true }
        return $false
    } catch { return $false } finally { $c.Close() }
}

function Get-NetState {
    $ad = @(Get-NetAdapter | ForEach-Object { @{ name = $_.Name; description = $_.InterfaceDescription; status = [string]$_.Status } })
    return [ordered]@{
        taken_utc         = (Get-Date).ToUniversalTime().ToString('o')
        adapters          = $ad
        probe_1_1_1_1_443 = (Test-Tcp '1.1.1.1' 443)
        probe_8_8_8_8_53  = (Test-Tcp '8.8.8.8' 53)
    }
}

function Show-NetState($s, $title) {
    Write-Host "--- $title"
    foreach ($a in $s.adapters) { Write-Host ("  {0,-12} {1}" -f $a.name, $a.status) }
    Write-Host ("  Conexion a internet (1.1.1.1:443): {0} | (8.8.8.8:53): {1}" -f $s.probe_1_1_1_1_443, $s.probe_8_8_8_8_53)
}

$before = Get-NetState
Show-NetState $before 'Estado de red ANTES'
$online = ($before.probe_1_1_1_1_443 -or $before.probe_8_8_8_8_53)

if ($CheckOnly) {
    if ($online) { Write-Host 'Hay internet. Para la prueba sin red, apaga el Wi-Fi (o modo avion) y vuelve a ejecutar.' }
    else { Write-Host 'Sin internet detectado: listo para la prueba sin red.' }
    exit 0
}
if ($online -and -not $AllowOnline) {
    Write-Host ''
    Write-Host 'ABORTADO: todavia hay internet. Apaga el Wi-Fi (o activa el modo avion) y ejecuta de nuevo.'
    exit 2
}

try { $ver = (Invoke-RestMethod "$HostUrl/api/version" -TimeoutSec 5).version }
catch {
    Write-Host "ABORTADO: no responde el servidor de Ollama en $HostUrl. Abre la ventana del servidor (ollama serve con OLLAMA_HOST=127.0.0.1:11435)."
    exit 3
}
Write-Host "Servidor Ollama $ver en $HostUrl"
try {
    $loaded = @((Invoke-RestMethod "$HostUrl/api/ps" -TimeoutSec 5).models | ForEach-Object { $_.name })
    $others = @($loaded | Where-Object { $_ -ne $Model })
    if ($others.Count -gt 0) { Write-Host ('AVISO: hay otros modelos cargados en este servidor: ' + ($others -join ', ')) }
} catch { }
nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader

Write-Host ''
Write-Host "Ejecutando los 9 items con $Model ..."
& python src/run_experiment.py --model $Model --host $HostUrl
$code = $LASTEXITCODE

$after = Get-NetState
Show-NetState $after 'Estado de red DESPUES'

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$evidence = [ordered]@{
    purpose          = 'criterio 5 del Hito 1: ejecucion sin red'
    model            = $Model
    host             = $HostUrl
    allow_online     = [bool]$AllowOnline
    offline_before   = (-not $online)
    offline_after    = (-not ($after.probe_1_1_1_1_443 -or $after.probe_8_8_8_8_53))
    runner_exit_code = $code
    before           = $before
    after            = $after
}
$path = Join-Path $root "runs\${stamp}_network_state.json"
if (Test-Path $path) { Write-Host "No se sobrescribe $path"; exit 4 }
[System.IO.File]::WriteAllText($path, ($evidence | ConvertTo-Json -Depth 6), (New-Object System.Text.UTF8Encoding($false)))
Write-Host ''
Write-Host "Evidencia de red guardada en: $path"
if ($code -eq 0 -and $evidence.offline_before -and $evidence.offline_after) {
    Write-Host 'RESULTADO: la corrida termino sin errores y sin internet antes ni despues.'
} else {
    Write-Host "RESULTADO: revisa la salida (codigo del runner: $code)."
}
Write-Host 'Ahora puedes volver a encender el Wi-Fi.'
exit $code
