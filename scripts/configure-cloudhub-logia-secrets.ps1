param(
  [string]$AppId = "52e867b0-9d84-4cf9-b5bf-7b05c71ad7d7",
  [string]$TargetOrg = "hfs-dev",
  [string]$SupplierEmail = "",
  [string]$SenderEmail = "",
  [string]$SalesforceHost = "",
  [switch]$SkipSalesforceRefresh
)

$ErrorActionPreference = "Stop"

function Get-UserEnvValue {
  param([Parameter(Mandatory = $true)][string]$Name)
  $value = [Environment]::GetEnvironmentVariable($Name, "User")
  if ([string]::IsNullOrWhiteSpace($value)) {
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
  }
  if ([string]::IsNullOrWhiteSpace($value)) {
    $value = [Environment]::GetEnvironmentVariable($Name, "Machine")
  }
  return $value
}

function Set-UserEnvValue {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Value
  )
  [Environment]::SetEnvironmentVariable($Name, $Value, "User")
}

if (-not [string]::IsNullOrWhiteSpace($SupplierEmail)) {
  Set-UserEnvValue -Name "GMAIL_SUPPLIER_EMAIL" -Value $SupplierEmail
}

if (-not [string]::IsNullOrWhiteSpace($SenderEmail)) {
  Set-UserEnvValue -Name "GMAIL_SENDER_EMAIL" -Value $SenderEmail
}

if (-not $SkipSalesforceRefresh) {
  $sfJson = sf org display --target-org $TargetOrg --verbose --json | ConvertFrom-Json
  $sfAccessToken = $sfJson.result.accessToken
  if ([string]::IsNullOrWhiteSpace($sfAccessToken)) {
    throw "Salesforce CLI did not return an access token for $TargetOrg."
  }
  Set-UserEnvValue -Name "SALESFORCE_ACCESS_TOKEN" -Value $sfAccessToken

  if ([string]::IsNullOrWhiteSpace($SalesforceHost) -and -not [string]::IsNullOrWhiteSpace($sfJson.result.instanceUrl)) {
    $SalesforceHost = ([Uri]$sfJson.result.instanceUrl).Host
    Set-UserEnvValue -Name "SALESFORCE_HOST" -Value $SalesforceHost
  }
}

if ([string]::IsNullOrWhiteSpace($SalesforceHost)) {
  $SalesforceHost = Get-UserEnvValue -Name "SALESFORCE_HOST"
}

$values = [ordered]@{
  SALESFORCE_HOST = $SalesforceHost
  SALESFORCE_ACCESS_TOKEN = Get-UserEnvValue -Name "SALESFORCE_ACCESS_TOKEN"
  META_WHATSAPP_PHONE_NUMBER_ID = Get-UserEnvValue -Name "META_WHATSAPP_PHONE_NUMBER_ID"
  META_WHATSAPP_ACCESS_TOKEN = Get-UserEnvValue -Name "META_WHATSAPP_ACCESS_TOKEN"
  SLACK_SIGNING_SECRET = Get-UserEnvValue -Name "SLACK_SIGNING_SECRET"
  SLACK_BOT_TOKEN = Get-UserEnvValue -Name "SLACK_BOT_TOKEN"
  SLACK_CHANNEL_ID = Get-UserEnvValue -Name "SLACK_CHANNEL_ID"
  GMAIL_CLIENT_ID = Get-UserEnvValue -Name "GMAIL_CLIENT_ID"
  GMAIL_CLIENT_SECRET = Get-UserEnvValue -Name "GMAIL_CLIENT_SECRET"
  GMAIL_REFRESH_TOKEN = Get-UserEnvValue -Name "GMAIL_REFRESH_TOKEN"
  GMAIL_SENDER_EMAIL = Get-UserEnvValue -Name "GMAIL_SENDER_EMAIL"
  GMAIL_SUPPLIER_EMAIL = Get-UserEnvValue -Name "GMAIL_SUPPLIER_EMAIL"
}

$missing = @(
  $values.GetEnumerator() |
    Where-Object { [string]::IsNullOrWhiteSpace($_.Value) } |
    ForEach-Object { $_.Key }
)

if ($missing.Count -gt 0) {
  throw "Missing required environment values: $($missing -join ', ')"
}

Write-Output "Applying Logia CloudHub properties. Secrets are passed directly to Anypoint and are not written to Git."

anypoint-cli-v4 runtime-mgr application modify $AppId `
  --no-lastMileSecurity `
  --property "logia.tenant:demo-mauritius" `
  --property "logia.purpose:RESOLVE_HOSPITAL_OPERATION_RISK" `
  --property "northstar.tenant:demo-mauritius" `
  --property "northstar.purpose:RESOLVE_HOSPITAL_OPERATION_RISK" `
  --property "salesforce.host:$($values.SALESFORCE_HOST)" `
  --property "meta.webhookVerifyToken:north-star-meta-verify" `
  --property "meta.whatsappPhoneNumberId:$($values.META_WHATSAPP_PHONE_NUMBER_ID)" `
  --property "slack.channelId:$($values.SLACK_CHANNEL_ID)" `
  --secureProperty "salesforce.accessToken:$($values.SALESFORCE_ACCESS_TOKEN)" `
  --secureProperty "meta.whatsappAccessToken:$($values.META_WHATSAPP_ACCESS_TOKEN)" `
  --secureProperty "slack.signingSecret:$($values.SLACK_SIGNING_SECRET)" `
  --secureProperty "slack.botToken:$($values.SLACK_BOT_TOKEN)" `
  --secureProperty "gmail.clientId:$($values.GMAIL_CLIENT_ID)" `
  --secureProperty "gmail.clientSecret:$($values.GMAIL_CLIENT_SECRET)" `
  --secureProperty "gmail.refreshToken:$($values.GMAIL_REFRESH_TOKEN)" `
  --secureProperty "gmail.senderEmail:$($values.GMAIL_SENDER_EMAIL)" `
  --secureProperty "gmail.supplierEmail:$($values.GMAIL_SUPPLIER_EMAIL)" `
  --output json | Out-Null

Write-Output "CloudHub update submitted. Wait until Runtime Manager shows the app as RUNNING, then smoke-test /logia queue."
