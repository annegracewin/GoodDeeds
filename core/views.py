from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import Post
from .serializers import PostSerializer, UserSerializer

User = get_user_model()


# ===== FEED VIEW =====
class FeedView(generics.ListAPIView):
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


# ===== USER LIST VIEW (for stories) =====
class UserListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ===== CREATE POST =====
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_post(request):
    post = Post.objects.create(
        user=request.user,
        image_url=request.data.get('image_url', 'https://picsum.photos/800/600'),
        caption=request.data.get('caption', ''),
        hashtags=request.data.get('hashtags', ''),
        location=request.data.get('location', ''),
        points=5  # Base points
    )
    return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


# ===== LIKE POST =====
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.likes += 1
        post.save()
        return Response({'likes': post.likes, 'message': 'Liked!'})
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


# ===== VERIFY POST (AI Demo) =====
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)

        # Simple AI verification (keyword-based)
        keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                   'blood', 'tree', 'food', 'education', 'health', 'recycle']

        caption_lower = post.caption.lower()
        found = [kw for kw in keywords if kw in caption_lower]

        if len(found) >= 2:
            post.is_verified = True
            post.verification_score = 0.8
            post.points += 15  # Bonus points
        elif len(found) >= 1:
            post.is_verified = True
            post.verification_score = 0.6
            post.points += 10
        else:
            post.verification_score = 0.2

        post.save()

        return Response({
            'is_verified': post.is_verified,
            'verification_score': post.verification_score,
            'points': post.points,
            'keywords_found': found
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)