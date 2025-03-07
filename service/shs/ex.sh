cd service

# python manage.py collectstatic -y
# cp -r /app/service/static/css /backend_static/
# cp -r /app/service/static/js /backend_static/
# cp -r /app/service/static/img /backend_static/

python manage.py migrate

python -m uvicorn --host 0.0.0.0 --port 8000 --workers 1 service.asgi:application 