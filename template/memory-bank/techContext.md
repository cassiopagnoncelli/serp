# Tech Context: Serp Template

## Technology Stack

### Core Framework
- **FastAPI**: Modern async web framework for Python APIs
- **Uvicorn**: ASGI server for high-performance serving
- **Python 3.13+**: Latest Python with enhanced async capabilities

### Database & ORM
- **PostgreSQL**: Primary database with advanced features
- **Tortoise ORM**: Async ORM inspired by Django ORM
- **Aerich**: Database migration tool for Tortoise
- **asyncpg**: High-performance async PostgreSQL driver

### Authentication & Security
- **PyJWT**: JSON Web Token implementation
- **Passlib**: Password hashing library
- **bcrypt**: Secure password hashing algorithm
- **OAuth2**: Social login support (Google, Facebook)

### Background Processing
- **Celery**: Distributed task queue
- **Redis**: Message broker and cache
- **Flower**: Celery monitoring tool (dev dependency)

### Email & Communication
- **FastAPI-Mail**: Email handling for FastAPI
- **SendGrid**: Email delivery service
- **Jinja2**: Template engine for emails

### File Storage
- **MinIO**: S3-compatible object storage
- **boto3**: AWS SDK for Python
- **Wand**: ImageMagick binding for image processing

### Development Tools
- **Poetry**: Dependency management and packaging
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **VCR.py**: HTTP interaction recording for tests
- **IPython**: Enhanced interactive shell
- **ipdb**: Interactive debugger

### Additional Libraries
- **Pydantic**: Data validation and settings management
- **SQLModel**: SQL database toolkit with Pydantic integration
- **Requests**: HTTP library for external API calls
- **WebSockets**: Real-time communication support
- **User-Agents**: User agent parsing
- **GeoIP2**: IP geolocation
- **Colorama**: Cross-platform colored terminal text

## Development Setup

### Environment Management
- **Virtual Environment**: `venv/` directory with Python 3.13+
- **Environment Variables**: `.env.{environment}` files for configuration
- **Settings Management**: Pydantic Settings for type-safe configuration

### Project Commands
The `serp` command provides Rails-like development tools:

```bash
# Development workflow
serp console          # Interactive REPL (like rails console)
serp db               # Database CLI (psql)
serp redis            # Redis CLI
serp test             # Run test suite
serp test path/file   # Run specific tests

# Database operations
serp dbcreate         # Create database
serp dbdrop           # Drop database
serp dbload           # Load schema and migrations

# Background processing
serp worker           # Start Celery worker
serp cron             # Start Celery cron jobs

# Utilities
serp env              # Show current environment
serp secret           # Generate secret key
serp tasks            # List available tasks
serp task <name>      # Execute specific task
```

### Configuration Structure
```
config/
├── *.yml             # Service configurations (database, redis, etc.)
└── core/             # Python configuration modules
    ├── settings.py   # Main settings class
    ├── tortoise_db.py # Database configuration
    ├── redis_manager.py # Redis setup
    └── ...           # Other service configs
```

## Technical Constraints

### Version Requirements
- **Python**: `>=3.13,<4.0` (leverages latest async improvements)
- **FastAPI**: `<1.0.0` (pre-1.0 for stability)
- **Pydantic**: `<3.0.0` (v2.x series)
- **Tortoise ORM**: `0.20.0` (specific version for compatibility)

### Database Requirements
- **PostgreSQL**: Required for production
- **SQLite**: Supported for testing via aiosqlite
- **Connection Pooling**: Managed by Tortoise ORM
- **Async Only**: All database operations must be async

### Memory and Performance
- **Async Architecture**: Non-blocking I/O throughout
- **Connection Limits**: Managed by ORM connection pools
- **Background Processing**: Heavy operations offloaded to Celery
- **Caching**: Redis for session storage and caching

## Dependencies Architecture

### Production Dependencies
```toml
# Core framework
fastapi[standard] < 1.0.0
uvicorn
pydantic < 3.0.0

# Database
tortoise-orm[postgresql] = 0.20.0
aerich >= 0.7.0
asyncpg >= 0.30.0

# Background processing
celery < 6.0.0
redis < 7.0.0

# Authentication
pyjwt < 3.0.0
passlib < 2.0.0
```

### Development Dependencies
```toml
# Monitoring
flower < 3.0.0

# Code quality
pylint >= 3.3.7
```

### Test Dependencies
```toml
# Testing framework
pytest < 9.0.0
pytest-asyncio >= 0.23.0
vcrpy >= 7.0.0
```

## Tool Usage Patterns

### Development Workflow
1. **Environment Setup**: Activate venv, load environment variables
2. **Database Operations**: Use `serp db*` commands for schema management
3. **Testing**: `serp test` with comprehensive async test support
4. **Console Development**: `serp console` for interactive development
5. **Background Jobs**: `serp worker` for local job processing

### Configuration Management
- **Environment-specific**: Different configs for dev/test/prod
- **Type Safety**: Pydantic Settings ensure proper typing
- **Validation**: Configuration validated at startup
- **Hot Reloading**: Development server reloads on changes

### Database Development
- **Migration-driven**: Aerich manages schema changes
- **Async ORM**: All queries use async/await patterns
- **Connection Management**: Automatic pooling and cleanup
- **Multi-environment**: Separate databases per environment

### Testing Strategy
- **Async Tests**: pytest-asyncio for async test functions
- **HTTP Mocking**: VCR.py for external API testing
- **Factory Pattern**: Test factories for model creation
- **Isolation**: Each test gets clean database state

## Deployment Considerations
- **Docker Support**: Dockerfile included for containerization
- **Environment Variables**: 12-factor app configuration
- **Process Management**: Separate processes for web server and workers
- **Health Checks**: Built-in endpoints for monitoring
- **Static Assets**: Served efficiently in production
