from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, VoiceCommand
import speech_recognition as sr
import pyttsx3
import json
import bcrypt
from datetime import datetime
import requests
from django.conf import settings
import re

def index(request):
    if request.user.is_authenticated:
        commands = VoiceCommand.objects.filter(user=request.user).order_by('-timestamp')[:5]
        return render(request, 'assistant/index.html', {'commands': commands})
    return render(request, 'assistant/index.html')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(
            username=username,
            email=email,
            password=hashed_password.decode('utf-8')
        )
        login(request, user)
        return JsonResponse({'message': 'Registration successful'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                login(request, user)
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

@login_required
@csrf_exempt
def process_voice_command(request):
    if request.method == 'POST':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)  # Reduce background noise
            audio = r.listen(source, timeout=5)  # 5 second timeout
            try:
                command = r.recognize_google(audio)
                response = process_command(command, request.user)
                
                VoiceCommand.objects.create(
                    user=request.user,
                    command=command,
                    response=response
                )
                
                engine = pyttsx3.init()
                engine.say(response)
                engine.runAndWait()
                
                return JsonResponse({
                    'command': command,
                    'response': response
                })
            except sr.UnknownValueError:
                return JsonResponse({'error': 'Could not understand audio. Please try again.'}, status=400)
            except sr.RequestError:
                return JsonResponse({'error': 'Could not request results. Please check your internet connection.'}, status=500)
            except sr.WaitTimeoutError:
                return JsonResponse({'error': 'Listening timed out. Please try again.'}, status=408)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_weather_info(city="London"):
    """Get detailed weather information for a city."""
    try:
        api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not api_key:
            return "Weather service is not configured yet."
        
        # Get current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather information
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            description = data['weather'][0]['description']
            pressure = data['main']['pressure']
            
            # Get sunrise and sunset times
            sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p')
            sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p')
            
            # Format the response
            weather_info = {
                'city': city.title(),
                'temperature': round(temp, 1),
                'feels_like': round(feels_like, 1),
                'description': description.capitalize(),
                'humidity': humidity,
                'wind_speed': round(wind_speed * 3.6, 1),  # Convert m/s to km/h
                'pressure': pressure,
                'sunrise': sunrise,
                'sunset': sunset
            }
            
            return weather_info
        else:
            return None
    except Exception as e:
        return None

def extract_city_from_command(command):
    """Extract city name from weather-related commands."""
    # Common patterns for weather queries
    patterns = [
        r"weather (?:in|at|for) (.+)",
        r"weather of (.+)",
        r"what's the weather (?:in|at|for) (.+)",
        r"what is the weather (?:in|at|for) (.+)",
        r"how's the weather (?:in|at|for) (.+)",
        r"temperature (?:in|at|for) (.+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command.lower())
        if match:
            city = match.group(1).strip()
            # Remove common words that might be captured
            city = re.sub(r'\b(right now|today|tomorrow|please)\b', '', city).strip()
            return city
    
    return "London"  # Default city

def format_weather_response(weather_info):
    """Format weather information into a natural response."""
    if not weather_info or isinstance(weather_info, str):
        return "Sorry, I couldn't fetch the weather information at the moment."
    
    response = (
        f"Here's the weather in {weather_info['city']}:\n\n"
        f"Temperature: {weather_info['temperature']}°C (Feels like {weather_info['feels_like']}°C)\n"
        f"Condition: {weather_info['description']}\n"
        f"Humidity: {weather_info['humidity']}%\n"
        f"Wind Speed: {weather_info['wind_speed']} km/h\n"
        f"Air Pressure: {weather_info['pressure']} hPa\n"
        f"Sunrise: {weather_info['sunrise']}\n"
        f"Sunset: {weather_info['sunset']}"
    )
    return response

def process_command(command, user):
    command = command.lower()
    
    if 'hello' in command or 'hi' in command:
        return f"Hello {user.username}! How can I help you today?"
    
    elif 'time' in command:
        current_time = datetime.now().strftime('%I:%M %p')
        return f"The current time is {current_time}"
    
    elif 'date' in command:
        current_date = datetime.now().strftime('%B %d, %Y')
        return f"Today's date is {current_date}"
    
    elif 'weather' in command or 'temperature' in command:
        city = extract_city_from_command(command)
        weather_info = get_weather_info(city)
        return format_weather_response(weather_info)
    
    elif 'tell me about yourself' in command or 'who are you' in command:
        return f"I am JARVIS, your personal AI assistant. I can help you with basic tasks like telling time, date, and detailed weather information for any city."
    
    elif 'what can you do' in command or 'help' in command:
        return ("I can help you with:\n"
                "1. Telling you the current time\n"
                "2. Providing today's date\n"
                "3. Checking detailed weather information for any city (try 'weather in Paris')\n"
                "4. Basic conversation\n"
                "Just ask me naturally what you'd like to know!")
    
    elif 'thank you' in command:
        return f"You're welcome, {user.username}! Is there anything else I can help you with?"
    
    elif 'bye' in command or 'goodbye' in command:
        return f"Goodbye {user.username}! Have a great day!"
    
    else:
        return "I'm sorry, I don't understand that command. Try saying 'help' to see what I can do!"

@login_required
def command_history(request):
    commands = VoiceCommand.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'assistant/history.html', {'commands': commands})
