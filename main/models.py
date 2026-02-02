from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .chromadb_service import ChromaDBService
import uuid


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    chroma_id = models.CharField(max_length=100, blank=True, null=True, editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    
    def save_to_chromadb(self):
        """Save this contact message to ChromaDB"""
        try:
            if not self.chroma_id:
                self.chroma_id = str(uuid.uuid4())
            
            # Combine all message data for vector storage
            full_text = f"Name: {self.name}\nEmail: {self.email}\nMessage: {self.message}"
            
            ChromaDBService.add_documents(
                documents=[full_text],
                ids=[self.chroma_id],
                metadatas=[{
                    "name": self.name,
                    "email": self.email,
                    "created_at": self.created_at.isoformat(),
                    "model_id": str(self.id),
                    "type": "contact_message"
                }]
            )
            # Save chroma_id to model
            if not self.pk:
                self.save()
            else:
                ContactMessage.objects.filter(pk=self.pk).update(chroma_id=self.chroma_id)
        except Exception as e:
            print(f"Error saving to ChromaDB: {e}")


@receiver(post_save, sender=ContactMessage)
def save_contact_to_chromadb(sender, instance, created, **kwargs):
    """Signal to automatically save contact messages to ChromaDB"""
    if created:
        instance.save_to_chromadb()


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('shopping', 'Shopping'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    due_time = models.TimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['due_date', 'due_time']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @property
    def due_datetime(self):
        """Combine due_date and due_time into a datetime"""
        from django.utils import timezone
        return timezone.make_aware(
            timezone.datetime.combine(self.due_date, self.due_time)
        )

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        from django.utils import timezone
        if self.completed:
            return False
        return self.due_datetime < timezone.now()

    @property
    def is_due_soon(self):
        """Check if task is due within the next hour"""
        from django.utils import timezone
        from datetime import timedelta
        if self.completed:
            return False
        now = timezone.now()
        due = self.due_datetime
        return now <= due <= now + timedelta(hours=1)
    
    def get_priority_color(self):
        """Get color for priority badge"""
        colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info'
        }
        return colors.get(self.priority, 'secondary')
    
    def get_category_icon(self):
        """Get icon for category"""
        icons = {
            'work': 'briefcase',
            'personal': 'person',
            'shopping': 'cart',
            'health': 'heart',
            'education': 'book',
            'other': 'folder'
        }
        return icons.get(self.category, 'folder')


class ActivityLog(models.Model):
    """Track user activities"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.action}"
