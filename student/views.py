from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate




from student.models import Department,Book,Student,Librarian
from student.serializers import DepartmentSerializer,BookSerializer,StudentSerializer,LibrarianLoginSerializer,LibrarianRegisterSerializer

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
        student_id = f"CO{(last_student.id + 1) if last_student else 1:03d}"
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