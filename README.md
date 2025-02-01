# Codlaxy

A Django-based web application for project management and collaboration.

## Prerequisites

- Docker and Docker Compose
- Git

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd codlaxy
```

2. Environment Setup:
   - Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   - Update the environment variables in `.env` if needed

3. Build and start the containers:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

This will start the following services:
- Django web application (http://localhost:8000)
- PostgreSQL database
- Redis for caching
- MailHog for email testing (http://localhost:8025)
- PgAdmin for database management (http://localhost:5051)

## Development URLs

- Main application: http://localhost:8000
- Email testing interface (MailHog): http://localhost:8025
- Database admin (PgAdmin): http://localhost:5051
  - Login Email: dev@codlaxy.com
  - Login Password: devadmin
  
  After logging into PgAdmin, to connect to the database use:
  - Host: db
  - Port: 5432
  - Database: codlaxy_dev
  - Username: codlaxy_dev
  - Password: codlaxy_dev

## Database Migrations

Migrations are automatically run when the container starts. If you need to run them manually:

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

## Creating a Superuser

To create an admin user:

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

## Development Tools

- Django Debug Toolbar is enabled in development (accessible at `/__debug__/` when logged in as admin)
- Django Extensions are installed for development utilities
- Automatic email testing with MailHog
- PostgreSQL database GUI with PgAdmin

## Stopping the Application

To stop the application:

```bash
docker-compose -f docker-compose.dev.yml down
```

To stop and remove all data (including database):

```bash
docker-compose -f docker-compose.dev.yml down -v
```

## Project Structure

- `codlaxy/` - Main Django project directory
  - `settings/` - Split settings files for different environments
    - `base.py` - Base settings
    - `development.py` - Development-specific settings
    - `production.py` - Production settings
- `projects/` - Projects app
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded files
- `requirements/` - Python dependencies
  - `base.txt` - Base requirements
  - `development.txt` - Development requirements
  - `production.txt` - Production requirements

## Key Features

- **Project Management**
  - Create and manage tech projects
  - Specify required roles and number of vacancies
  - Track project status and updates
  - Add project details including technologies used

- **Team Building**
  - Apply for roles in projects
  - Review and manage applications
  - Form project teams
  - Real-time notifications

- **User Interaction**
  - Like and comment on projects
  - User profiles with portfolio links
  - Project categorization (Startup, Skill Improvement, Recognition)
  - Search projects by title, description, technologies, or roles

## Tech Stack

- Backend: Django 5.0
- Database: PostgreSQL
- Frontend: Tailwind CSS
- Docker for containerization

## Troubleshooting

1. If the web container fails to start:
   ```bash
   docker-compose logs web
   ```

2. To reset the database:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. To access the Django shell:
   ```bash
   docker-compose exec web python manage.py shell
   ```

## Support

For issues or questions:
1. Check the existing issues in the repository
2. Create a new issue with detailed information about your problem
3. Include relevant error messages and steps to reproduce

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. 