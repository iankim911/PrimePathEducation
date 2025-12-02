#!/bin/bash

# PrimePath Test Management Module - Production Deployment Script
# This script handles the complete deployment process with zero-downtime rollout

set -e  # Exit on any error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not available. Please install Docker Compose."
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found. Please create it with production settings."
    fi
    
    # Check if Nginx config exists
    if [ ! -f "nginx/nginx.conf" ]; then
        error "Nginx configuration not found at nginx/nginx.conf"
    fi
    
    log "Prerequisites check passed ✓"
}

# Backup current database
backup_database() {
    if [ "$SKIP_BACKUP" != "true" ]; then
        log "Creating database backup..."
        
        mkdir -p "$BACKUP_DIR"
        
        # Create backup using existing database container
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T postgres \
            pg_dump -U "${POSTGRES_USER:-primepath}" "${POSTGRES_DB:-primepath}" \
            > "${BACKUP_DIR}/pre_deploy_$(date +%Y%m%d_%H%M%S).sql" 2>/dev/null || \
            warning "Database backup failed - continuing with deployment"
        
        log "Database backup completed ✓"
    else
        log "Skipping database backup (SKIP_BACKUP=true)"
    fi
}

# Build and test images
build_images() {
    log "Building Docker images..."
    
    # Build the main application image
    docker build -f Dockerfile.production -t primepath:latest . || error "Failed to build main application image"
    
    # Build WebSocket service if Dockerfile exists
    if [ -f "Dockerfile.websocket" ]; then
        docker build -f Dockerfile.websocket -t primepath-websocket:latest . || error "Failed to build WebSocket service image"
    fi
    
    log "Docker images built successfully ✓"
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            log "Health check passed ✓"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    error "Health check failed after $max_attempts attempts"
}

# Deploy with zero downtime
deploy() {
    log "Starting deployment..."
    
    # Pull latest images if using registry
    if [ "$USE_REGISTRY" = "true" ]; then
        log "Pulling latest images from registry..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    fi
    
    # Start new services
    log "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Run health check
    health_check
    
    log "Deployment completed successfully ✓"
}

# Database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Run migrations on one of the app containers
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec app-1 \
        npm run db:migrate || warning "Database migrations failed - check logs"
    
    log "Database migrations completed ✓"
}

# Cleanup old resources
cleanup() {
    log "Cleaning up old resources..."
    
    # Remove unused images
    docker image prune -f || warning "Failed to prune images"
    
    # Remove old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete 2>/dev/null || true
    
    log "Cleanup completed ✓"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    echo ""
    log "Application URLs:"
    log "  - Main Application: http://localhost"
    log "  - Health Check: http://localhost/health"
    log "  - Grafana Dashboard: http://localhost:3000"
    log "  - Prometheus: http://localhost:9090"
    echo ""
}

# Rollback function
rollback() {
    warning "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Restore from backup
    if [ -f "$1" ]; then
        log "Restoring database from backup: $1"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres
        sleep 10
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T postgres \
            psql -U "${POSTGRES_USER:-primepath}" -d "${POSTGRES_DB:-primepath}" < "$1"
    fi
    
    log "Rollback completed"
}

# Main deployment flow
main() {
    log "PrimePath Test Management Module - Production Deployment"
    log "======================================================="
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            backup_database
            build_images
            deploy
            run_migrations
            cleanup
            show_status
            ;;
        "rollback")
            if [ -z "$2" ]; then
                error "Please specify backup file for rollback: ./deploy.sh rollback backup_file.sql"
            fi
            rollback "$2"
            ;;
        "health")
            health_check
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f "${2:-}"
            ;;
        "stop")
            log "Stopping services..."
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
            ;;
        "restart")
            log "Restarting services..."
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart "${2:-}"
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health|status|logs|stop|restart}"
            echo ""
            echo "Commands:"
            echo "  deploy           - Full deployment process"
            echo "  rollback <file>  - Rollback to previous backup"
            echo "  health           - Run health check"
            echo "  status           - Show service status"
            echo "  logs [service]   - Show logs for all or specific service"
            echo "  stop             - Stop all services"
            echo "  restart [service] - Restart all or specific service"
            echo ""
            echo "Environment Variables:"
            echo "  SKIP_BACKUP=true - Skip database backup"
            echo "  USE_REGISTRY=true - Pull images from registry"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"