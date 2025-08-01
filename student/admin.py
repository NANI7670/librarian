from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, Book,Student,Librarian,Complaint, StudentPurchase

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author', 'department',
        'publisher_year', 'price', 'total_copies', 'available_copies'
    )
    list_filter = ('department',)
    search_fields = ('title', 'author')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'email', 'department')
    search_fields = ('student_id', 'first_name', 'last_name', 'email', 'department')
    list_filter = ('department',)


class LibrarianAdmin(UserAdmin):
    model = Librarian
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Librarian, LibrarianAdmin)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'sent_to', 'message_summary', 'created_at')
    list_filter = ('sent_to', 'created_at')
    search_fields = ('sender__email', 'message')

    def message_summary(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_summary.short_description = 'Message'

admin.site.register(StudentPurchase)
