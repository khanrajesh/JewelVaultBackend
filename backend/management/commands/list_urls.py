from django.core.management.base import BaseCommand
from django.urls import get_resolver


def _iter_patterns(patterns, prefix=''):
    for p in patterns:
        if hasattr(p, 'url_patterns'):
            # include() -> recurse
            new_prefix = prefix + (p.pattern._route or '')
            yield from _iter_patterns(p.url_patterns, new_prefix)
        else:
            route = prefix + (p.pattern._route or '')
            yield route, getattr(p, 'name', None), getattr(p.callback, '__module__', '') + '.' + getattr(p.callback, '__name__', '')


class Command(BaseCommand):
    help = 'List all URL patterns (for debugging)'

    def handle(self, *args, **options):
        resolver = get_resolver()
        patterns = resolver.url_patterns
        for route, name, callback in _iter_patterns(patterns):
            self.stdout.write(f"{route} -> {name} -> {callback}")
