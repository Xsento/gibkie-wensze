param(
    [switch]$InitDb,
    [switch]$Stop
)

$ErrorActionPreference = "Continue"
Set-Location -Path $PSScriptRoot

function Krok($tekst) { Write-Host "`n==> $tekst" -ForegroundColor Cyan }
function Blad($tekst) { Write-Host "BLAD: $tekst" -ForegroundColor Red; exit 1 }

Krok "Sprawdzam Dockera"
docker info *> $null
if ($LASTEXITCODE -ne 0) { Blad "Docker nie dziala. Uruchom Docker Desktop i sprobuj ponownie." }

if ($Stop) {
    Krok "Zatrzymuje kontenery"
    docker compose down
    exit $LASTEXITCODE
}

Krok "Buduje i uruchamiam kontenery (db + web) w tle"
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { Blad "docker compose up sie nie powiodl." }

Krok "Czekam, az PostgreSQL bedzie gotowy"
$gotowa = $false
for ($i = 1; $i -le 30; $i++) {
    docker compose exec -T db pg_isready -U gibki_wonsz -d tripforge_db *> $null
    if ($LASTEXITCODE -eq 0) { $gotowa = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $gotowa) { Blad "Baza nie odpowiada po 30 s. Sprawdz: docker compose logs db" }
Write-Host "Baza gotowa."

if ($InitDb) {
    Krok "Inicjalizuje baze (flask init-db) - UWAGA: usuwa istniejace dane"
    $haslo = Read-Host "Podaj haslo dla kont startowych (Enter = losowe)" -AsSecureString
    $jawne = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($haslo))
    if ($jawne) {
        $env:SEED_PASSWORD = $jawne
        docker compose exec -T -e SEED_PASSWORD web flask --app run init-db
        Remove-Item Env:SEED_PASSWORD
    } else {
        docker compose exec -T web flask --app run init-db
    }
    if ($LASTEXITCODE -ne 0) { Blad "init-db sie nie powiodl. Sprawdz: docker compose logs web" }
}

Krok "Czekam na aplikacje na http://localhost:5000"
$dziala = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        Invoke-WebRequest -Uri "http://localhost:5000/login" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop | Out-Null
        $dziala = $true; break
    } catch { Start-Sleep -Seconds 1 }
}
if (-not $dziala) { Blad "Aplikacja nie odpowiada. Sprawdz: docker compose logs web" }

Krok "Gotowe - otwieram przegladarke"
Write-Host "Konta: tomasz@tripforge.local, arkadiusz@tripforge.local, pawel@tripforge.local"
Write-Host "Zatrzymanie: powershell -ExecutionPolicy Bypass -File .\start.ps1 -Stop"
Start-Process "http://localhost:5000/login"
