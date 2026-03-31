Param()

$ErrorActionPreference = "Stop"

Write-Host "[1/4] Seeding laptop-service..." -ForegroundColor Cyan
docker compose exec laptop-service python manage.py seed_laptops

Write-Host "[2/4] Seeding mobile-service..." -ForegroundColor Cyan
docker compose exec mobile-service python manage.py seed_mobiles

Write-Host "[3/4] Seeding customer-service..." -ForegroundColor Cyan
docker compose exec customer-service python manage.py seed_customers

Write-Host "[4/4] Seeding staff-service..." -ForegroundColor Cyan
docker compose exec staff-service python manage.py seed_staff

Write-Host "Done. Sample accounts:" -ForegroundColor Green
Write-Host "- customer01 / Customer@123"
Write-Host "- customer02 / Customer@123"
Write-Host "- customer03 / Customer@123"
Write-Host "- staff01 / Staff@123"
Write-Host "- staff02 / Staff@123"
