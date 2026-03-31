$body = @{ username = 'customer01'; password = 'Customer@123' } | ConvertTo-Json
$res = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/auth/login/' -Method POST -ContentType 'application/json' -Body $body
$data = $res.Content | ConvertFrom-Json
Write-Host "Status: $($res.StatusCode)"
Write-Host "Token exists: $(-not [string]::IsNullOrEmpty($data.access))"
Write-Host "Token (first 30 chars): $($data.access.Substring(0, 30))..."
