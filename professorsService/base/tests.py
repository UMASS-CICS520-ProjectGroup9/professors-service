from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from base.models import Professor, Review
from unittest.mock import patch
from django.test import override_settings

@override_settings()
class ProfessorAPITestCase(TestCase):
    """
    Unit tests for the Professor API endpoints.
    Each test follows best practices: explicit precondition, test, and postcondition assertions.
    """

    def setUp(self):
        self.client = APIClient()
        self.student_headers = {'HTTP_AUTHORIZATION': 'bearer student'}
        self.staff_headers = {'HTTP_AUTHORIZATION': 'bearer staff'}
        self.admin_headers = {'HTTP_AUTHORIZATION': 'bearer admin'}
        # Patch authentication to simulate user roles
        self.patcher = patch('professorsService.authentication.ExternalJWTAuthentication.authenticate', side_effect=self.fake_auth)
        self.patcher.start()
        # Prepopulate with two professors
        self.prof1 = Professor.objects.create(
            name="Alice Smith", department="CS", email="alice@umass.edu", office="CS101", rating=4.5, creator_id=2
        )
        self.prof2 = Professor.objects.create(
            name="Bob Jones", department="BIO", email="bob@umass.edu", office="BIO201", rating=3.8, creator_id=2
        )
        self.prof1.refresh_from_db()
        self.prof2.refresh_from_db()

    def tearDown(self):
        self.patcher.stop()

    def fake_auth(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.split()[-1].lower() if auth_header else ''
        roles = {
            'student': {'id': 1, 'role': 'STUDENT', 'is_authenticated': True},
            'staff': {'id': 2, 'role': 'STAFF', 'is_authenticated': True},
            'admin': {'id': 3, 'role': 'ADMIN', 'is_authenticated': True},
        }
        user_info = roles.get(token, {'id': 0, 'role': 'STUDENT', 'is_authenticated': True})
        class DummyUser:
            def __init__(self, info):
                self.id = info['id']
                self.role = info['role']
                self.is_authenticated = info['is_authenticated']
        return (DummyUser(user_info), {})

    def test_list_professors(self):
        """
        Test listing all professors.
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        response = self.client.get('/api/professors/', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        self.assertEqual(len(response.data), 2, "Testing: Should return 2 professors.")
        names = [prof['name'] for prof in response.data]
        self.assertEqual(names, sorted(names), "Testing: Professors should be sorted.")
        # Postcondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Postcondition: No professors should be changed.")

    def test_get_professor(self):
        """
        Test retrieving a single professor by ID.
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        response = self.client.get(f'/api/professors/{self.prof1.id}/', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        self.assertEqual(response.data['name'], 'Alice Smith', "Testing: Name should be 'Alice Smith'.")
        # Postcondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Postcondition: No professors should be changed.")

    def test_create_professor(self):
        """
        Test creating a professor (STAFF only).
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        new_prof = {
            "name": "Carol Lee", "department": "MATH", "email": "carol@umass.edu", "office": "MATH101", "rating": 0.0
        }
        # Testing assertion
        response = self.client.post('/api/professors/create/', new_prof, format='json', **self.staff_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Testing: Should return 201 Created.")
        self.assertEqual(Professor.objects.count(), 3, "Testing: Should have 3 professors after creation.")
        # Postcondition assertion
        created = Professor.objects.get(name="Carol Lee")
        self.assertEqual(created.department, "MATH", "Postcondition: Department should be MATH.")

    def test_delete_professor(self):
        """
        Test deleting a professor (STAFF only).
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        url = f'/api/professors/{self.prof1.id}/delete/'
        response = self.client.delete(url, **self.staff_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Testing: Should return 204 No Content.")
        self.assertEqual(Professor.objects.count(), 1, "Testing: Should have 1 professor after deletion.")
        # Postcondition assertion
        with self.assertRaises(Professor.DoesNotExist):
            Professor.objects.get(id=self.prof1.id)

    def test_create_review(self):
        """
        Test creating a review for a professor (STUDENT only).
        """
        # Precondition assertion
        self.assertEqual(Review.objects.count(), 0, "Precondition: No reviews exist.")
        new_review = {
            "author": "Student1",
            "rating": 5,
            "comment": "Great teacher!"
        }
        # Testing assertion
        response = self.client.post(f'/api/professors/{self.prof1.id}/review/', new_review, format='json', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Testing: Should return 201 Created.")
        self.assertEqual(Review.objects.count(), 1, "Testing: Should have 1 review after creation.")
        # Postcondition assertion
        created = Review.objects.get(professor=self.prof1)
        self.assertEqual(created.rating, 5, "Postcondition: Rating should be 5.")
        self.assertEqual(created.comment, "Great teacher!", "Postcondition: Comment should match.")

    def test_update_review(self):
        """
        Test updating a review for a professor (STUDENT only).
        """
        # Precondition assertion
        review = Review.objects.create(professor=self.prof1, author="Student1", rating=4, comment="Good", creator_id=1)
        self.assertEqual(review.rating, 4, "Precondition: Initial rating is 4.")
        review_data = {"author": "Student1", "rating": 5, "comment": "Excellent!"}
        # Testing assertion
        response = self.client.post(f'/api/professors/{self.prof1.id}/review/', review_data, format='json', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        review.refresh_from_db()
        self.assertEqual(review.rating, 5, "Testing: Rating should be updated to 5.")
        self.assertEqual(review.comment, "Excellent!", "Testing: Comment should be updated.")
        # Postcondition assertion
        self.assertEqual(Review.objects.count(), 1, "Postcondition: No new reviews should be created.")



    def test_filter_by_department(self):
        """
        Test filtering by department using query param.
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        response = self.client.get('/api/professors/?query=CS', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        self.assertTrue(any(prof['department'] == 'CS' for prof in response.data), "Testing: At least one professor should be CS.")
        # Postcondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Postcondition: No professors should be changed.")

    def test_filter_by_name_partial(self):
        """
        Test filtering by partial name using query param.
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        response = self.client.get('/api/professors/?query=Ali', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        self.assertTrue(any('Ali' in prof['name'] for prof in response.data), "Testing: At least one professor name should contain 'Ali'.")
        # Postcondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Postcondition: No professors should be changed.")

    def test_no_results(self):
        """
        Test filtering with no results using query param.
        """
        # Precondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Precondition: 2 professors exist.")
        # Testing assertion
        response = self.client.get('/api/professors/?query=PHYSICS', **self.student_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Testing: Should return 200 OK.")
        self.assertEqual(len(response.data), 0, "Testing: Should return 0 professors.")
        # Postcondition assertion
        self.assertEqual(Professor.objects.count(), 2, "Postcondition: No professors should be changed.")


