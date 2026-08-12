from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from core.models import Challenge, Reward, Sponsor, Post
from users.models import User
from core.forms import ChallengeForm, RewardForm, SponsorForm  # we'll create forms

@staff_member_required
def dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'total_challenges': Challenge.objects.count(),
        'pending_challenges': Challenge.objects.filter(status='pending').count(),
        'total_rewards': Reward.objects.count(),
        'total_sponsors': Sponsor.objects.filter(is_active=True).count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)

# ---- Challenges ----
@staff_member_required
def challenge_list(request):
    # Get filter from query
    filter_status = request.GET.get('status', 'all')
    challenges = Challenge.objects.all().order_by('-created_at')
    if filter_status != 'all':
        challenges = challenges.filter(status=filter_status)
    context = {
        'challenges': challenges,
        'filter_status': filter_status,
    }
    return render(request, 'admin_panel/challenges.html', context)

@staff_member_required
def approve_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if challenge.status == 'pending':
        challenge.status = 'approved'
        challenge.is_active = True
        challenge.reviewed_by = request.user
        challenge.reviewed_at = timezone.now()
        challenge.save()
        messages.success(request, f'Challenge "{challenge.title}" approved.')
    else:
        messages.warning(request, 'This challenge is not pending.')
    return redirect('admin_panel:challenges')

@staff_member_required
def reject_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if challenge.status == 'pending':
        challenge.status = 'rejected'
        challenge.is_active = False
        challenge.reviewed_by = request.user
        challenge.reviewed_at = timezone.now()
        challenge.save()
        messages.success(request, f'Challenge "{challenge.title}" rejected.')
    else:
        messages.warning(request, 'This challenge is not pending.')
    return redirect('admin_panel:challenges')

@staff_member_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.created_by = request.user
            challenge.submitted_by = request.user
            challenge.status = 'approved'   # Admin creates as approved
            challenge.is_active = True
            challenge.save()
            messages.success(request, 'Challenge created successfully.')
            return redirect('admin_panel:challenges')
    else:
        form = ChallengeForm()
    return render(request, 'admin_panel/challenge_form.html', {'form': form, 'action': 'Create'})

@staff_member_required
def edit_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Challenge updated.')
            return redirect('admin_panel:challenges')
    else:
        form = ChallengeForm(instance=challenge)
    return render(request, 'admin_panel/challenge_form.html', {'form': form, 'action': 'Edit'})

@staff_member_required
def delete_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        challenge.delete()
        messages.success(request, 'Challenge deleted.')
        return redirect('admin_panel:challenges')
    return render(request, 'admin_panel/confirm_delete.html', {'object': challenge, 'type': 'Challenge'})

# ---- Rewards ----
@staff_member_required
def reward_list(request):
    rewards = Reward.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/rewards.html', {'rewards': rewards})

@staff_member_required
def create_reward(request):
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reward created.')
            return redirect('admin_panel:rewards')
    else:
        form = RewardForm()
    return render(request, 'admin_panel/reward_form.html', {'form': form, 'action': 'Create'})

@staff_member_required
def edit_reward(request, pk):
    reward = get_object_or_404(Reward, pk=pk)
    if request.method == 'POST':
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reward updated.')
            return redirect('admin_panel:rewards')
    else:
        form = RewardForm(instance=reward)
    return render(request, 'admin_panel/reward_form.html', {'form': form, 'action': 'Edit'})

@staff_member_required
def delete_reward(request, pk):
    reward = get_object_or_404(Reward, pk=pk)
    if request.method == 'POST':
        reward.delete()
        messages.success(request, 'Reward deleted.')
        return redirect('admin_panel:rewards')
    return render(request, 'admin_panel/confirm_delete.html', {'object': reward, 'type': 'Reward'})

# ---- Users ----
@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})

@staff_member_required
def toggle_user_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} {status}.')
    return redirect('admin_panel:users')

# ---- Sponsors ----
@staff_member_required
def sponsor_list(request):
    sponsors = Sponsor.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/sponsors.html', {'sponsors': sponsors})

@staff_member_required
def create_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsor added.')
            return redirect('admin_panel:sponsors')
    else:
        form = SponsorForm()
    return render(request, 'admin_panel/sponsor_form.html', {'form': form, 'action': 'Create'})

@staff_member_required
def edit_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method == 'POST':
        form = SponsorForm(request.POST, instance=sponsor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsor updated.')
            return redirect('admin_panel:sponsors')
    else:
        form = SponsorForm(instance=sponsor)
    return render(request, 'admin_panel/sponsor_form.html', {'form': form, 'action': 'Edit'})

@staff_member_required
def delete_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method == 'POST':
        sponsor.delete()
        messages.success(request, 'Sponsor deleted.')
        return redirect('admin_panel:sponsors')
    return render(request, 'admin_panel/confirm_delete.html', {'object': sponsor, 'type': 'Sponsor'})