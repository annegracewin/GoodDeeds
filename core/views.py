from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import RewardSerializer, RewardRedemptionSerializer
from .models import Like, Reward, RewardRedemption

import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

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



logger = logging.getLogger(__name__)

# ============================================================
# FEED VIEW
# ============================================================
class FeedView(generics.ListAPIView):
    """
    Get posts with filtering by type: all, verified, trending
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
   
    def get_serializer_context(self):
        return {'request': self.request}
    
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
@permission_classes([IsAuthenticated])
def create_post(request):
    try:
        caption = request.data.get('caption', '').strip()
        location = request.data.get('location', '').strip()
        hashtags = request.data.get('hashtags', '').strip()

        if not caption:
            return Response(
                {'error': 'Caption is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post = Post(
            user=request.user,
            caption=caption,
            hashtags=hashtags,
            location=location,
            points=5,
            verification_status='pending'
        )

        # Handle image
        if 'image' in request.FILES:
            post.image = request.FILES['image']
            post.image_url = ''   # <-- Set empty string to avoid NULL
        elif request.data.get('image_url'):
            post.image_url = request.data.get('image_url')
        else:
            post.image_url = 'https://picsum.photos/800/600'

        post.save()
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
# ============================================================
# LIKE POST (requires login)
# ============================================================
@api_view(['POST'])
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        # Unlike: remove the like and decrement count
        like.delete()
        post.likes -= 1
        post.save()
        return Response({'likes': post.likes, 'liked': False})
    else:
        # Like: increment count
        post.likes += 1
        post.save()
        return Response({'likes': post.likes, 'liked': True})

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


@api_view(['POST'])
@login_required
def create_challenge(request):
    data = request.data
    challenge = Challenge.objects.create(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category', 'community'),
        created_by=request.user,
        submitted_by=request.user,
        status='pending',         # pending approval
        is_active=False,
        start_date=data.get('start_date', timezone.now()),
        end_date=data.get('end_date', timezone.now() + timezone.timedelta(days=30)),
        points_reward=data.get('points_reward', 10),
        image=data.get('image', 'https://picsum.photos/800/400'),
    )
    return Response(ChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@login_required
def my_challenges(request):
    """
    Get all challenges the logged-in user has joined.
    """
    participants = ChallengeParticipant.objects.filter(user=request.user)
    return Response(ChallengeParticipantSerializer(participants, many=True).data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_detail(request, post_id):
    """
    Fetch a single post by ID. Used for polling verification status.
    """
    def get_serializer_context(self):
        return {'request': self.request}
    
    try:
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post)
        
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

# --- CHALLENGES ---
class ChallengeListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        return Challenge.objects.filter(status='approved', is_active=True, end_date__gte=timezone.now())

@api_view(['POST'])
@login_required
def join_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participant, created = ChallengeParticipant.objects.get_or_create(
        challenge=challenge,
        user=request.user,
        defaults={'status': 'registered'}
    )
    if created:
        challenge.participants_count += 1
        challenge.save()
        return Response({'message': 'Joined successfully!'}, status=status.HTTP_201_CREATED)
    return Response({'message': 'Already joined'}, status=status.HTTP_200_OK)

# --- REWARDS ---
class RewardListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RewardSerializer
    queryset = Reward.objects.filter(is_active=True, stock_quantity__gt=0)

@api_view(['POST'])
@login_required
def redeem_reward(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id, is_active=True)
    user = request.user

    if user.nature_points < reward.points_cost:
        return Response({'error': 'Not enough points'}, status=status.HTTP_400_BAD_REQUEST)
    if reward.stock_quantity <= 0:
        return Response({'error': 'Out of stock'}, status=status.HTTP_400_BAD_REQUEST)

    # Deduct points and reduce stock
    user.nature_points -= reward.points_cost
    user.save()
    reward.stock_quantity -= 1
    reward.save()

    redemption = RewardRedemption.objects.create(
        user=user,
        reward=reward,
        points_spent=reward.points_cost,
        status='pending'
    )

    return Response(RewardRedemptionSerializer(redemption).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'nature_points': user.nature_points,
        'profile_pic': user.profile_pic,
        'total_posts': user.total_posts,
        'bio': user.bio,
        'location': user.location,
    })

@api_view(['DELETE'])
@login_required
def delete_post(request, post_id):
    """
    Delete a post. Only the owner or admin can delete.
    """
    try:
        post = Post.objects.get(id=post_id)
        # Check permission: owner or staff
        if post.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to delete this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Post.DoesNotExist:
        return Response(
            {'error': 'Post not found.'},
            status=status.HTTP_404_NOT_FOUND
        )