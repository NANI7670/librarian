from rest_framework import serializers
from student.models import Department,Book,Student,Librarian,BookBorrow

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
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'name', 'email', 'department', 'department_name', 'profile_picture']



class BookBorrowSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    fine = serializers.SerializerMethodField()

    class Meta:
        model = BookBorrow
        fields = '__all__'

    def get_fine(self, obj):
        return obj.fine_amount()