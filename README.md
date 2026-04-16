# Real-Time Chat Application

A modern, scalable real-time messaging application built with Django and WebSockets. Designed to work seamlessly across web and mobile platforms, featuring real-time messaging similar to WhatsApp and Facebook Messenger.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [WebSocket Events](#websocket-events)
- [Database Schema](#database-schema)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Messaging
- **Real-time messaging** using WebSockets (Django Channels)
- **One-to-one conversations** and **group chats**
- **Message persistence** with full conversation history
- **Typing indicators** showing when users are typing
- **Online/offline status** tracking
- **Read receipts** (sent, delivered, read)
- **Message editing and deletion**
- **Message search and filtering**

### User Management
- **User authentication** with JWT tokens
- **User profiles** with avatars and bios
- **Contact list** with online status
- **Block/unblock users**
- **Last seen timestamp**
- **User presence** tracking

### Media Support
- **Image sharing** in conversations
- **File attachments** (with size limits)
- **Media preview** and caching
- **Image compression** for mobile optimization

### Additional Features
- **Push notifications** for missed messages
- **Message receipts** and delivery status
- **Conversation muting** and archiving
- **User activity logs**
- **Admin dashboard** for moderation

## 🛠️ Tech Stack

### Backend
- **Django 4.x** - Web framework
- **Django REST Framework** - API development
- **Django Channels 4.x** - WebSocket support
- **Channels Redis** - Channel layer backend
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker

### Frontend (Web)
- **React.js** (recommended)
- **WebSocket client library**
- **State management** (Redux/Context API)
- **UI library** (Material-UI/Tailwind)

### Mobile
- **React Native / Flutter** (recommended)
- **WebSocket client integration**

### DevOps
- **Docker & Docker Compose** (for containerization)
- **Gunicorn & Daphne** (WebSocket server)
- **Nginx** (reverse proxy)

## 🏗️ Project Architecture

```
┌─────────────────────────────────────┐
│         Client Applications         │
│    (Web React / Mobile React Native)│
└────────────┬────────────────────────┘
             │ HTTP + WebSocket
             ↓
┌─────────────────────────────────────┐
│      API Gateway / Load Balancer    │
│            (Nginx)                  │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
┌─────────────┐  ┌──────────────┐
│   Daphne    │  │   Gunicorn   │
│ (WebSocket) │  │   (HTTP API) │
└────┬────────┘  └────┬─────────┘
     │                │
     └────────┬───────┘
              ↓
      ┌──────────────────┐
      │  Django App      │
      │  - Models        │
      │  - Views         │
      │  - Consumers     │
      │  - Serializers   │
      └────────┬─────────┘
               ↓
      ┌──────────────────┐
      │  PostgreSQL DB   │
      │  Redis Cache     │
      └──────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Virtual environment (venv/virtualenv)

### Step 1: Clone and Setup Virtual Environment

```bash
cd /home/elam09harvey/Desktop/ChatApp/Chatapp
source ChatAppVenv/bin/activate  # On Linux/Mac
# or
ChatAppVenv\Scripts\activate  # On Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Additional Requirements

Create a `requirements.txt` file with all dependencies:

```
Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.0.0
psycopg2-binary==2.9.6
channels==4.0.0
channels-redis==4.1.0
asgiref==3.7.1
redis==5.0.0
pillow==10.0.0
python-decouple==3.8
PyJWT==2.8.0
djangorestframework-simplejwt==5.3.0
drf-spectacular==0.27.0
celery==5.3.0
django-celery-beat==2.5.0
factory-boy==3.3.0
pytest==7.4.0
pytest-django==4.5.2
```

Update and install:

```bash
pip install -r requirements.txt
```

### Step 4: PostgreSQL Setup

Create a database and user:

```bash
psql -U postgres
CREATE DATABASE chatapp_db;
CREATE USER chatapp_user WITH PASSWORD 'your_secure_password';
ALTER ROLE chatapp_user SET client_encoding TO 'utf8';
ALTER ROLE chatapp_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE chatapp_user SET default_transaction_deferrable TO on;
ALTER ROLE chatapp_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE chatapp_db TO chatapp_user;
```

### Step 5: Redis Setup

```bash
# Install Redis (if not already installed)
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Redis
redis-server
```

## ⚙️ Configuration

### Create `.env` file in project root:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=chatapp_db
DATABASE_USER=chatapp_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CHANNEL_LAYERS_BACKEND=redis://localhost:6379/1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# JWT Settings
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (Optional - for media storage)
USE_S3=False
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

### Update `settings.py`:

```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

INSTALLED_APPS = [
    'daphne',  # Must be first for async support
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'chat',  # Your chat app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}

# Channels Configuration
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://localhost:6379/0')],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_EXPIRATION_HOURS', default=24, cast=int)),
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
    }
}
```

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Django Development Server (WebSocket & HTTP):**
```bash
source ChatAppVenv/bin/activate
python manage.py migrate
python manage.py runserver
```

Or use Daphne for better async support:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

**Terminal 3 - Frontend (if building React):**
```bash
npm start  # From your React project directory
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Access admin panel: `http://localhost:8000/admin`

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}

Response: 201 Created
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```
POST /api/auth/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### User Endpoints

#### Get User Profile
```
GET /api/users/me/
Headers: Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar": "https://...",
  "bio": "Hello, I'm using ChatApp!",
  "is_online": true,
  "last_seen": "2024-03-30T10:30:00Z"
}
```

#### Update User Profile
```
PATCH /api/users/me/
Headers: Authorization: Bearer <access_token>
Content-Type: application/json

