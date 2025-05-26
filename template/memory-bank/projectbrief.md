# Project Brief: Serp Template

## Overview
Serp is a full-featured Python API template that provides a complete foundation for building modern web applications. It combines enterprise-grade features in a Rails-inspired structure, offering developers a robust starting point for API development.

## Core Requirements

### Primary Features
- **ASGI Server**: FastAPI-based modern async web framework
- **Database Management**: Tortoise ORM with PostgreSQL support and migrations via Aerich
- **Authentication System**: JWT-based auth with social login (Google, Facebook)
- **Background Processing**: Celery-based job queue with Redis broker
- **Email Service**: Integrated mailer with template support
- **Storage Service**: File storage capabilities with MinIO/S3 support
- **Testing Framework**: Comprehensive test suite with pytest
- **Development Tools**: Console, linting, documentation, build tools
- **AI Integration**: Built-in AI tools support

### Architecture Goals
- **Rails-like Structure**: Familiar MVC-inspired organization (app/, lib/, config/, tests/, bin/)
- **Modular Design**: Clear separation of concerns with dedicated directories
- **Production Ready**: Environment-specific configurations and deployment tools
- **Developer Experience**: Rich console, debugging tools, and comprehensive testing

### Key Constraints
- Python 3.13+ requirement
- PostgreSQL as primary database
- Redis for caching and job queuing
- FastAPI for API framework
- Tortoise ORM for database operations

## Success Criteria
- Functional API with authentication
- Working background job processing
- Email delivery capabilities
- Comprehensive test coverage
- Production deployment readiness
- Clear development workflow

## Project Scope
This is a **template project** - a foundation that developers can clone and extend for their specific needs. It provides all the boilerplate and infrastructure code while remaining flexible for customization.
