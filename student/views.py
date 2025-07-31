from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate




from student.models import Department,Book,Student,Librarian,BookBorrow
from student.serializers import DepartmentSerializer,BookSerializer,StudentSerializer,LibrarianLoginSerializer,LibrarianRegisterSerializer,BookBorrowSerializer,StudentSerializer

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer



class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer



class StudentRegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        last_student = Student.objects.last()
        student_id = f"CM{(last_student.id + 1) if last_student else 1:03d}"
        data['student_id'] = student_id

        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StudentLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            student = Student.objects.get(email=email, password=password)
            return Response({
                "id": student.pk,
                "student_id": student.student_id,
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "department": student.department
            })
        except Student.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        

class BookList(APIView):
    def get(self, request):
        department_name = request.GET.get('department')
        if department_name:
            books = Book.objects.filter(department__name=department_name)
        else:
            books = Book.objects.none()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    

class LibrarianRegisterView(APIView):
    def post(self, request):
        serializer = LibrarianRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class LibrarianLoginView(APIView):
    def post(self, request):
        serializer = LibrarianLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                user.last_login_time = now()
                user.save()
                request.session['librarian_id'] = user.id
                return Response({'message': 'Login successful'})
            return Response({'error': 'Invalid credentials'}, status=401)
        return Response(serializer.errors, status=400)

class LibrarianLogoutView(APIView):
    def post(self, request):
        librarian_id = request.session.get('librarian_id')
        if librarian_id:
            try:
                librarian = Librarian.objects.get(id=librarian_id)
                librarian.last_logout_time = now()
                librarian.save()
            except Librarian.DoesNotExist:
                pass
        request.session.flush()
        return Response({'message': 'Logout successful'})
    


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class StudentDetailAPIView(APIView):
    def get(self, request, student_id):
        try:
            stu = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "student_id": stu.student_id,
            "first_name": stu.first_name,
            "last_name": stu.last_name,
            "email": stu.email,
            "department": stu.department
        }
        return Response({"data": data}, status=200)

    def put(self, request, student_id):
        try:
            stu = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(stu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student profile updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


def get_student_details(student_id):
    try:
        student = Student.objects.get(student_id=student_id)  # Correct field
        data = {
            "student_id": student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "department": student.department.name if student.department else None,  # If department is FK
        }
        return data, None
    except Student.DoesNotExist:
        return None, "Student not found"
    except Exception as e:
        return None, str(e)

        

@api_view(['POST'])
def borrow_book(request):
    student_id = request.data.get('student_id')
    book_id = request.data.get('book_id')

    try:
        student = Student.objects.get(student_id=student_id)
        book = Book.objects.get(id=book_id)

        # 3 book limit
        active_borrows = BookBorrow.objects.filter(student=student, returned=False)
        if active_borrows.count() >= 3:
            return Response({'error': 'Limit of 3 books reached'}, status=400)

        # Prevent duplicate title from same department
        if BookBorrow.objects.filter(student=student, book__title=book.title,
                                     book__department=book.department, returned=False).exists():
            return Response({'error': 'Same book from same department already taken'}, status=400)

        if book.available_copies <= 0:
            return Response({'error': 'Stock over'}, status=400)

        borrow = BookBorrow.objects.create(student=student, book=book)
        book.available_copies -= 1
        book.save()

        return Response({'message': 'Book borrowed successfully'})

    except (Student.DoesNotExist, Book.DoesNotExist):
        return Response({'error': 'Invalid student or book ID'}, status=404)

@api_view(['POST'])
def return_book(request):
    borrow_id = request.data.get('borrow_id')

    try:
        borrow = BookBorrow.objects.get(id=borrow_id)
        if borrow.returned:
            return Response({'error': 'Book already returned'}, status=400)

        borrow.returned = True
        borrow.save()

        borrow.book.available_copies += 1
        borrow.book.save()

        return Response({'message': 'Book returned successfully'})
    except BookBorrow.DoesNotExist:
        return Response({'error': 'Invalid borrow ID'}, status=404)
    

@api_view(['GET'])
def get_all_books(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)