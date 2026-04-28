from django.core.management.base import BaseCommand

from tourism.models import TempleGuide, TouristPlace
from tourism.temple_guide_data import TEMPLE_GUIDE_DATA


def normalize_lookup_key(value):
    return ''.join(ch for ch in value.lower() if ch.isalnum())


class Command(BaseCommand):
    help = 'Sync structured Mathura-Vrindavan temple guide data into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Syncing temple guide data...'))

        guide_count = 0
        place_updates = 0

        places = list(TouristPlace.objects.all())
        for item in TEMPLE_GUIDE_DATA:
            guide, _ = TempleGuide.objects.update_or_create(
                name=item['name'],
                defaults=item,
            )
            guide_count += 1

            match = self.find_matching_place(places, item['name'], item.get('aliases', []))
            if match:
                description = f"{item['famous_for']} {item['history']}".strip()
                timings = ', '.join(
                    f"{entry['session']}: {entry['timing']}"
                    for entry in item.get('timings', [])[:3]
                )
                match.description = description[: match._meta.get_field('description').max_length] if hasattr(match._meta.get_field('description'), 'max_length') and match._meta.get_field('description').max_length else description
                if timings:
                    match.visiting_hours = timings[:100]
                match.save(update_fields=['description', 'visiting_hours'])
                place_updates += 1

        self.stdout.write(self.style.SUCCESS(f'Synced {guide_count} temple guide records.'))
        self.stdout.write(self.style.SUCCESS(f'Updated {place_updates} matching tourist places with richer details.'))

    def find_matching_place(self, places, name, aliases):
        target_values = [name, *aliases]
        normalized_targets = {normalize_lookup_key(value) for value in target_values if value}
        for place in places:
            place_key = normalize_lookup_key(place.name)
            if place_key in normalized_targets:
                return place
        return None
