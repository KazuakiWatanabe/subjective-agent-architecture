# ================================================
# demo.local.ps1（修正版 / script 配下対応版）
# ================================================
# 目的:
#   script\demo.local.ps1 に配置しても
#   どこから実行しても docker-compose.local.yml を正しく参照できるようにする
#
# 使い方:
#   PowerShell で以下を実行
#   powershell -ExecutionPolicy Bypass -File .\script\demo.local.ps1
#
# 前提:
#   - Docker Desktop 起動済み
#   - リポジトリ直下に Dockerfile.local / docker-compose.local.yml が存在

$ErrorActionPreference = "Stop"

# ------------------------------
# リポジトリルートを自動検出
# ------------------------------
# script フォルダの親ディレクトリをルートとみなす
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "== Repo Root ==" -ForegroundColor Cyan
Write-Host $RepoRoot

# ------------------------------
# Docker 起動
# ------------------------------
Write-Host "`n== 1) Docker Compose 起動（build含む） ==" -ForegroundColor Cyan
docker compose -f "$RepoRoot\docker-compose.local.yml" up --build -d

Start-Sleep -Seconds 3

# ------------------------------
# Health チェック
# ------------------------------
Write-Host "`n== 2) Health Check ==" -ForegroundColor Cyan
curl.exe http://localhost:8080/health

# ------------------------------
# /convert デモ
# ------------------------------
Write-Host "`n== 3) /convert デモ ==" -ForegroundColor Cyan

$body = @{
    text = "最近来店が減っている。値引きには反応しないが、限定感には反応する。"
} | ConvertTo-Json -Compress

curl.exe -X POST http://localhost:8080/convert `
  -H "Content-Type: application/json" `
  -d $body

# ------------------------------
# 失敗ケース確認
# ------------------------------
Write-Host "`n== 4) 空入力（400確認） ==" -ForegroundColor Cyan

$bad = @{ text = "" } | ConvertTo-Json -Compress

try {
    curl.exe -i -X POST http://localhost:8080/convert `
      -H "Content-Type: application/json" `
      -d $bad
} catch {
    Write-Host "Expected: 400 Bad Request" -ForegroundColor Yellow
}

Write-Host "`n== 終了する場合 ==" -ForegroundColor Cyan
Write-Host "docker compose -f `"$RepoRoot\docker-compose.local.yml`" down"
