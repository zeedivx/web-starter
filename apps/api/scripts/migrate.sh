#!/usr/bin/env bash
# Migration management script

set -e

COMMAND=${1:-help}

case $COMMAND in
    create)
        if [ -z "$2" ]; then
            echo "Error: Migration message required"
            echo "Usage: ./scripts/migrate.sh create 'migration message'"
            exit 1
        fi
        echo "Creating migration: $2"
        uv run alembic revision --autogenerate -m "$2"
        ;;

    upgrade)
        echo "Running migrations..."
        uv run alembic upgrade head
        ;;

    downgrade)
        STEPS=${2:-1}
        echo "Downgrading $STEPS migration(s)..."
        uv run alembic downgrade -$STEPS
        ;;

    history)
        echo "Migration history:"
        uv run alembic history --verbose
        ;;

    current)
        echo "Current migration:"
        uv run alembic current
        ;;

    reset)
        echo "Resetting database to base..."
        uv run alembic downgrade base
        ;;

    help)
        echo "Migration Management Script"
        echo ""
        echo "Usage: ./scripts/migrate.sh [command] [args]"
        echo ""
        echo "Commands:"
        echo "  create 'message'  - Create new migration with autogenerate"
        echo "  upgrade           - Run all pending migrations"
        echo "  downgrade [n]     - Downgrade n migrations (default: 1)"
        echo "  history           - Show migration history"
        echo "  current           - Show current migration"
        echo "  reset             - Downgrade all migrations to base"
        echo "  help              - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/migrate.sh create 'add users table'"
        echo "  ./scripts/migrate.sh upgrade"
        echo "  ./scripts/migrate.sh downgrade 2"
        ;;

    *)
        echo "Unknown command: $COMMAND"
        echo "Run './scripts/migrate.sh help' for usage"
        exit 1
        ;;
esac
