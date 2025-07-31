from django.db import models
from datetime import date
from datetime import date, timedelta
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin,User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    publisher_year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} by {self.author}"
    

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)  # like CO001, CO002
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
    

class LibrarianManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Librarian must have an email')
        email = self.normalize_email(email)
        librarian = self.model(email=email, **extra_fields)
        librarian.set_password(password)
        librarian.save()
        return librarian

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Librarian(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = LibrarianManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    


def get_return_date():
    return date.today() + timedelta(days=14)

class BookBorrow(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    borrow_date = models.DateField(default=date.today)
    return_date = models.DateField(default=get_return_date)
    returned = models.BooleanField(default=False)

    def fine_amount(self):
        if not self.returned and date.today() > self.return_date:
            return (date.today() - self.return_date).days * 10
        return 0


class BookReview(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FavoriteBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


class Complaint(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Correct
    message = models.TextField()
    sent_to = models.CharField(max_length=20, choices=(("librarian", "Librarian"), ("admin", "Admin")))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.sent_to} - {self.message[:20]}"
    

class BookNotificationRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.book} - {'Notified' if self.notified else 'Waiting'}"


class BookNotificationLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.student_id} - {self.book.title} - {self.message}"
    

class StudentPurchase(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='purchases')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    submitted = models.BooleanField(default=False)
    submit_date = models.DateField(null=True, blank=True)

    def calculate_fine(self):
        if self.submitted and self.submit_date:
            days_taken = (self.submit_date - self.purchase_date).days
        else:
            days_taken = (date.today() - self.purchase_date).days

        fine_per_day = 10  # ₹10 per day after 3 days
        if days_taken > 3:
            return (days_taken - 3) * fine_per_day
        return 0

    @property
    def fine(self):
        return self.calculate_fine()

    def __str__(self):
        return f"{self.student.user.username} - {self.book.name}"

