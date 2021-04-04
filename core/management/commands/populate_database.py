from django.core.management.base import BaseCommand, CommandError
import os
import environ

env = environ.Env(
    DEBUG=(bool, False)
)


class Command(BaseCommand):
    help = 'Imports postgresql dump into postgresql database'

    def handle(self, *args, **options):
        os.system(f"psql -U {env('DB_USERNAME')} password={env('DB_PASSWORD')} -c 'CREATE DATABASE {env('DB_NAME')}'")
        os.system(f"psql -U {env('DB_USERNAME')} -d {env('DB_NAME')} -f schema.sql")
        self.stdout.write(self.style.SUCCESS('Done'))
