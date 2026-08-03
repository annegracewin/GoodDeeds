from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Post, Challenge, ChallengeParticipant
from .serializers import (
    PostSerializer, UserSerializer, 
    ChallengeSerializer, ChallengeParticipantSerializer
)

# Import the AI verifier (you need to create this file)
try:
    from ai_verify.verification import GeminiVerifier
    VERIFIER_AVAILABLE = True
except ImportError:
    VERIFIER_AVAILABLE = False
    # Fallback to keyword-based verification
    from .utils import keyword_verify

User = get_user_model()

# ============================================================
# FEED VIEW
# ============================================================
class FeedView(generics.ListAPIView):
    """
    Get posts with filtering by type: all, verified, trending
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Post.objects.all()
        feed_type = self.request.query_params.get('type', 'all')
        if feed_type == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif feed_type == 'trending':
            queryset = queryset.filter(likes__gte=5).order_by('-likes', '-created_at')
        return queryset.order_by('-created_at')


# ============================================================
# USER LIST (for dynamic stories)
# ============================================================
class UserListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ============================================================
# CREATE POST (requires login)
# ============================================================
@api_view(['POST'])
@login_required
def create_post(request):
    """
    Create a new post. The user is taken from the request.
    """
    data = request.data
    post = Post.objects.create(
        user=request.user,
        image_url=data.get('image_url', 'https://picsum.photos/800/600'),
        caption=data.get('caption', ''),
        hashtags=data.get('hashtags', ''),
        location=data.get('location', ''),
        points=5  # Base points
    )
    # Optionally trigger AI verification asynchronously later
    return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


# ============================================================
# LIKE POST (requires login)
# ============================================================
@api_view(['POST'])
@login_required
def like_post(request, post_id):
    """
    Increment the like count for a post.
    """
    try:
        post = Post.objects.get(id=post_id)
        post.likes += 1
        post.save()
        return Response({'likes': post.likes, 'message': 'Liked!'})
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# AI VERIFICATION (real with Gemini, fallback to keywords)
# ============================================================
@api_view(['POST'])
@login_required
def verify_post(request, post_id):
    """
    Run AI verification on a post.
    Uses Gemini if available, otherwise falls back to keyword check.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    # Use real verifier if available
    if VERIFIER_AVAILABLE:
        verifier = GeminiVerifier()
        result = verifier.verify_post(post)
    else:
        # Fallback: keyword verification
        result = keyword_verify(post)

    # Update post
    post.is_verified = result.get('is_authentic', False)
    post.verification_score = result.get('score', 0.0)
    post.verification_status = result.get('status', 'pending')
    if result.get('is_authentic', False):
        post.points += 15  # Bonus for verified posts
    post.save()

    return Response({
        'is_verified': post.is_verified,
        'verification_score': post.verification_score,
        'verification_status': post.verification_status,
        'points': post.points,
        'details': result.get('details', {})
    })


# ============================================================
# CHALLENGES
# ============================================================

class ChallengeListView(generics.ListAPIView):
    """
    List all active challenges, optionally filtered by category or featured.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        queryset = Challenge.objects.filter(is_active=True, end_date__gte=timezone.now())
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        return queryset.order_by('-created_at')


@api_view(['POST'])
@login_required
def create_challenge(request):
    """
    Create a new challenge.
    """
    data = request.data
    challenge = Challenge.objects.create(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category', 'community'),
        created_by=request.user,
        start_date=data.get('start_date', timezone.now()),
        end_date=data.get('end_date', timezone.now() + timezone.timedelta(days=30)),
        points_reward=data.get('points_reward', 10),
        image=data.get('image', 'https://picsum.photos/800/400'),
    )
    return Response(ChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@login_required
def join_challenge(request, challenge_id):
    """
    Join a challenge.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Check if already joined
    if ChallengeParticipant.objects.filter(challenge=challenge, user=request.user).exists():
        return Response(
            {'message': 'Already joined this challenge'},
            status=status.HTTP_400_BAD_REQUEST
        )

    participant = ChallengeParticipant.objects.create(
        challenge=challenge,
        user=request.user,
        status='registered'
    )

    challenge.participants_count += 1
    challenge.save()

    return Response(
        ChallengeParticipantSerializer(participant).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@login_required
def my_challenges(request):
    """
    Get all challenges the logged-in user has joined.
    """
    participants = ChallengeParticipant.objects.filter(user=request.user)
    return Response(ChallengeParticipantSerializer(participants, many=True).data)