{
  "bio": "Updated bio",
  "first_name": "John",
  "avatar": <file>
}
```

#### Get Contacts List
```
GET /api/users/contacts/
Headers: Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 2,
    "username": "jane_doe",
    "email": "jane@example.com",
    "is_online": true,
    "last_seen": "2024-03-30T11:00:00Z"
  },
  ...
]
```

### Conversation Endpoints

#### Get All Conversations
```
GET /api/conversations/
Headers: Authorization: Bearer <access_token>
Query params: ?search=jane&ordering=-updated_at

Response: 200 OK
{
  "count": 15,
  "next": "http://api/conversations/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "direct",
      "participants": [1, 2],
      "last_message": {
        "id": 100,
        "content": "Hey, how are you?",
        "sender": 2,
        "created_at": "2024-03-30T10:30:00Z",
        "read_by": [1, 2]
      },
      "unread_count": 0,
      "updated_at": "2024-03-30T10:30:00Z"
    },
    ...
  ]
}
```

#### Create Conversation
```
POST /api/conversations/
Headers: Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "direct",
  "participants": [2],
  "name": null  // For group chats
}

Response: 201 Created
{
  "id": 1,
  "type": "direct",
  "participants": [1, 2],
  "created_at": "2024-03-30T10:00:00Z"
}
```

#### Get Conversation Messages
```
GET /api/conversations/{conversation_id}/messages/
Headers: Authorization: Bearer <access_token>
Query params: ?page=1&search=hello

Response: 200 OK
{
  "count": 50,
  "next": "...",
  "results": [
    {
      "id": 1,
      "conversation": 1,
      "sender": 1,
      "content": "Hello!",
      "message_type": "text",
      "media": null,
      "created_at": "2024-03-30T09:00:00Z",
      "edited_at": null,
      "read_by": [1, 2],
      "reactions": []
    },
    ...
  ]
}
```

#### Send Message
```
POST /api/conversations/{conversation_id}/messages/
Headers: Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Hello, Jane!",
  "message_type": "text",
  "media": null
}

Response: 201 Created
{
  "id": 101,
  "conversation": 1,
  "sender": 1,
  "content": "Hello, Jane!",
  "message_type": "text",
  "created_at": "2024-03-30T10:35:00Z",
  "read_by": []
}
```

#### Edit Message
```
PATCH /api/conversations/{conversation_id}/messages/{message_id}/
Headers: Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated message content"
}
```

#### Delete Message
```
DELETE /api/conversations/{conversation_id}/messages/{message_id}/
Headers: Authorization: Bearer <access_token>

Response: 204 No Content
```

#### Mark Messages as Read
```
POST /api/conversations/{conversation_id}/mark-as-read/
Headers: Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message_ids": [1, 2, 3]
}

Response: 200 OK
```

## 🔌 WebSocket Events

### Connection
**URL:** `ws://localhost:8000/ws/chat/{conversation_id}/?token=<access_token>`

### Client Events (Client → Server)

#### Send Message
```javascript
socket.send(JSON.stringify({
  type: 'chat_message',
  message: 'Hello!',
  message_id: 'uuid-here'
}));
```

#### Typing Indicator
```javascript
socket.send(JSON.stringify({
  type: 'typing',
  is_typing: true
}));
```

