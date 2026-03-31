$appJs = Invoke-WebRequest -Uri 'http://localhost:8100/assets/app.js' -UseBasicParsing
$content = $appJs.Content
Write-Host "✅ Verification of deployed fixes:"
Write-Host ""
Write-Host "File size: $($content.Length) bytes"
Write-Host "Has getHasToken function: $(if ($content -match 'const getHasToken') { 'YES' } else { 'NO' })"
Write-Host "Has login redirect: $(if ($content -match "window.location.href = '/customer-ui/'") { 'YES' } else { 'NO' })"
Write-Host "Has success toast: $(if ($content -match 'Dang nhap thanh cong') { 'YES' } else { 'NO' })"
