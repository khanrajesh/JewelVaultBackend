import json
import subprocess
import shlex
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

OPENAPI_PATH = Path(__file__).resolve().parents[3] / "openapi.json"

class Command(BaseCommand):
    help = 'Validate backend/openapi.json and optionally regenerate using configured command.'

    def add_arguments(self, parser):
        parser.add_argument('--regen', action='store_true', help='Run configured generator command to recreate openapi.json')

    def handle(self, *args, **options):
        regen = options.get('regen')

        if regen:
            gen_cmd = getattr(settings, 'OPENAPI_GENERATE_CMD', None)
            if not gen_cmd:
                self.stderr.write('No OPENAPI_GENERATE_CMD configured in settings. Set it to a shell command that regenerates openapi.json')
                return
            self.stdout.write(f'Running generator: {gen_cmd}')
            try:
                subprocess.check_call(shlex.split(gen_cmd))
            except subprocess.CalledProcessError as exc:
                self.stderr.write(f'Generator command failed: {exc}')
                return

        if not OPENAPI_PATH.exists():
            self.stderr.write(f'OpenAPI file not found at {OPENAPI_PATH}')
            return

        try:
            data = json.loads(OPENAPI_PATH.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            self.stderr.write(f'Invalid JSON in openapi.json: {exc}')
            return

        if not isinstance(data, dict) or 'openapi' not in data:
            self.stderr.write('openapi.json does not look like a valid OpenAPI document (missing "openapi" key)')
            return

        self.stdout.write(self.style.SUCCESS('openapi.json appears valid'))
