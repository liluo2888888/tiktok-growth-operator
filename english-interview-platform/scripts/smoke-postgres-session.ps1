$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$root = Split-Path $scriptsDir -Parent
$runId = [guid]::NewGuid().ToString("N")
$pgTempRoot = Join-Path $env:TEMP ("english-interview-pg-smoke-" + $runId)
$sessionStdoutPath = Join-Path $pgTempRoot "session-service.stdout.log"
$sessionStderrPath = Join-Path $pgTempRoot "session-service.stderr.log"
$gatewayStdoutPath = Join-Path $pgTempRoot "api-gateway.stdout.log"
$gatewayStderrPath = Join-Path $pgTempRoot "api-gateway.stderr.log"
$pgPort = 55432
$sessionServicePort = 18082
$apiGatewayPort = 18080
$databaseName = "english_interview"
$databaseUser = "postgres"
$databaseURL = "host=localhost port=$pgPort user=$databaseUser dbname=$databaseName sslmode=disable"
$sessionServiceBaseURL = "http://localhost:$sessionServicePort"
$apiGatewayBaseURL = "http://localhost:$apiGatewayPort"
$pgContainerName = "english-interview-pg-smoke-$runId"

function Stop-PortProcess {
  param([int[]]$Ports)

  $connections = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
  if (-not $connections) {
    return
  }

  $connections |
    Select-Object -ExpandProperty OwningProcess |
    Sort-Object -Unique |
    ForEach-Object {
      Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
}

function Wait-HttpOk {
  param(
    [string]$Url,
    [int]$TimeoutSeconds = 20
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
      if ($response.StatusCode -eq 200) {
        return
      }
    } catch {
      Start-Sleep -Milliseconds 500
    }
  }

  throw "Timeout waiting for $Url"
}

function Wait-PostgresDockerReady {
  param(
    [string]$ContainerName,
    [int]$TimeoutSeconds = 60
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    docker exec $ContainerName pg_isready -U $databaseUser 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
      return
    }

    Start-Sleep -Milliseconds 500
  }

  throw "Timeout waiting for PostgreSQL container $ContainerName"
}

function Invoke-PostgresQuery {
  param(
    [string]$ContainerName,
    [string]$Query,
    [string]$Database = $databaseName
  )

  $output = docker exec $ContainerName psql -U $databaseUser -d $Database -t -A -v ON_ERROR_STOP=1 -c $Query
  if ($LASTEXITCODE -ne 0) {
    throw "psql query failed: $Query"
  }

  return $output
}

