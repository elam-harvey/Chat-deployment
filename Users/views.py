from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, Message
from django.contrib.auth import get_user_model, login
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .forms import ChatGroupForm, UserRegistrationForm as RegisterForm
from .forms import LoginForm
from django.db.models import Q

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES) # FILES is important for handling file uploads like profile pictures
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to the database yet
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()  # Now save the user to the database
            login(request, user)  # Log the user in after registration
            return redirect('chat_list')
    else:
        form = RegisterForm()
    return render(request, 'Users/register.html', {'form': form})
    

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_list')
    else:
        form = LoginForm()
    return render(request, 'Users/login.html', {'form': form})

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

@login_required
def join_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    user = request.user

    # Check if user is already a member
    if user not in group.members.all():
        group.members.add(user)
        # Notify group members that a new user joined
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{group_id}',
            {
                'type': 'user_joined',
                'username': user.username
            }
        )
    
    return redirect('chat_room', group_id=group.id)

@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if the person making the request is the admin
    if request.user == group.admin:
        user_to_remove = get_object_or_404(User, id=user_id)
    
        # Admin should not remove themselves by mistake
        if user_to_remove != group.admin:
            group.members.remove(user_to_remove)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{group_id}',
                {
                    'type': 'user_removed',
                    'user_id': user_to_remove.id,
                    'username': user_to_remove.username,
                }
            )
    return redirect('chat_room', group_id=group.id)

@login_required
def exit_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)

    if request.user in group.members.all():
        group.members.remove(request.user)

        if request.user == group.admin:
            if group.members.exists():
                group.admin = group.members.first()
                group.save()
            else:
                group.delete()
                return redirect('chat_list')

    return redirect('chat_list')

# a view to render the chat room template
#@login_required
def chat_room(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    is_member = request.user in group.members.all()

    return render(request, 'Users/chat_room.html', {'group': group, 'is_member': is_member})
     
def chat_list(request):
    groups = ChatGroup.objects.filter(members=request.user).order_by('-created_at')
    
    # Get one-to-one conversations
    conversations = []
    other_users = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()
    
    for other in other_users:
        latest_msg = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other)) | (Q(sender=other) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        if latest_msg:
            unread_count = Message.objects.filter(sender=other, receiver=request.user, is_read=False).count()
            conversations.append({
                'other_user': other,
                'latest_message': latest_msg,
                'unread_count': unread_count
            })
    
    # Sort conversations by latest message timestamp
    conversations.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)
    
    return render(request, 'Users/chat_list.html', {'groups': groups, 'conversations': conversations})

# a function to create a new chat group
@login_required
def create_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)  # Add only the creator
            return redirect('group_info', group_id=group.id)
    else:
        form = ChatGroupForm()
    return render(request, 'Users/create_group.html', {'form': form})

@login_required
def group_info(request, group_id):
    """Group information page where users can view and share invite link"""
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Only admin can view this page
    if request.user != group.admin:
        return redirect('chat_room', group_id=group.id)
    
    # Get full URL for the invite link
    from django.http import request as http_request
    invite_link = request.build_absolute_uri(group.get_invite_link())
    
    return render(request, 'Users/group_info.html', {
        'group': group,
        'invite_link': invite_link,
        'group_uuid': str(group.id)
    })

@login_required
def direct_message(request, user_id):
    """View for one-to-one direct messages"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Prevent user from messaging themselves
    if other_user == request.user:
        return redirect('chat_list')
    
    # Get all messages between these two users
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) | (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'Users/direct_message.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def send_message(request, user_id):
    """View to send a direct message"""
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('message', '').strip()
        
        if message_content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=message_content
            )
    
    return redirect('direct_message', user_id=user_id)

@login_required
def start_conversation(request):
    if request.method == 'POST':
        # Determine which action the user is taking
        action = request.POST.get('action', 'direct_message')
        
        if action == 'join_group':
            # Handle group joining
            group_id = request.POST.get('group_id', '').strip()
            
            if not group_id:
                error_message = "Please enter a group UUID or paste the link."
                return render(request, 'Users/start_conversation.html', {'error_message': error_message})
            
            # Try to parse the group_id - it could be a full URL or just a UUID
            import re
            uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', group_id)
            
            if uuid_match:
                extracted_uuid = uuid_match.group(1)
                try:
                    group = ChatGroup.objects.get(id=extracted_uuid)
                    return redirect('join_group', group_id=extracted_uuid)
                except ChatGroup.DoesNotExist:
                    error_message = "Group not found. Check the UUID and try again."
                    return render(request, 'Users/start_conversation.html', {'error_message': error_message})
            else:
                error_message = "Invalid group UUID or link format."
                return render(request, 'Users/start_conversation.html', {'error_message': error_message})
        
        else:  # action == 'direct_message'
            # Handle direct messaging
            username = request.POST.get('username', '').strip()
            
            if not username:
                error_message = "Please enter a username."
                return render(request, 'Users/start_conversation.html', {'error_message': error_message})
            
            try:
                other_user = User.objects.get(username=username)
                if other_user == request.user:
                    error_message = "You cannot start a conversation with yourself."
                    return render(request, 'Users/start_conversation.html', {'error_message': error_message})
                return redirect('direct_message', user_id=other_user.id)
            except User.DoesNotExist:
                error_message = "User not found."
                return render(request, 'Users/start_conversation.html', {'error_message': error_message})
    else:
        return render(request, 'Users/start_conversation.html')