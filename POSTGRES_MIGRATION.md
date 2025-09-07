# PostgreSQL Migration Guide

This guide will help you migrate your Django loan management system from SQLite to PostgreSQL on Render.

## Step 1: Create PostgreSQL Database on Render

### Render PostgreSQL Configuration

When creating your PostgreSQL database on Render, use these settings:

- **Name**: `prestamos-postgresql-db`
- **Project**: Create new project "prestamos-app"
- **Database**: `prestamos_db` (or leave blank for auto-generated)
- **User**: `prestamos_user` (or leave blank for auto-generated)
- **Region**: Oregon (US West)
- **PostgreSQL Version**: 17
- **Plan**: Free
- **Storage**: 1 GB
- **High Availability**: Disabled

## Step 2: Update Your Render Service

1. Go to your existing web service on Render
2. In the Environment section, add these environment variables:
   - `DATABASE_URL`: Copy the connection string from your PostgreSQL database
   - Update `CSRF_TRUSTED_ORIGINS` to include your domain

## Step 3: Deploy and Migrate

### Option A: Fresh Deploy (Recommended for production)

1. **Deploy your service** with the new PostgreSQL configuration
2. **Run migrations** on the new database:
   ```bash
   python manage.py migrate
   ```
3. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

### Option B: Data Migration (If you have existing data)

1. **Export data from SQLite** (run locally):
   ```bash
   python migrate_to_postgres.py export
   ```

2. **Deploy your service** with PostgreSQL

3. **Import data to PostgreSQL** (run on Render or locally with DATABASE_URL set):
   ```bash
   python migrate_to_postgres.py import
   ```

## Step 4: Verify Migration

1. **Check database connection**:
   ```bash
   python manage.py dbshell
   ```

2. **Verify data**:
   - Check that all clients, loans, and payments are present
   - Test the admin interface
   - Verify all functionality works

## Environment Variables

Your production environment should have:

```bash
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.onrender.com
DATABASE_URL=postgres://username:password@host:port/database_name
CSRF_TRUSTED_ORIGINS=https://your-domain.onrender.com
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Check that DATABASE_URL is correctly set
2. **SSL errors**: Your settings.py already handles SSL requirements
3. **Migration errors**: Ensure all dependencies are installed

### Useful Commands

```bash
# Check database connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check installed apps
python manage.py check

# Collect static files
python manage.py collectstatic
```

## Benefits of PostgreSQL

- **Better performance** for complex queries
- **ACID compliance** for data integrity
- **Concurrent access** support
- **Advanced data types** and indexing
- **Better scalability** for production use

## Next Steps

After successful migration:

1. **Monitor performance** using Render's metrics
2. **Set up backups** (available in paid plans)
3. **Consider upgrading** to a paid plan for production use
4. **Implement monitoring** and logging

Your Django application is already well-configured for PostgreSQL migration!
