from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta, datetime
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.utils import timezone



from student.models import Department,Book,Student,Librarian,BookBorrow,BookReview,FavoriteBook,Complaint,BookNotificationRequest,BookNotificationLog,StudentPurchase
from student.serializers import (DepartmentSerializer,BookSerializer,StudentSerializer,LibrarianLoginSerializer,LibrarianRegisterSerializer,BookBorrowSerializer,
                                StudentSerializer,ComplaintSerializer,BookNotificationLogSerializer,BookNotificationRequestSerializer,StudentPurchaseSerializer,
                                StudentSerializerNew)

                                
              

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer



class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookRetrieveUpdateDestroyView(APIView):
    def put(self, request, pk):
        request.data['total_copies'] = request.data['total_books']
        request.data['available_copies'] = int(request.data['available_books'])
        book = get_object_or_404(Book, pk=pk)
        tot_avai_books = book.available_copies
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if tot_avai_books == 0 and int(request.data['available_books']) > 0:
                records = BookNotificationRequest.objects.filter(notified=False, book_id=pk)
                for re in records:
                    BookNotificationLog.objects.create(
                        student_id=re.student_id,
                        book_id=re.book_id,
                        message=f'{book.title} book is available'
                    )
                records.update(notified=True)
            return Response({"data": None}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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
                user.last_login_time = datetime.now()
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
            "department": stu.department,
            "profile_pic": stu.profile_picture.url
        }
        return Response({"data": data}, status=200)

    def put(self, request, student_id):
        try:
            stu = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        request.data['profile_picture'] = request.data['profile_pic']
        serializer = StudentSerializerNew(stu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student profile updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class get_student_details(APIView):
    def post(self, request, student_id):
        import ast
        try:
            student = Student.objects.get(student_id=student_id)  # Correct field
            data = {
                "student_id": student_id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "department": ast.literal_eval(student.department)['name'] if student.department else None,  # If department is FK
            }
            return Response(data, status=200)
        except Student.DoesNotExist:
            return Response({"data": "Not found"}, status=400)
        except Exception as e:
            return Response({"data": str(e)}, status=400)

        

@api_view(['POST'])
def borrow_book(request):
    student_id = request.data.get('student_id')
    book_id = request.data.get('book_id')
    borrow_date = request.data.get('borrow_date')
    due_date = request.data.get('due_date')

    try:
        student = Student.objects.get(student_id=student_id)
        book = Book.objects.get(id=book_id)

        if book.available_copies <= 0:
            return Response({'error': 'No copies available'}, status=400)
        
        if StudentPurchase.objects.filter(student=student, book=book, submitted=False).exists():
            return Response({'error': 'You have already borrowed this copy of book'}, status=400)
        
        if StudentPurchase.objects.filter(student=student, submitted=False).count() >= 3:
            return Response({'error': 'You have already taken 3 books. Please submit one to borrow'}, status=400)

        # Create the purchase
        submit_date = (timezone.now() + timedelta(days=3)).date()
        StudentPurchase.objects.create(
            student=student,
            book=book,
            purchase_date=borrow_date,
            submit_date=submit_date
        )

        # Decrease book stock
        book.available_copies -= 1
        book.save()

        return Response({'success': 'Book borrowed successfully'}, status=200)

    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

def get(self, request):
    student = request.user.student  # or however you authenticate student
    purchases = StudentPurchase.objects.filter(student=student)
    serializer = StudentPurchaseSerializer(purchases, many=True)
    return Response(serializer.data)


class BorrowBookView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        book_id = request.data.get('book_id')

        try:
            student = Student.objects.get(id=student_id)
            book = Book.objects.get(id=book_id)

            purchase = StudentPurchase.objects.create(student=student, book=book)
            serializer = StudentPurchaseSerializer(purchase)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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



class BookReviewAPIView(APIView):
    def post(self, request):
        student_id = request.data.get("student_id")
        book_id = request.data.get("book_id")
        review = request.data.get("review")

        student = Student.objects.get(student_id=student_id)
        book = Book.objects.get(id=book_id)

        BookReview.objects.update_or_create(
            student=student,
            book=book,
            defaults={'review': review}
        )
        return Response({"message": "Review submitted."})

    def get(self, request, book_id, student_id):
        try:
            review = BookReview.objects.get(book_id=book_id, student__student_id=student_id)
            return Response({"review": review.review})
        except BookReview.DoesNotExist:
            return Response({"review": ""})
        

class FavoriteBookAPIView(APIView):
    def post(self, request):
        student_id = request.data.get("student_id")
        book_id = request.data.get("book_id")

        student = Student.objects.get(student_id=student_id)
        book = Book.objects.get(id=book_id)

        FavoriteBook.objects.get_or_create(student=student, book=book)
        return Response({"message": "Book added to favorites."})

    def delete(self, request):
        student_id = request.data.get("student_id")
        book_id = request.data.get("book_id")

        FavoriteBook.objects.filter(student__student_id=student_id, book_id=book_id).delete()
        return Response({"message": "Book removed from favorites."})

    def get(self, request, student_id):
        favs = FavoriteBook.objects.filter(student__student_id=student_id).select_related('book')
        data = [{"id": f.book.id, "title": f.book.title} for f in favs]
        return Response(data)
    


@api_view(['GET'])
def get_book_reviews(request, book_id):
    reviews = BookReview.objects.filter(book_id=book_id)
    data = [
        {
            'student_name': f"{r.student.first_name} {r.student.last_name}",
            'review': r.review
        }
        for r in reviews if r.review
    ]
    return Response({'reviews': data})
    
@api_view(['POST'])
def submit_review(request):
    borrow_id = request.data.get('borrow_id')
    review = request.data.get('review')

    borrowed = get_object_or_404(BookBorrow, id=borrow_id)
    if not borrowed.returned:
        return Response({'error': 'Book must be returned before submitting review'}, status=400)

    borrowed.review = review
    borrowed.save()

    return Response({'success': 'Review submitted successfully'})


@api_view(['POST'])
def save_book_review(request):
    book_id = request.data.get('book_id')
    student_id = request.data.get('student_id')
    review = request.data.get('review')

    if not all([book_id, student_id, review]):
        return Response({'error': 'Missing fields'}, status=400)

    BookReview.objects.create(student_id=student_id, book_id=book_id, review=review)
    return Response({'success': 'Review saved'})


class ComplaintCreateAPIView(APIView):
    def post(self, request):
        try:
            data = request.data.copy()
            serializer = ComplaintSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Complaint sent successfully!"}, status=201)
            return Response({"errors": serializer.errors}, status=400)
        except Exception as err:
            return Response({"errors": serializer.errors}, status=400)


class LibrarianComplaintsAPIView(APIView):
    def get(self, request):
        complaints = Complaint.objects.filter(sent_to='librarian')
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)

