import random
from flask import Flask, render_template, request
import redis
import datetime

app = Flask(__name__)
import os
from urllib.parse import urlparse

redis_url = urlparse(os.environ.get("REDIS_URL"))
r = redis.Redis(
    host=redis_url.hostname,
    port=redis_url.port,
    password=redis_url.password
)


@app.route('/')
def index():
    #user_ip = request.remote_addr
    user_ip = f"192.168.0.{random.randint(1, 255)}"  # solo para pruebas
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # HyperLogLog: visitas únicas
    r.pfadd('unique_visits', user_ip)

    # Bitmap: actividad diaria
    user_id = abs(hash(user_ip)) % 100000
    r.setbit(f'active_users:{today}', user_id, 1)

    # Estadísticas actuales
    total_unique_visits = r.pfcount('unique_visits')
    today_active = r.bitcount(f'active_users:{today}')

    # Obtener actividad de los últimos 7 días
    daily_activity = []
    for i in range(7):
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        count = r.bitcount(f'active_users:{day}')
        daily_activity.append((day, count))

    # Orden cronológico
    daily_activity.reverse()

    return render_template('index.html',
                           total_unique_visits=total_unique_visits,
                           today_active=today_active,
                           today=today,
                           daily_activity=daily_activity)

if __name__ == '__main__':
    app.run(debug=True)
