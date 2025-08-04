#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH."
        exit 1
    fi
}

# Function to update Docker containers
update_docker() {
    print_status "Updating Docker containers..."
    
    # Stop existing containers
    docker-compose down
    
    # Rebuild containers with latest code
    docker-compose build --no-cache web
    
    # Start containers
    docker-compose up -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 10
    
    print_success "Docker containers updated successfully!"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Make migrations
    docker-compose exec -T web python manage.py makemigrations
    
    # Apply migrations
    docker-compose exec -T web python manage.py migrate
    
    print_success "Database migrations completed!"
}

# Function to collect static files
collect_static() {
    print_status "Collecting static files..."
    
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_success "Static files collected!"
}

# Function to create superuser if needed
create_superuser() {
    print_status "Checking if superuser exists..."
    
    # Check if superuser exists
    if ! docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" 2>/dev/null | grep -q "Superuser exists"; then
        print_warning "No superuser found. You can create one with:"
        echo "docker-compose exec web python manage.py createsuperuser"
    else
        print_success "Superuser already exists!"
    fi
}

# Function to show container status
show_status() {
    print_status "Container status:"
    docker-compose ps
    
    echo ""
    print_status "Application URLs:"
    echo "  - API: http://localhost:8002/api/"
    echo "  - Admin: http://localhost:8002/admin/"
    echo "  - Remote: http://5.104.84.97:8002/api/"
}

# Main execution
main() {
    print_status "Starting FreshBytes development setup..."
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Update Docker containers
    update_docker
    
    # Run database operations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Check superuser
    create_superuser
    
    # Show status
    show_status
    
    print_success "Setup completed! Your application is ready."
    print_status "To view logs: docker-compose logs -f web"
    print_status "To stop: docker-compose down"
}

# Check if script is run with arguments
case "${1:-}" in
    "migrate-only")
        check_docker
        check_docker_compose
        run_migrations
        ;;
    "docker-only")
        check_docker
        check_docker_compose
        update_docker
        ;;
    "status")
        docker-compose ps
        ;;
    "logs")
        docker-compose logs -f web
        ;;
    "stop")
        docker-compose down
        print_success "Containers stopped!"
        ;;
    "restart")
        docker-compose restart web
        print_success "Web container restarted!"
        ;;
    *)
        main
        ;;
esac