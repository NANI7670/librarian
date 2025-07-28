from django.urls import path
from rest_framework.routers import DefaultRouter
from student.views import (
    DepartmentListCreateView,
    BookRetrieveUpdateDestroyView,
    BookListCreateView,
    StudentRegisterView,
    StudentLoginView,
  BookList,LibrarianRegisterView, LibrarianLoginView, LibrarianLogoutView
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
]


