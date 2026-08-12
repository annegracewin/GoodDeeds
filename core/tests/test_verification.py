from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Post
from core.utils import keyword_verify

User = get_user_model()

class VerificationTests(TestCase):
    """Test the verification system."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_keyword_verify_two_keywords(self):
        """Test keyword verification with 2+ keywords."""
        post = Post.objects.create(
            user=self.user,
            caption="I planted trees and cleaned the beach today!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.8)
        self.assertEqual(result['status'], 'verified')
        self.assertIn('plant', result['details']['keywords'])
        self.assertIn('clean', result['details']['keywords'])

    def test_keyword_verify_one_keyword(self):
        """Test keyword verification with exactly 1 keyword."""
        # "cleaned" is the only keyword here
        post = Post.objects.create(
            user=self.user,
            caption="I cleaned the house today!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.6)  # Exactly 1 keyword → 0.6
        self.assertEqual(result['status'], 'verified')

    def test_keyword_verify_no_keywords(self):
        """Test keyword verification with 0 keywords."""
        post = Post.objects.create(
            user=self.user,
            caption="I had a nice day today.",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertFalse(result['is_authentic'])
        self.assertEqual(result['score'], 0.2)
        self.assertEqual(result['status'], 'flagged')
        self.assertEqual(len(result['details']['keywords']), 0)

    def test_keyword_verify_specific_keywords(self):
        """Test that specific keywords are detected correctly."""
        # Test with "plant" only
        post = Post.objects.create(
            user=self.user,
            caption="I am doing plant work today!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.6)  # Exactly 1 keyword
        
        # Test with "plant" and "tree"
        post2 = Post.objects.create(
            user=self.user,
            caption="I am doing plant and tree work today!",
            verification_status='pending'
        )
        result2 = keyword_verify(post2)
        self.assertTrue(result2['is_authentic'])
        self.assertEqual(result2['score'], 0.8)  # 2 keywords
        
        # Test with no keywords
        post3 = Post.objects.create(
            user=self.user,
            caption="Random text with no keywords",
            verification_status='pending'
        )
        result3 = keyword_verify(post3)
        self.assertFalse(result3['is_authentic'])
        self.assertEqual(result3['score'], 0.2)
        self.assertEqual(result3['status'], 'flagged')

    def test_threshold_values(self):
        """Test that scores match the expected thresholds."""
        # 2+ keywords → score 0.8
        post1 = Post.objects.create(
            user=self.user,
            caption="I planted trees and cleaned the beach",
            verification_status='pending'
        )
        result1 = keyword_verify(post1)
        self.assertEqual(result1['score'], 0.8)
        
        # 1 keyword → score 0.6
        post2 = Post.objects.create(
            user=self.user,
            caption="I cleaned the house",
            verification_status='pending'
        )
        result2 = keyword_verify(post2)
        self.assertEqual(result2['score'], 0.6)
        
        # 0 keywords → score 0.2
        post3 = Post.objects.create(
            user=self.user,
            caption="Random text",
            verification_status='pending'
        )
        result3 = keyword_verify(post3)
        self.assertEqual(result3['score'], 0.2)