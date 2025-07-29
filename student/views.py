from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate




from student.models import Department,Book,Student,Librarian,BookBorrow
from student.serializers import DepartmentSerializer,BookSerializer,StudentSerializer,LibrarianLoginSerializer,LibrarianRegisterSerializer,StudentSerializer,BookBorrowSerializer

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
        stu = Student.objects.get(id=student_id)

        data = {
            "student_id": stu.student_id,
            "first_name": stu.first_name,
            "last_name": stu.last_name,
            "email": stu.email,
            "department": stu.department
        }
        return Response({"data": data}, status=200)




@api_view(['GET'])
def get_student_summary(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        borrows = BookBorrow.objects.filter(student=student)

        borrow_data = BookBorrowSerializer(borrows, many=True).data
        total_fine = sum([b.fine_amount() for b in borrows if not b.returned])

        return Response({
            'student': StudentSerializer(student).data,
            'borrowed_books': borrow_data,
            'total_fine': total_fine
        })
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

@api_view(['POST'])
def borrow_book(request):
    student_id = request.data.get('student_id')
    book_id = request.data.get('book_id')

    try:
        student = Student.objects.get(student_id=student_id)
        book = Book.objects.get(id=book_id)

        existing = BookBorrow.objects.filter(student=student, returned=False)

        if existing.count() >= 3:
            return Response({'error': 'Max 3 books allowed'}, status=400)

        if existing.filter(book__title=book.title, book__department=book.department).exists():
            return Response({'error': 'Cannot borrow duplicate book from same department'}, status=400)

        if book.available_copies <= 0:
            return Response({'error': 'Stock Over'}, status=400)

        borrow = BookBorrow.objects.create(
            student=student,
            book=book,
            borrow_date=date.today(),
            return_date=date.today() + timedelta(days=14)
        )

        book.available_copies -= 1
        book.save()

        return Response(BookBorrowSerializer(borrow).data)

    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=404)

@api_view(['POST'])
def return_book(request):
    borrow_id = request.data.get('borrow_id')
    try:
        borrow = BookBorrow.objects.get(id=borrow_id)
        if borrow.returned:
            return Response({'error': 'Already returned'}, status=400)

        borrow.returned = True
        borrow.book.available_copies += 1
        borrow.book.save()
        borrow.save()
        return Response({'message': 'Book returned successfully'})
    except:
        return Response({'error': 'Return failed'}, status=400)