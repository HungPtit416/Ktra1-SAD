# Full e2e test: Login -> Add product to cart -> View cart
Write-Host "E2E CART TEST" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "Step 1: Login customer" -ForegroundColor Yellow
$loginBody = @{ username = 'customer01'; password = 'Customer@123' } | ConvertTo-Json
$loginRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/auth/login/' -Method POST -ContentType 'application/json' -Body $loginBody -UseBasicParsing
$token = ($loginRes.Content | ConvertFrom-Json).access
Write-Host "OK Login: $($loginRes.StatusCode)"

# Step 2: Get carts
Write-Host "Step 2: Fetch carts" -ForegroundColor Yellow
$headers = @{ Authorization = "Bearer $token" }
$cartsRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/carts/' -Headers $headers -UseBasicParsing
$carts = $cartsRes.Content | ConvertFrom-Json
Write-Host "OK Carts: $($carts.Count) found"

if ($carts.Count -gt 0) {
    $cartId = $carts[0].id
    Write-Host "Using cart: $cartId"
    
    # Step 3: Add product
    Write-Host "Step 3: Add to cart" -ForegroundColor Yellow
    $addBody = @{ cart = $cartId; product_type = 'laptop'; product_id = 1; quantity = 2 } | ConvertTo-Json
    $addRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/cart-items/' -Method POST -Headers $headers -ContentType 'application/json' -Body $addBody -UseBasicParsing
    Write-Host "OK Added: $($addRes.StatusCode)"
    
    # Step 4: Get items
    Write-Host "Step 4: Fetch items" -ForegroundColor Yellow
    $itemsRes = Invoke-WebRequest -Uri 'http://localhost:8100/customer/api/cart-items/' -Headers $headers -UseBasicParsing
    $items = $itemsRes.Content | ConvertFrom-Json
    Write-Host "OK Items: $($items.Count) in cart"
    
    # Step 5: Get product
    Write-Host "Step 5: Fetch product" -ForegroundColor Yellow
    $prodRes = Invoke-WebRequest -Uri 'http://localhost:8100/laptops/1/' -UseBasicParsing
    $product = $prodRes.Content | ConvertFrom-Json
    Write-Host "OK Product: $($product.name) - $($product.price) VND"
    Write-Host ""
    Write-Host "SUCCESS - Cart working!" -ForegroundColor Green
}

