# Goals Tracker

A comprehensive goal tracking application that helps users define, track, and achieve their goals through daily standards and structured goal-setting frameworks.

## Features

- Three-tiered goal structure (BIG, MTG, DP)
- Daily standards tracking
- Weekly, monthly, quarterly, and yearly reflections
- Progress analytics and visualization
- User authentication and profile management

## Tech Stack

### Frontend
- Vue 3 + Vite
- TailwindCSS for styling
- Pinia for state management
- Vue Router for navigation
- Headless UI for accessible components

### Backend
- Django REST Framework
- PostgreSQL database
- Redis for caching and Celery
- JWT authentication
- Celery for task orchestration

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis

## Setup

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the variables with your database and Redis configuration

4. Initialize the database:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Start Celery worker (in a separate terminal):
```bash
celery -A backend worker -l info
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Development

### Backend Development

- Create new Django app: `python manage.py startapp app_name`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

### Frontend Development

- Create new component: Create `.vue` file in appropriate directory under `src/components` or `src/views`
- Add route: Update `src/router/index.js`
- Add store: Create new store file in `src/stores`

## Project Structure

```
.
├── backend/
│   ├── backend/          # Django project settings
│   ├── users/           # User management app
│   ├── goals/           # Goals management app
│   ├── standards/       # Standards management app
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── assets/      # Static assets
    │   ├── components/  # Reusable Vue components
    │   ├── layouts/     # Layout components
    │   ├── router/      # Vue Router configuration
    │   ├── stores/      # Pinia stores
    │   └── views/       # Page components
    ├── public/          # Public static files
    └── package.json
```

## API Documentation

The API documentation is available at `/api/docs/` when running the backend server in development mode.

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Deployment

### Backend Deployment (Railway.app)
1. Connect your repository to Railway
2. Set up environment variables
3. Deploy the application

### Frontend Deployment (Netlify)
1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Configure environment variables

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