class AdminComplaintsAPIView(APIView):
    def get(self, request):
        complaints = Complaint.objects.filter(sent_to='admin')
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)
    

# Student requests notification
class CreateBookNotificationRequestView(APIView):
    def post(self, request):
        BookNotificationRequest.objects.create(student_id=request.data['student'], book_id=request.data['book'])
        return Response({"data": None}, status=200)


# Student views notifications
class StudentNotificationListView(APIView):
    serializer_class = BookNotificationLogSerializer

    def get(self, request, id):
        nots = BookNotificationLog.objects.filter(student=id).order_by('-created_at')
        serializer = self.serializer_class(nots, many=True)
        return Response({"data": serializer.data}, status=200)


class StudentPurchaseListView(APIView):
    def get(self, request, id):
        pur = StudentPurchase.objects.filter(student=id, submitted=False)
        ser = StudentPurchaseSerializer(pur, many=True)
        return Response({"data": ser.data}, status=200)


class PurchaseBookView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, book_id):
        student = get_object_or_404(Student, user=request.user)
        book = get_object_or_404(Book, id=book_id)
        purchase = StudentPurchase.objects.create(student=student, book=book)
        return Response({"message": "Book purchased successfully."})


class BooksByDepartmentView(APIView):

    def get(self, request, dep_id):
        books = Book.objects.filter(department__name=dep_id)
        serializer = BookSerializer(books, many=True)
        return Response({'data': serializer.data, "message": "Books list"}, status=200)


# ✅ Clear fine
class PayFineView(APIView):
    def post(self, request, purchase_id):
        purchase = get_object_or_404(StudentPurchase, id=purchase_id)
        # Here we just simulate paying fine by setting submit_date = purchase_date (no fine)
        purchase.submit_date = purchase.purchase_date
        purchase.save()
        return Response({"message": "Fine cleared successfully"}, status=status.HTTP_200_OK)


# ✅ Return book
class ReturnBookView(APIView):

    def post(self, request, purchase_id):
        book_id = request.data.get("book_id")
        print(purchase_id, book_id, '11111111111111111111111')
        purchase = get_object_or_404(StudentPurchase, id=purchase_id)
        book = get_object_or_404(Book, id=book_id)
        # Mark as submitted & set date
        purchase.submitted = True
        purchase.submit_date = date.today()
        purchase.save()

        # Increase available copies
        book.available_copies += 1
        book.save()

        # Remove from purchases (optional: if you want to delete instead of keeping record)
        purchase.delete()

        return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)