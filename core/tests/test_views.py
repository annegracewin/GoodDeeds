from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from core.models import Post, Challenge, Reward, ChallengeParticipant
from uuid import uuid4
import json

User = get_user_model()

class ViewTests(TestCase):
    """Test all API endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )

    # ---- Authentication Tests ----

    def test_user_registration(self):
        """Test user registration endpoint."""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        """Test user login."""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    # ---- Post Tests ----

    def test_create_post_authenticated(self):
        """Test creating a post when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/create/', {
            'caption': 'My good deed',
            'location': 'City Park',
            'hashtags': '#GoodDeed'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(caption='My good deed').exists())

    def test_create_post_unauthenticated(self):
        """Test creating a post when NOT logged in."""
        response = self.client.post('/api/create/', {
            'caption': 'My good deed'
        })
        # Should not be allowed
        self.assertNotEqual(response.status_code, 201)

    def test_feed_view(self):
        """Test the feed API endpoint."""
        self.client.login(username='testuser', password='testpass123')
        Post.objects.create(user=self.user, caption="Post 1", points=5)
        Post.objects.create(user=self.user, caption="Post 2", points=10)

        response = self.client.get('/api/feed/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_like_post(self):
        """Test liking a post."""
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(user=self.user, caption="Test post")
        response = self.client.post(f'/api/{post.id}/like/')
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.likes, 1)

    def test_unlike_post(self):
        """Test unliking a post (toggle)."""
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(user=self.user, caption="Test post")
        
        # Like first
        response = self.client.post(f'/api/{post.id}/like/')
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.likes, 1)
        
        # Unlike (click again)
        response = self.client.post(f'/api/{post.id}/like/')
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.likes, 0)

    # ---- Challenge Tests ----

    def test_list_challenges(self):
        """Test listing challenges."""
        Challenge.objects.create(
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
        response = self.client.get('/api/challenges/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_join_challenge(self):
        """Test joining a challenge."""
        self.client.login(username='testuser', password='testpass123')
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
        response = self.client.post(f'/api/challenges/{challenge.id}/join/')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ChallengeParticipant.objects.filter(
            challenge=challenge, user=self.user
        ).exists())

    # ---- Reward Tests ----

    def test_list_rewards(self):
        """Test listing rewards."""
        Reward.objects.create(
            name="Test Reward",
            description="Test description",
            category="gift_card",
            points_cost=10,
            stock_quantity=5,
            is_active=True
        )
        response = self.client.get('/api/rewards/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    # ---- Admin Panel Tests ----

    def test_admin_panel_requires_staff(self):
        """Test that admin panel requires staff access."""
        response = self.client.get('/admin-panel/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_admin_panel_staff_access(self):
        """Test that staff can access admin panel."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 200)