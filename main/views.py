from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import SignUpForm, LoginForm, ContactForm, TaskForm
from .models import Task, ActivityLog
from .chromadb_service import ChromaDBService


def home(request):
    # If user is logged in, show their tasks
    context = {}
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user)
        upcoming_tasks = tasks.filter(completed=False, due_date__gte=timezone.now().date()).order_by('due_date', 'due_time')[:3]
        context = {
            'tasks': tasks,
            'upcoming_tasks': upcoming_tasks,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(completed=True).count(),
        }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


@csrf_protect
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'main/contact.html', {'form': form})


@login_required
def dashboard(request):
    # Get ChromaDB stats for dashboard
    chroma_stats = {}
    try:
        collection = ChromaDBService.get_collection()
        count_result = collection.count()
        chroma_stats = {
            'total_documents': count_result,
            'status': 'connected'
        }
    except Exception as e:
        chroma_stats = {
            'status': 'error',
            'error': str(e)
        }
    
    # Get user's tasks
    tasks = Task.objects.filter(user=request.user)
    upcoming_tasks = tasks.filter(completed=False, due_date__gte=timezone.now().date()).order_by('due_date', 'due_time')[:5]
    overdue_tasks = tasks.filter(completed=False, due_date__lt=timezone.now().date())
    due_soon_tasks = []
    
    now = timezone.now()
    for task in tasks.filter(completed=False):
        if task.is_due_soon:
            due_soon_tasks.append(task)
    
    # Get recent activities
    recent_activities = ActivityLog.objects.filter(user=request.user)[:10]
    
    # Calculate statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = tasks.filter(completed=False).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tasks by priority
    high_priority = tasks.filter(priority='high', completed=False).count()
    medium_priority = tasks.filter(priority='medium', completed=False).count()
    low_priority = tasks.filter(priority='low', completed=False).count()
    
    # Tasks by category
    tasks_by_category = {}
    for category_code, category_name in Task.CATEGORY_CHOICES:
        tasks_by_category[category_name] = tasks.filter(category=category_code, completed=False).count()
    
    context = {
        'user': request.user,
        'chroma_stats': chroma_stats,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'due_soon_tasks': due_soon_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': round(completion_rate, 1),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'tasks_by_category': tasks_by_category,
        'recent_activities': recent_activities,
    }
    return render(request, 'main/dashboard.html', context)


@login_required
def search_messages(request):
    """Search contact messages using ChromaDB"""
    results = None
    query = request.GET.get('q', '')
    processed_results = []
    
    if query:
        try:
            results = ChromaDBService.query(
                query_texts=[query],
                n_results=10,
                include=['documents', 'metadatas', 'distances']
            )
            # Process results for easier template rendering
            if results and results.get('ids') and len(results['ids']) > 0:
                ids = results['ids'][0]
                documents = results.get('documents', [[]])[0] if results.get('documents') else []
                metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
                distances = results.get('distances', [[]])[0] if results.get('distances') else []
                
                for idx, doc_id in enumerate(ids):
                    processed_results.append({
                        'id': doc_id,
                        'document': documents[idx] if idx < len(documents) else '',
                        'metadata': metadatas[idx] if idx < len(metadatas) else {},
                        'distance': distances[idx] if idx < len(distances) else None
                    })
        except Exception as e:
            messages.error(request, f'Search error: {str(e)}')
    
    return render(request, 'main/search.html', {
        'query': query,
        'results': results,
        'processed_results': processed_results
    })


@csrf_protect
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


@login_required
def logout_view(request):
    """Custom logout view with success message"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


# Task Management Views
@login_required
def task_list(request):
    """Display all tasks for the logged-in user"""
    tasks = Task.objects.filter(user=request.user).order_by('due_date', 'due_time')
    
    # Filter by status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_type == 'pending':
        tasks = tasks.filter(completed=False)
    elif filter_type == 'overdue':
        tasks = tasks.filter(completed=False, due_date__lt=timezone.now().date())
    
    context = {
        'tasks': tasks,
        'filter_type': filter_type,
    }
    return render(request, 'main/task_list.html', context)


@login_required
@csrf_protect
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='Task Created',
                description=f'Created task: {task.title}'
            )
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'main/task_form.html', {'form': form, 'action': 'Create'})


@login_required
@csrf_protect
def task_edit(request, pk):
    """Edit an existing task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='Task Updated',
                description=f'Updated task: {task.title}'
            )
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'main/task_form.html', {'form': form, 'task': task, 'action': 'Edit'})


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task_title = task.title
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action='Task Deleted',
            description=f'Deleted task: {task_title}'
        )
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('task_list')
    return render(request, 'main/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    """Toggle task completion status"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    if task.completed:
        task.completed_at = timezone.now()
    else:
        task.completed_at = None
    task.save()
    
    # Log activity
    action = 'Task Completed' if task.completed else 'Task Reopened'
    ActivityLog.objects.create(
        user=request.user,
        action=action,
        description=f'{action}: {task.title}'
    )
    
    status = 'completed' if task.completed else 'marked as incomplete'
    messages.success(request, f'Task "{task.title}" {status}!')
    return redirect('task_list')


@login_required
def check_task_notifications(request):
    """Check for tasks that are due soon and show notifications (AJAX endpoint)"""
    from django.http import JsonResponse
    
    tasks = Task.objects.filter(
        user=request.user,
        completed=False,
        notification_sent=False
    )
    
    due_soon_tasks = []
    now = timezone.now()
    
    for task in tasks:
        if task.is_due_soon:
            due_soon_tasks.append({
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date.strftime('%b %d, %Y'),
                'due_time': task.due_time.strftime('%I:%M %p')
            })
            # Mark notification as sent
            task.notification_sent = True
            task.save()
    
    return JsonResponse({
        'due_soon_tasks': due_soon_tasks,
        'has_notifications': len(due_soon_tasks) > 0
    })
