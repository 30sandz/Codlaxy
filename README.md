# Codlaxy - Tech Project Collaboration Platform

A dynamic platform for tech enthusiasts to collaborate on projects, form teams, and showcase their work. Users can create projects, specify required roles, and connect with potential team members.

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

## Prerequisites

- Docker and Docker Compose
- Git

## Running the Project

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd codlaxy
   ```

2. Start the Docker containers:
   ```bash
   docker-compose up -d
   ```
   This will start:
   - Web application on port 8000
   - PostgreSQL database on port 5432
   - Redis on port 6379
   - pgAdmin on port 5050

3. Access the application:
   - Main application: http://localhost:8000
   - pgAdmin: http://localhost:5050
     - Email: codlaxy@admin.com
     - Password: admin

4. Default database credentials:
   - Database: codlaxy
   - Username: codlaxy
   - Password: codlaxy

## Development

To make changes to the project:

1. Stop the containers:
   ```bash
   docker-compose down
   ```

2. Make your changes to the code

3. Rebuild and start the containers:
   ```bash
   docker-compose up -d --build
   ```

## Project Structure

- `projects/`: Main application directory
  - `models.py`: Database models (User, Project, Application, etc.)
  - `views.py`: View logic for handling requests
  - `templates/`: HTML templates
  - `templatetags/`: Custom template filters

## Features in Detail

1. **Project Creation**
   - Title and description
   - Category selection
   - Technology stack
   - Required roles with vacancy counts
   - Project logo and links (GitHub, LinkedIn, Demo)

2. **Role Management**
   - Specify roles needed for the project
   - Set number of vacancies per role
   - Track applications and team members

3. **User Interactions**
   - Comment on projects
   - Like projects
   - Apply for roles
   - Receive notifications

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