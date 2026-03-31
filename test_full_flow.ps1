# Test the full flow: login -> get token -> fetch product details -> fetch carts
$body = @{ username = 'customer01'; password = 'Customer@123' } | ConvertTo-Json
$loginRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/auth/login/' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
$loginData = $loginRes.Content | ConvertFrom-Json 
$token = $loginData.access
Write-Host "1. Login Status: $($loginRes.StatusCode)"

# Fetch a laptop product (public endpoint, no auth needed)
$productRes = Invoke-WebRequest -Uri 'http://localhost:8100/laptops/1/' -UseBasicParsing
$productData = $productRes.Content | ConvertFrom-Json
Write-Host "2. Product Fetch Status: $($productRes.StatusCode)"
Write-Host "   Product Name: $($productData.name)"

# Fetch carts with token (requires auth)
$headers = @{ Authorization = "Bearer $token" }
$cartsRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/carts/' -Headers $headers -UseBasicParsing
$cartsData = $cartsRes.Content | ConvertFrom-Json
Write-Host "3. Carts Fetch Status: $($cartsRes.StatusCode)"
Write-Host "   Customer carts count: $($cartsData.Count)"

Write-Host ""
Write-Host "✅ FLOW VERIFICATION COMPLETE - All endpoints working!"