function Start-PostgresDocker {
  param(
    [string]$ContainerName,
    [int]$Port
  )

  Stop-PostgresDocker -ContainerName $ContainerName

  docker run -d --name $ContainerName `
    -e POSTGRES_USER=$databaseUser `
    -e POSTGRES_HOST_AUTH_METHOD=trust `
    -e POSTGRES_DB=$databaseName `
    -p "${Port}:5432" `
    postgres:16 | Out-Null

  if ($LASTEXITCODE -ne 0) {
    throw "docker run postgres:16 failed"
  }

  Wait-PostgresDockerReady -ContainerName $ContainerName
}

function Stop-PostgresDocker {
  param([string]$ContainerName)

  $previousPreference = $ErrorActionPreference
  $ErrorActionPreference = "SilentlyContinue"
  docker rm -f $ContainerName *> $null
  $ErrorActionPreference = $previousPreference
}

function Start-CmdScript {
  param(
    [string]$ScriptName,
    [hashtable]$ExtraEnv = @{},
    [string]$StdoutPath,
    [string]$StderrPath
  )

  $envBlock = @(
    "set ""GOROOT=C:\toolchains\go1.24.3-tar\go""",
    "set ""PATH=C:\toolchains\go1.24.3-tar\go\bin;%PATH%"""
  )

  foreach ($pair in $ExtraEnv.GetEnumerator()) {
    $envBlock += "set ""$($pair.Key)=$($pair.Value)"""
  }

  $fullCommand = ($envBlock + @("call .\$ScriptName")) -join " && "
  Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $fullCommand -WorkingDirectory $scriptsDir -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath -PassThru
}

$dockerExe = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerExe) {
  throw "docker is required for smoke-postgres-session.ps1"
}

Stop-PortProcess -Ports @($apiGatewayPort, $sessionServicePort, $pgPort)
Stop-PostgresDocker -ContainerName $pgContainerName

if (Test-Path $pgTempRoot) {
  Remove-Item $pgTempRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $pgTempRoot | Out-Null

$sessionProc = $null
$gatewayProc = $null

try {
  Start-PostgresDocker -ContainerName $pgContainerName -Port $pgPort

  $dbExists = (Invoke-PostgresQuery -ContainerName $pgContainerName -Database "postgres" -Query "SELECT 1 FROM pg_database WHERE datname = '$databaseName';").Trim()
  if ($dbExists -ne "1") {
    throw "Expected PostgreSQL database $databaseName to exist"
  }

  $sessionProc = Start-CmdScript -ScriptName "run-session-service.cmd" -ExtraEnv @{
    SESSION_REPOSITORY_BACKEND = "postgres"
    DATABASE_URL = $databaseURL
    PGSSLMODE = "disable"
    SESSION_SERVICE_ADDR = ":$sessionServicePort"
  } -StdoutPath $sessionStdoutPath -StderrPath $sessionStderrPath

  $gatewayProc = Start-CmdScript -ScriptName "run-api-gateway.cmd" -ExtraEnv @{
    API_GATEWAY_ADDR = ":$apiGatewayPort"
    SESSION_SERVICE_BASE_URL = $sessionServiceBaseURL
  } -StdoutPath $gatewayStdoutPath -StderrPath $gatewayStderrPath

  Wait-HttpOk -Url ($sessionServiceBaseURL + "/healthz")
  Wait-HttpOk -Url ($apiGatewayBaseURL + "/healthz")

  $bootstrapBody = @{
    roleId = "product"
    missionId = "behavioral"
  } | ConvertTo-Json -Compress

  $bootstrap = Invoke-RestMethod -Method Post -Uri ($apiGatewayBaseURL + "/v1/mobile/session/bootstrap") -ContentType "application/json" -Body $bootstrapBody

  $turnBody = @{
    answer = "I aligned product, design, and engineering with one execution cadence and recovered a delayed launch."
  } | ConvertTo-Json -Compress

  $null = Invoke-RestMethod -Method Post -Uri ($apiGatewayBaseURL + "/v1/mobile/sessions/" + $bootstrap.sessionId + "/turns") -ContentType "application/json" -Body $turnBody
  $detail = Invoke-RestMethod -Method Get -Uri ($apiGatewayBaseURL + "/v1/mobile/sessions/" + $bootstrap.sessionId)

  if (-not $detail.turns -or $detail.turns.Count -lt 3) {
    throw "Expected at least 3 turns after submit"
  }

  if (-not $detail.stage) {
    throw "Expected stage in session detail"
  }

  if (-not $detail.currentQuestion) {
    throw "Expected currentQuestion in session detail"
  }

  $row = Invoke-PostgresQuery -ContainerName $pgContainerName -Query "SELECT id || '|' || status || '|' || stage || '|' || current_question || '|' || jsonb_array_length(transcript) FROM interview_sessions WHERE id = '$($bootstrap.sessionId)';"
  $row = $row.Trim()
  if (-not $row) {
    throw "Expected persisted row in PostgreSQL"
  }

  $parts = $row -split "\|", 5
  if ($parts.Count -ne 5) {
    throw "Unexpected persisted row format: $row"
  }

  [pscustomobject]@{
    postgresRuntime = "docker"
    sessionId = $bootstrap.sessionId
    stage = $detail.stage
    currentQuestion = $detail.currentQuestion
    turnCount = $detail.turns.Count
    persistedSessionId = $parts[0]
    persistedStatus = $parts[1]
    persistedStage = $parts[2]
    persistedCurrentQuestion = $parts[3]
    persistedTurnCount = [int]$parts[4]
    databaseUrl = $databaseURL
  } | ConvertTo-Json -Depth 5
}
finally {
  if ($sessionProc -and -not $sessionProc.HasExited) {
    Stop-Process -Id $sessionProc.Id -Force -ErrorAction SilentlyContinue
  }

  if ($gatewayProc -and -not $gatewayProc.HasExited) {
    Stop-Process -Id $gatewayProc.Id -Force -ErrorAction SilentlyContinue
  }

  Stop-PostgresDocker -ContainerName $pgContainerName
}
