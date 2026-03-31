$body = @{ username = 'customer01'; password = 'Customer@123' } | ConvertTo-Json
$res = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/auth/login/' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
$data = $res.Content | ConvertFrom-Json 
Write-Host "Login Status: $($res.StatusCode)"
if ($data.access) {
    Write-Host "Token generated successfully"
    Write-Host "Token length: $($data.access.Length)"
} else {
    Write-Host "ERROR: No token"
}
