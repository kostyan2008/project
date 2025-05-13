import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

OWM_API_KEY = os.getenv('OWM_API_KEY')
if not OWM_API_KEY:
    raise ValueError("No OWM_API_KEY set in environment variables")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
CACHE_TIME_MINUTES = 10

weather_cache = {}


def get_cached_weather(city_name):
    cached_data = weather_cache.get(city_name.lower())
    if cached_data:
        cache_time = cached_data['timestamp']
        time_diff = (datetime.now() - cache_time).total_seconds() / 60
        if time_diff < CACHE_TIME_MINUTES:
            return cached_data['data']
    return None


def set_cached_weather(city_name, data):
    weather_cache[city_name.lower()] = {
        'data': data,
        'timestamp': datetime.now()
    }


def get_weather_data(city_name):
    cached_data = get_cached_weather(city_name)
    if cached_data:
        return cached_data

    try:
        params = {
            'q': city_name,
            'appid': OWM_API_KEY,
            'units': 'metric',
            'lang': 'ru'
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        set_cached_weather(city_name, data)
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_country_flag(country_code):
    return f"https://flagcdn.com/48x36/{country_code.lower()}.png"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city').strip()
        if not city:
            flash('Пожалуйста, введите название города', 'error')
            return redirect(url_for('index'))
        return redirect(url_for('weather', city=city))

    popular_cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
    return render_template('index.html', popular_cities=popular_cities)


@app.context_processor
def inject_year():
    return {'now': datetime.now()}


@app.route('/weather')
def weather():
    city = request.args.get('city')
    if not city:
        flash('Город не указан', 'error')
        return redirect(url_for('index'))

    weather_data = get_weather_data(city)

    if not weather_data or weather_data.get('cod') != 200:
        error_msg = "Город не найден" if weather_data and weather_data.get(
            'cod') == '404' else "Произошла ошибка при получении данных"
        flash(error_msg, 'error')
        return redirect(url_for('index'))

    try:
        country_code = weather_data['sys']['country']
        weather_info = {
            'city': city,
            'country': weather_data['sys']['country'],
            'country_flag': get_country_flag(country_code),
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'description': weather_data['weather'][0]['description'].capitalize(),
            'icon': weather_data['weather'][0]['icon'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'pressure': weather_data['main']['pressure'],
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M'),
            'updated': datetime.now().strftime('%H:%M:%S')
        }
        return render_template('weather.html', weather=weather_info)

    except KeyError as e:
        print(f"Error parsing weather data: {e}")
        flash('Ошибка при обработке данных о погоде', 'error')
        return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
