# JARVIS - AI Voice Assistant

A web-based AI voice assistant built with Python, Django, and MongoDB. Features user authentication and voice command processing.

## Features

- User registration and authentication
- Voice command processing
- Text-to-speech responses
- Modern, responsive UI using Tailwind CSS
- MongoDB database integration

## Prerequisites

- Python 3.8 or higher
- MongoDB installed and running
- PyAudio dependencies (for voice recognition)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd jarvis
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Make sure MongoDB is running on your system.

4. Apply the database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit `http://localhost:8000` in your web browser.

## Usage

1. Register a new account or login with existing credentials
2. Click the "Start Listening" button to activate voice recognition
3. Speak your command
4. The assistant will process your command and respond with voice and text

## Available Commands

- Greeting: "Hello" or "Hi"
- Time: Ask for the current time
- Weather: Ask about the weather (currently a placeholder response)
- Farewell: "Bye" or "Goodbye"

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 