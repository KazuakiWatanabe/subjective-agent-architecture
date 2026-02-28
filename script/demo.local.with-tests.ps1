# ============================================================
# demo.local.with-tests.ps1（Docker起動 + テスト自動実行 + 証拠ログ保存 + デモプリセット）
# ============================================================
# 目的:
#   - docker compose で API を起動 → test コンテナで pytest 実行（E2E含む）
#   - pytest のログを test\evidence\ に自動保存（社内デモ用の“証拠”）
#   - テスト完了後に app をバックグラウンド起動し直し、プリセット入力で /convert を複数実行
#
# 使い方（推奨: repo 直下から）:
#   powershell -ExecutionPolicy Bypass -File .\script\demo.local.with-tests.ps1
#
# 停止:
#   docker compose -f <repo>\docker-compose.local.with-tests.yml down
#
# 前提:
#   - Docker Desktop 起動済み
#   - リポジトリ直下に Dockerfile.local が存在（pytest を含むこと）
#   - API が http://localhost:8080 で待ち受けること

$ErrorActionPreference = "Stop"

# ------------------------------
# Repo Root を自動検出（script の親を repo root）
# ------------------------------
$RepoRoot = Split-Path -Parent $PSScriptRoot
Write-Host "== Repo Root ==" -ForegroundColor Cyan
Write-Host $RepoRoot

# ------------------------------
# 証拠ログ保存先
# ------------------------------
$EvidenceDir = Join-Path $RepoRoot "test\evidence"
if (!(Test-Path $EvidenceDir)) {
  New-Item -ItemType Directory -Path $EvidenceDir | Out-Null
}

$Ts = Get-Date -Format "yyyyMMdd-HHmmss"
$PytestLogPath = Join-Path $EvidenceDir ("pytest.local." + $Ts + ".log")

# ------------------------------
# Compose ファイル（with tests）を生成
# ------------------------------
$ComposePath = Join-Path $RepoRoot "docker-compose.local.with-tests.yml"

$compose = @"
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.local
    ports:
      - "8080:8080"
    environment:
      - PYTHONPATH=/app/src
    volumes:
      - ./:/app

  test:
    build:
      context: .
      dockerfile: Dockerfile.local
    depends_on:
      - app
    environment:
      - PYTHONPATH=/app/src
      - DEMO_URL=http://app:8080
    # PATH 依存を避けるため python -m pytest
    command: ["python", "-m", "pytest", "-v"]
    volumes:
      - ./:/app
"@

Set-Content -Path $ComposePath -Value $compose -Encoding UTF8

Write-Host "`n== Compose file written ==" -ForegroundColor Cyan
Write-Host $ComposePath

# ------------------------------
# 1) テスト実行（test完了で停止）
# ------------------------------
Write-Host "`n== 1) Docker Compose 起動（build含む / test完了で停止） ==" -ForegroundColor Cyan
docker compose -f "$ComposePath" up --build --abort-on-container-exit --exit-code-from test

# ------------------------------
# 1.5) pytest ログを保存（証拠化）
# ------------------------------
Write-Host "`n== 1.5) pytestログ保存（証拠化） ==" -ForegroundColor Cyan
Write-Host $PytestLogPath
# コンテナは停止済みでも logs は取得できます
docker compose -f "$ComposePath" logs test --no-color | Out-File -FilePath $PytestLogPath -Encoding utf8

# ------------------------------
# 2) app をデモ用に起動（バックグラウンド）
# ------------------------------
Write-Host "`n== 2) テスト完了。app をデモ用に起動（バックグラウンド） ==" -ForegroundColor Cyan
docker compose -f "$ComposePath" up --build -d app

Start-Sleep -Seconds 3

# ------------------------------
# 3) Health チェック
# ------------------------------
Write-Host "`n== 3) Health Check ==" -ForegroundColor Cyan
curl.exe http://localhost:8080/health

# ------------------------------
# 4) /convert デモ（社内で刺さる題材プリセット）
# ------------------------------
Write-Host "`n== 4) /convert デモ（プリセット） ==" -ForegroundColor Cyan

$presets = @(
  @{
    label = "CS/チャーン: 来店減少×限定感"
    text  = "最近来店が減っている。値引きには反応しないが、限定感には反応する。"
  },
  @{
    label = "販促: LINE配信の反応が鈍い"
    text  = "LINE配信の開封率が落ちている。クーポンは飽きられているが、会員ランク特典には反応がある。"
  },
  @{
    label = "CS: 解約理由（費用対効果）"
    text  = "店舗から『費用対効果が見えない』と言われている。利用は続けたいが、成果の説明が欲しい。"
  },
  @{
    label = "現場: オペレーション負荷（配信作業が面倒）"
    text  = "配信作業が面倒で継続できない。現場は忙しく、文章を考える時間がない。テンプレ化したい。"
  },
  @{
    label = "新規: 初回定着（オンボーディング）"
    text  = "導入したが何をすれば効果が出るか分からず放置されがち。最初の一手と継続の型が欲しい。"
  }
)

foreach ($p in $presets) {
  Write-Host "`n---" -ForegroundColor DarkGray
  Write-Host ("[Preset] " + $p.label) -ForegroundColor Yellow
  Write-Host ("Input: " + $p.text)

  $body = @{ text = $p.text } | ConvertTo-Json -Compress

  $res = curl.exe -s -X POST http://localhost:8080/convert `
    -H "Content-Type: application/json" `
    -d $body

  Write-Host "Output:" -ForegroundColor Green
  Write-Host $res
}

# ------------------------------
# 5) 失敗ケース確認（空入力 400）
# ------------------------------
Write-Host "`n== 5) 空入力（400確認） ==" -ForegroundColor Cyan
$bad = @{ text = "" } | ConvertTo-Json -Compress

curl.exe -i -X POST http://localhost:8080/convert `
  -H "Content-Type: application/json" `
  -d $bad

# ------------------------------
# 終了方法
# ------------------------------
Write-Host "`n== 証拠ログ ==" -ForegroundColor Cyan
Write-Host ("pytest log: " + $PytestLogPath)

Write-Host "`n== 終了する場合 ==" -ForegroundColor Cyan
Write-Host "docker compose -f `"$ComposePath`" down"
