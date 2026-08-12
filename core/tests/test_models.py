from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Post, Challenge, Reward, Sponsor, Like

User = get_user_model()

class ModelTests(TestCase):
    """Test all models in the core app."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_post(self):
        """Test creating a post."""
        post = Post.objects.create(
            user=self.user,
            caption="Planted 10 trees in the community park!",
            hashtags="#TreePlanting #GreenEarth",
            location="Central Park",
            points=5
        )
        self.assertEqual(post.caption, "Planted 10 trees in the community park!")
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.verification_status, 'pending')
        self.assertFalse(post.is_verified)
        self.assertEqual(post.points, 5)

    def test_create_challenge(self):
        """Test creating a challenge."""
        challenge = Challenge.objects.create(
            title="Plant 100 Trees",
            description="Plant 100 trees in your local community.",
            category="environment",
            created_by=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            points_reward=20,
            is_active=True,
            status='pending'
        )
        self.assertEqual(challenge.title, "Plant 100 Trees")
        self.assertEqual(challenge.category, "environment")
        self.assertEqual(challenge.status, 'pending')
        self.assertEqual(challenge.points_reward, 20)

    def test_create_reward(self):
        """Test creating a reward."""
        reward = Reward.objects.create(
            name="$10 Gift Card",
            description="Amazon gift card worth $10",
            category="gift_card",
            points_cost=20,
            stock_quantity=10,
            is_active=True
        )
        self.assertEqual(reward.name, "$10 Gift Card")
        self.assertEqual(reward.points_cost, 20)
        self.assertEqual(reward.stock_quantity, 10)
        self.assertTrue(reward.is_active)

    def test_create_sponsor(self):
        """Test creating a sponsor."""
        sponsor = Sponsor.objects.create(
            name="GreenEarth Foundation",
            email="contact@greenearth.org",
            website="https://greenearth.org",
            contact_person="John Doe",
            is_active=True
        )
        self.assertEqual(sponsor.name, "GreenEarth Foundation")
        self.assertEqual(sponsor.email, "contact@greenearth.org")
        self.assertTrue(sponsor.is_active)

    def test_post_str_method(self):
        """Test the __str__ method of Post."""
        post = Post.objects.create(
            user=self.user,
            caption="Test caption for str method"
        )
        self.assertEqual(str(post), f"testuser - Test caption for str method")

    def test_challenge_get_progress(self):
        """Test getting progress for a challenge."""
        challenge = Challenge.objects.create(
            title="Test Challenge",
            description="Test description",
            category="environment",
            created_by=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            points_reward=10,
            is_active=True,
            status='approved'
        )
        # Create some verified posts for this challenge
        Post.objects.create(
            user=self.user,
            challenge=challenge,
            caption="Post 1",
            is_verified=True,
            verification_status='verified'
        )
        Post.objects.create(
            user=self.user,
            challenge=challenge,
            caption="Post 2",
            is_verified=True,
            verification_status='verified'
        )
        Post.objects.create(
            user=self.user,
            challenge=challenge,
            caption="Post 3",
            is_verified=False,
            verification_status='pending'
        )
        progress = challenge.get_progress(self.user)
        self.assertEqual(progress, 2)  # Only verified posts count

    def test_like_model(self):
        """Test the Like model."""
        post = Post.objects.create(
            user=self.user,
            caption="Test post for likes"
        )
        like = Like.objects.create(user=self.user, post=post)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, post)
        self.assertIsNotNone(like.created_at)