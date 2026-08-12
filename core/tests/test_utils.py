# core/tests/test_utils.py
"""
Tests for core/utils.py
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Post
from core.utils import keyword_verify

User = get_user_model()

class UtilsTests(TestCase):
    """Test all utility functions."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_keyword_verify_two_keywords(self):
        """Test keyword_verify with 2+ keywords."""
        post = Post.objects.create(
            user=self.user,
            caption="I planted trees and cleaned the beach!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.8)
        self.assertEqual(result['status'], 'verified')
        self.assertIn('plant', result['details']['keywords'])
        self.assertIn('clean', result['details']['keywords'])

    def test_keyword_verify_one_keyword(self):
        """Test keyword_verify with exactly 1 keyword."""
        post = Post.objects.create(
            user=self.user,
            caption="I cleaned the house today!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.6)
        self.assertEqual(result['status'], 'verified')
        self.assertIn('clean', result['details']['keywords'])

    def test_keyword_verify_no_keywords(self):
        """Test keyword_verify with 0 keywords."""
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

    def test_keyword_verify_duplicate_keywords(self):
        """Test keyword_verify with duplicate keywords."""
        post = Post.objects.create(
            user=self.user,
            caption="I helped help helping helpers!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.6)  # Only 'help' is in the list
        self.assertEqual(len(result['details']['keywords']), 1)
        self.assertIn('help', result['details']['keywords'])

    def test_keyword_verify_case_insensitive(self):
        """Test that keyword_verify is case insensitive."""
        post = Post.objects.create(
            user=self.user,
            caption="I PLANTED A TREE today!",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        # 'plant' and 'tree' → 2 keywords → 0.8
        self.assertEqual(result['score'], 0.8)

    def test_keyword_verify_all_keywords(self):
        """Test keyword_verify with all keywords."""
        all_keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                        'blood', 'tree', 'food', 'education', 'health', 'recycle']
        caption = "I " + " ".join(all_keywords) + " today!"
        post = Post.objects.create(
            user=self.user,
            caption=caption,
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        self.assertEqual(result['score'], 0.8)
        self.assertEqual(len(result['details']['keywords']), len(all_keywords))

    def test_keyword_verify_partial_matches(self):
        """Test that partial word matches don't trigger."""
        # "planting" contains "plant" → should match
        post1 = Post.objects.create(
            user=self.user,
            caption="I am planting seeds!",
            verification_status='pending'
        )
        result1 = keyword_verify(post1)
        self.assertTrue(result1['is_authentic'])
        
        # "plate" does NOT contain "plant" → should not match
        post2 = Post.objects.create(
            user=self.user,
            caption="I am eating from a plate!",
            verification_status='pending'
        )
        result2 = keyword_verify(post2)
        self.assertFalse(result2['is_authentic'])
        self.assertEqual(result2['score'], 0.2)

    def test_keyword_verify_empty_caption(self):
        """Test keyword_verify with empty caption."""
        post = Post.objects.create(
            user=self.user,
            caption="",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertFalse(result['is_authentic'])
        self.assertEqual(result['score'], 0.2)
        self.assertEqual(result['status'], 'flagged')

    def test_keyword_verify_special_characters(self):
        """Test keyword_verify with special characters in caption."""
        post = Post.objects.create(
            user=self.user,
            caption="I planted trees! 🌳 #TreePlanting #GreenEarth",
            verification_status='pending'
        )
        result = keyword_verify(post)
        self.assertTrue(result['is_authentic'])
        # 'plant' and 'tree' → 2 keywords → 0.8
        self.assertEqual(result['score'], 0.8)