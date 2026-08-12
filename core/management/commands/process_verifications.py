import logging
from django.core.management.base import BaseCommand
from django.db import models
from core.models import Post
from ai_verify.verification import GeminiVerifier
from core.utils import keyword_verify

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process pending AI verifications for posts'

    def handle(self, *args, **options):
        logger.info("🚀 Starting verification process...")
        self.stdout.write("🔍 Checking for pending posts...")

        # ---- STEP 1: Find ALL pending posts ----
        # Posts with verification_status='pending' and have an image (file or URL)
        pending_posts = Post.objects.filter(
            verification_status='pending'
        ).filter(
            models.Q(image__isnull=False) | models.Q(image_url__isnull=False)
        )[:10]  # Process up to 10 at a time

        total_posts = Post.objects.count()
        self.stdout.write(f"📊 Total posts in database: {total_posts}")

        if not pending_posts:
            # Check if there are any pending posts without images
            all_pending = Post.objects.filter(verification_status='pending').count()
            if all_pending > 0:
                self.stdout.write(f"⚠️ Found {all_pending} posts with status='pending', but none have images. Check your posts in admin.")
            else:
                self.stdout.write("📭 No posts with status='pending' found in database.")
            self.stdout.write("ℹ️  Make sure your posts have verification_status='pending' and an image.")
            return

        self.stdout.write(f"⏳ Found {pending_posts.count()} pending posts to process:")
        for p in pending_posts:
            self.stdout.write(f"   - {p.id}: caption='{p.caption[:30]}...', image={bool(p.image)}, image_url={p.image_url}")

        # ---- STEP 2: Initialize AI Verifier ----
        try:
            verifier = GeminiVerifier()
            use_gemini = True
            self.stdout.write("✅ Using Gemini AI verifier")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Gemini init failed: {e}. Using keyword fallback."))
            use_gemini = False

        # ---- STEP 3: Process each post ----
        processed_count = 0
        for post in pending_posts:
            self.stdout.write(f"\n🔄 Processing post {post.id}...")
            try:
                # Run verification
                if use_gemini:
                    result = verifier.verify_post(post)
                else:
                    result = keyword_verify(post)

                # ---- CRITICAL FIX: Set BOTH fields correctly ----
                # result.get('is_authentic') should be True/False
                # result.get('status') should be 'verified' or 'flagged'
                is_authentic = result.get('is_authentic', False)
                status = result.get('status', 'pending')

                post.is_verified = is_authentic          # Boolean
                post.verification_score = result.get('score', 0.0)
                post.verification_status = status        # String: 'verified' or 'flagged'

                # Award bonus points if verified
                if is_authentic:
                    bonus_points = 15
                    post.points = (post.points or 0) + bonus_points
                    # Also update user's total points
                    post.user.nature_points = (post.user.nature_points or 0) + bonus_points
                    post.user.save()
                    self.stdout.write(f"   ✅ Verified! +{bonus_points} points awarded")
                else:
                    self.stdout.write(f"   ⚠️ Verification failed or flagged")

                post.save()
                processed_count += 1
                self.stdout.write(f"   ✅ Updated: is_verified={post.is_verified}, status='{post.verification_status}', score={post.verification_score:.2f}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Failed: {e}"))
                # Don't stop; continue with next post

        # ---- STEP 4: Summary ----
        self.stdout.write(f"\n📊 Processed {processed_count} out of {pending_posts.count()} posts.")
        remaining = Post.objects.filter(verification_status='pending').count()
        if remaining > 0:
            self.stdout.write(f"⏳ {remaining} posts still pending (will process next run).")
        else:
            self.stdout.write("✅ All pending posts processed!")

        logger.info(f"✅ Processed {processed_count} posts")