from django.db import migrations

def create_initial_achievements(apps, schema_editor):
    Achievement = apps.get_model('gamification', 'Achievement')
    
    achievements = [
        # Streak Achievements
        {
            'name': 'Getting Started',
            'description': 'Maintain a 3-day streak',
            'points': 50,
            'icon': 'fire',
            'achievement_type': 'streak',
            'required_count': 3
        },
        {
            'name': 'Consistency Champion',
            'description': 'Maintain a 7-day streak',
            'points': 100,
            'icon': 'fire',
            'achievement_type': 'streak',
            'required_count': 7
        },
        {
            'name': 'Habit Master',
            'description': 'Maintain a 30-day streak',
            'points': 500,
            'icon': 'fire',
            'achievement_type': 'streak',
            'required_count': 30
        },
        
        # Completion Achievements
        {
            'name': 'First Steps',
            'description': 'Complete your first standard or process',
            'points': 25,
            'icon': 'check',
            'achievement_type': 'completion',
            'required_count': 1
        },
        {
            'name': 'Progress Pioneer',
            'description': 'Complete 10 standards or processes',
            'points': 100,
            'icon': 'check',
            'achievement_type': 'completion',
            'required_count': 10
        },
        {
            'name': 'Achievement Hunter',
            'description': 'Complete 100 standards or processes',
            'points': 1000,
            'icon': 'check',
            'achievement_type': 'completion',
            'required_count': 100
        },
        
        # Level Achievements
        {
            'name': 'Level Up!',
            'description': 'Reach level 2',
            'points': 50,
            'icon': 'star',
            'achievement_type': 'level',
            'required_count': 2
        },
        {
            'name': 'Rising Star',
            'description': 'Reach level 5',
            'points': 200,
            'icon': 'star',
            'achievement_type': 'level',
            'required_count': 5
        },
        {
            'name': 'Master Achiever',
            'description': 'Reach level 10',
            'points': 1000,
            'icon': 'star',
            'achievement_type': 'level',
            'required_count': 10
        },
        
        # Special Achievements
        {
            'name': 'Goal Setter',
            'description': 'Complete your first BIG goal',
            'points': 500,
            'icon': 'trophy',
            'achievement_type': 'special',
            'required_count': 1
        },
        {
            'name': 'Milestone Maker',
            'description': 'Complete your first MTG',
            'points': 200,
            'icon': 'flag',
            'achievement_type': 'special',
            'required_count': 1
        }
    ]
    
    Achievement.objects.bulk_create([
        Achievement(**achievement) for achievement in achievements
    ])

def remove_initial_achievements(apps, schema_editor):
    Achievement = apps.get_model('gamification', 'Achievement')
    Achievement.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('gamification', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_achievements, remove_initial_achievements),
    ]
