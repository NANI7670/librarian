from rest_framework import serializers
from student.models import Department,Book,Student,Librarian,BookBorrow,Complaint,BookNotificationRequest,BookNotificationLog,StudentPurchase

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name')
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'email', 'department', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class LibrarianRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        librarian = Librarian(**validated_data)
        librarian.set_password(password)  # ✅ hashes the password
        librarian.save()
        return librarian



class LibrarianLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'email', 'department', 'profile_picture']




class BookBorrowSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    fine = serializers.SerializerMethodField()

    class Meta:
        model = BookBorrow
        fields = '__all__'

    def get_fine(self, obj):
        return obj.fine_amount()
    

class ComplaintSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'



class BookNotificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookNotificationRequest
        fields = ['id', 'book', 'student', 'notified']
        read_only_fields = ['student', 'notified']

class BookNotificationLogSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = BookNotificationLog
        fields = ['id', 'book_name', 'message', 'created_at']


class StudentPurchaseSerializer(serializers.ModelSerializer):
    fine = serializers.ReadOnlyField()

    # ✅ Additional fields (read-only) for display
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_department = serializers.CharField(source='book.department.name', read_only=True)

    class Meta:
        model = StudentPurchase
        fields = [
            'id',
            'student',
            'book',
            'purchase_date',
            'submitted',
            'submit_date',
            'fine',
            'book_title',         # ✅ newly added
            'book_author',        # ✅ newly added
            'book_department'     # ✅ newly added
        ]
