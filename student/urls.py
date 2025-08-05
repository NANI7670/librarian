from django.urls import path
from rest_framework.routers import DefaultRouter
from student.views import (
    DepartmentListCreateView,
    BookRetrieveUpdateDestroyView,
    BookListCreateView,
    StudentRegisterView,BorrowBookView,
    StudentLoginView,borrow_book,return_book,get_all_books,get_student_details,submit_review,save_book_review,AdminComplaintsAPIView,ComplaintCreateAPIView,CreateBookNotificationRequestView,
  BookList,LibrarianRegisterView, LibrarianLoginView, LibrarianLogoutView,BookDetailView,StudentDetailAPIView,BookReviewAPIView,FavoriteBookAPIView,LibrarianComplaintsAPIView,
  StudentNotificationListView,StudentPurchaseListView,PurchaseBookView,get_book_reviews
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
    path('student/<str:student_id>/', get_student_details.as_view(), name='student-detail'),
    path('borrow/', borrow_book),
    path('return/', return_book),
    path('books/', get_all_books),  
     path('borrow/', BorrowBookView.as_view(), name='borrow-book'),
    path("api/review/", BookReviewAPIView.as_view()),
    path("api/review/<int:book_id>/<str:student_id>/", BookReviewAPIView.as_view()),
    path("api/favorite/", FavoriteBookAPIView.as_view()),
    path("api/favorite/<str:student_id>/", FavoriteBookAPIView.as_view()),
    path('submit_review/', submit_review),
    path('save_book_review/', save_book_review),
    path('get_book_reviews/<int:book_id>/', get_book_reviews),

    path('complaint/send/', ComplaintCreateAPIView.as_view()),
    path('complaint/librarian/', LibrarianComplaintsAPIView.as_view()),
    path('complaint/admin/', AdminComplaintsAPIView.as_view()),
    path('notify-request/', CreateBookNotificationRequestView.as_view(), name='notify-request'),
    path('notifications/', StudentNotificationListView.as_view(), name='notifications'),
    path('student-purchases/<int:id>/', StudentPurchaseListView.as_view(), name='student-purchase-list'),
    path('student/purchase/<int:book_id>/', PurchaseBookView.as_view(), name='purchase-book'),

]


