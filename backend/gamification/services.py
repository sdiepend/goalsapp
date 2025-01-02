from django.utils import timezone
from .models import UserProfile, Achievement, UserAchievement, PointTransaction

class PointCalculator:
    """Base point values and multipliers"""
    STANDARD_POINTS = 10
    PROCESS_POINTS = 15
    MTG_POINTS = 100
    BIG_POINTS = 500
    
    # Streak multipliers
    STREAK_MULTIPLIERS = {
        3: 1.2,   # 3 days: 20% bonus
        7: 1.5,   # 7 days: 50% bonus
        14: 1.8,  # 14 days: 80% bonus
        30: 2.0,  # 30 days: 100% bonus
        60: 2.5,  # 60 days: 150% bonus
        90: 3.0   # 90 days: 200% bonus
    }

class GamificationService:
    def __init__(self, user):
        self.user = user
        self.profile, _ = UserProfile.objects.get_or_create(user=user)

    def get_streak_multiplier(self):
        """Calculate streak multiplier based on current streak"""
        streak = self.profile.current_streak
        multiplier = 1.0
        
        for days, value in sorted(PointCalculator.STREAK_MULTIPLIERS.items()):
            if streak >= days:
                multiplier = value
            else:
                break
                
        return multiplier

    def award_points(self, points, transaction_type, reference_id=None, reference_type=None, description=None):
        """Award points and create transaction record"""
        multiplier = self.get_streak_multiplier()
        
        transaction = PointTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type=transaction_type,
            reference_id=reference_id,
            reference_type=reference_type,
            streak_multiplier=multiplier,
            description=description or f'Completed {transaction_type}'
        )
        
        # Update streak
        self.profile.update_streak(timezone.now().date())
        
        # Check for achievements
        self.check_achievements()
        
        return transaction

    def complete_standard(self, standard):
        """Award points for completing a standard"""
        return self.award_points(
            PointCalculator.STANDARD_POINTS,
            'standard',
            reference_id=standard.id,
            reference_type='standard',
            description=f'Completed standard: {standard.title}'
        )

    def complete_process(self, process_progress):
        """Award points for completing a daily process"""
        return self.award_points(
            PointCalculator.PROCESS_POINTS,
            'process',
            reference_id=process_progress.process.id,
            reference_type='process',
            description=f'Completed process: {process_progress.process.title}'
        )

    def complete_mtg(self, mtg):
        """Award points for completing a medium-term goal"""
        return self.award_points(
            PointCalculator.MTG_POINTS,
            'mtg',
            reference_id=mtg.id,
            reference_type='mtg',
            description=f'Completed MTG: {mtg.title}'
        )

    def complete_big(self, big):
        """Award points for completing a big goal"""
        return self.award_points(
            PointCalculator.BIG_POINTS,
            'big',
            reference_id=big.id,
            reference_type='big',
            description=f'Completed BIG goal: {big.title}'
        )

    def check_achievements(self):
        """Check and award any newly unlocked achievements"""
        # Get all unearned achievements
        earned_ids = UserAchievement.objects.filter(
            user=self.user
        ).values_list('achievement_id', flat=True)
        
        potential_achievements = Achievement.objects.exclude(
            id__in=earned_ids
        )
        
        for achievement in potential_achievements:
            if self.check_achievement_requirements(achievement):
                self.award_achievement(achievement)

    def check_achievement_requirements(self, achievement):
        """Check if user meets requirements for an achievement"""
        if achievement.achievement_type == 'streak':
            return self.profile.current_streak >= achievement.required_count
            
        elif achievement.achievement_type == 'completion':
            count = PointTransaction.objects.filter(
                user=self.user,
                transaction_type__in=['standard', 'process', 'mtg', 'big']
            ).count()
            return count >= achievement.required_count
            
        elif achievement.achievement_type == 'level':
            return self.profile.level >= achievement.required_count
            
        return False

    def award_achievement(self, achievement):
        """Award an achievement and its points"""
        UserAchievement.objects.create(
            user=self.user,
            achievement=achievement
        )
        
        self.award_points(
            achievement.points,
            'achievement',
            reference_id=achievement.id,
            reference_type='achievement',
            description=f'Unlocked achievement: {achievement.name}'
        )
