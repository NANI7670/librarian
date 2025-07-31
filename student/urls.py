from django.urls import path
from rest_framework.routers import DefaultRouter
from student.views import (
    DepartmentListCreateView,
    BookRetrieveUpdateDestroyView,
    BookListCreateView,
    StudentRegisterView,
    StudentLoginView,borrow_book,return_book,get_all_books,get_student_details,
  BookList,LibrarianRegisterView, LibrarianLoginView, LibrarianLogoutView,BookDetailView,StudentDetailAPIView
)


# You can use router instead of manual as_view mapping



urlpatterns = [
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-detail'),
    path('register/', StudentRegisterView.as_view(), name='student-register'),
    path('student-login/', StudentLoginView.as_view(), name='student-login'),
    path('bookslist/', BookList.as_view(), name='book-list'),
    path('librarianregister/', LibrarianRegisterView.as_view(), name='librarian-register'),
    path('labrarianlogin/', LibrarianLoginView.as_view(), name='librarian-login'),
    path('laibrarianlogout/', LibrarianLogoutView.as_view(), name='librarian-logout'),
    path('api/books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('register/<str:student_id>/', StudentDetailAPIView.as_view(), name='student-profile'),
    path('student/<str:student_id>/', get_student_details, name='student-detail'),
    path('borrow/', borrow_book),
    path('return/', return_book),
    path('books/', get_all_books),  

]


