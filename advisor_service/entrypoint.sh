#!/bin/bash
set -e

# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

echo "🚀 Starting AI Advisor Service..."

# Wait for database
echo "⏳ Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✓ Database ready"

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
echo "👤 Checking superuser..."
python manage.py shell <<END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superuser created: admin / admin123")
else:
    print("✓ Superuser already exists")
END

# Load KB sample
echo "📚 Loading Knowledge Base..."
python manage.py load_kb --sample 2>/dev/null || echo "⚠️  KB already loaded or error"

# Start server
echo "🟢 Starting server..."
gunicorn advisor_service.wsgi:application \
    --bind 0.0.0.0:8003 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