#### Mark as Read
```javascript
socket.send(JSON.stringify({
  type: 'mark_read',
  message_ids: [1, 2, 3]
}));
```

#### User Presence
```javascript
socket.send(JSON.stringify({
  type: 'presence',
  status: 'online' // or 'offline', 'away'
}));
```

### Server Events (Server → Client)

#### Message Received
```javascript
{
  type: 'chat_message',
  id: 101,
  sender: {
    id: 2,
    username: 'jane_doe',
    avatar: 'https://...'
  },
  message: 'Hi John!',
  timestamp: '2024-03-30T10:35:00Z',
  read_by: []
}
```

#### User Typing
```javascript
{
  type: 'typing',
  user: {
    id: 2,
    username: 'jane_doe'
  },
  is_typing: true
}
```

#### Message Read Receipt
```javascript
{
  type: 'message_read',
  message_id: 101,
  read_by: [1, 2],
  timestamp: '2024-03-30T10:36:00Z'
}
```

#### User Presence Changed
```javascript
{
  type: 'user_presence',
  user: {
    id: 2,
    username: 'jane_doe'
  },
  status: 'online',
  last_seen: '2024-03-30T10:40:00Z'
}
```

#### Message Edited
```javascript
{
  type: 'message_edited',
  message_id: 101,
  content: 'Updated message',
  edited_at: '2024-03-30T10:37:00Z'
}
```

#### Message Deleted
```javascript
{
  type: 'message_deleted',
  message_id: 101,
  sender_id: 1
}
```

## 📊 Database Schema

### User Model
```
User (extends Django User)
├── id (PK)
├── username
├── email
├── password (hashed)
├── first_name
├── last_name
├── avatar (ImageField)
├── bio (TextField)
├── is_online (BooleanField)
├── last_seen (DateTimeField)
├── blocked_users (M2M)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### Conversation Model
```
Conversation
├── id (PK)
├── type (CharField: 'direct' | 'group')
├── name (CharField - for groups)
├── description (TextField - for groups)
├── participants (M2M to User)
├── avatar (ImageField - for groups)
├── created_by (FK to User)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### Message Model
```
Message
├── id (PK)
├── conversation (FK)
├── sender (FK to User)
├── content (TextField)
├── message_type (CharField: 'text' | 'image' | 'file')
├── media (FileField)
├── read_by (M2M to User)
├── edited_at (DateTimeField, nullable)
├── is_deleted (BooleanField)
├── created_at (DateTimeField)
└── reaction (Reverse relation)
```

### MessageReaction Model
```
MessageReaction
├── id (PK)
├── message (FK)
├── user (FK)
├── emoji (CharField)
└── created_at (DateTimeField)
```

## 👨‍💻 Development

### Project Structure

```
chatapp/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── chat/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   ├── tests.py
│   └── urls.py
├── users/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tests.py
│   └── urls.py
├── common/
│   ├── permissions.py
│   ├── exceptions.py
│   ├── utils.py
│   └── middleware.py
├── media/
├── staticfiles/
├── .env
├── .gitignore
├── requirements.txt
├── manage.py
├── docker-compose.yml
└── Dockerfile
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest chat/

# Run with coverage
pytest --cov=chat --cov=users

# Run specific test file
pytest users/tests/test_models.py
```

### Creating Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Code Style

Use Black for code formatting:
```bash
black .
```

Use Flake8 for linting:
```bash
flake8 .
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
```

### docker-compose.yml
```yaml
version: '3.9'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 config.asgi:application
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings
    env_file: .env
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## ☁️ Production Deployment

### Prerequisites
- Domain name configured
- SSL certificate (Let's Encrypt)
- Server with at least 2GB RAM

### Deployment Steps

1. **Update .env for production**
2. **Set DEBUG=False**
3. **Change SECRET_KEY**
4. **Configure ALLOWED_HOSTS**
5. **Setup email notifications**
6. **Use PostgreSQL with proper backups**
7. **Use Redis with persistence**
8. **Configure Nginx as reverse proxy**
9. **Use Gunicorn + Daphne with supervisor**
10. **Setup SSL/TLS with Certbot**
11. **Configure automatic backups**
12. **Enable monitoring and logging**

### Nginx Configuration
```nginx
upstream daphne {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## 📚 Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Last Updated:** March 30, 2024
**Version:** 1.0.0
