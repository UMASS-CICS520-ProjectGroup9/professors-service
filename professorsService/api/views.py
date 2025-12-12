from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.db.models import Q, Avg
from base.models import Professor, Review
from .serializers import ProfessorSerializer, ReviewSerializer
from .permissions import IsStudent, IsStaff, IsAdmin
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsStudent])
def getProfessors(request):
    """
    Retrieve a list of professors, optionally filtered by query.

    **GET**: Returns a list of professors.

    Query Parameters:
        - query: Filter by professor name or department (case-insensitive, partial match)
    """
    query = request.GET.get('query', '')
    professors = Professor.objects.all()
    if query:
        professors = professors.filter(
            Q(name__icontains=query) | 
            Q(department__icontains=query)
        )
    serializer = ProfessorSerializer(professors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsStudent])
def getProfessor(request, pk):
    """
    Retrieve a single professor by primary key (pk).

    **GET**: Returns professor details or 404 if not found.

    Path Parameters:
        - pk: Professor primary key (integer)
    """
    try:
        professor = Professor.objects.get(pk=pk)
        serializer = ProfessorSerializer(professor)
        return Response(serializer.data)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsStaff])
def createProfessor(request):
    """
    Create a new professor.

    **POST**: Creates a new professor record.

    Request Body:
        - name: string
        - department: string
        - ... (other fields as required by ProfessorSerializer)

    Returns the created professor data on success.
    """
    serializer = ProfessorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creator_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsStaff])
def deleteProfessor(request, pk):
    """
    Delete a professor by primary key (pk).

    **DELETE**: Deletes the specified professor.

    Path Parameters:
        - pk: Professor primary key (integer)

    Returns 204 No Content on success, or 404 if the professor does not exist.
    """
    try:
        professor = Professor.objects.get(pk=pk)
        professor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsStudent])
def createReview(request, pk):
    """
    Create or update a review for a professor.

    **POST**: If the user has already reviewed, updates the review. Otherwise, creates a new review.

    Path Parameters:
        - pk: Professor primary key (integer)

    Request Body:
        - rating: integer
        - comment: string
        - ... (other fields as required by ReviewSerializer)

    Returns the created or updated review data on success.
    """
    try:
        professor = Professor.objects.get(pk=pk)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)

    # If user already reviewed, update the review
    data = request.data.copy()
    data['professor'] = professor.id
    review = Review.objects.filter(professor=professor, creator_id=request.user.id).first()
    if review:
        serializer = ReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            avg_rating = professor.reviews.aggregate(Avg('rating'))['rating__avg']
            professor.rating = round(avg_rating, 1) if avg_rating else 0.0
            professor.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(creator_id=request.user.id)
            avg_rating = professor.reviews.aggregate(Avg('rating'))['rating__avg']
            professor.rating = round(avg_rating, 1) if avg_rating else 0.0
            professor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE review endpoint
from rest_framework.permissions import IsAuthenticated
@api_view(['DELETE'])
@permission_classes([IsStudent])
def deleteReview(request, prof_pk, review_pk):
    """
    Delete a review for a professor.

    **DELETE**: Deletes the specified review if the user is the creator or has admin/staff role.

    Path Parameters:
        - prof_pk: Professor primary key (integer)
        - review_pk: Review primary key (integer)

    Returns 204 No Content on success, 404 if not found, or 403 if permission denied.
    """
    try:
        professor = Professor.objects.get(pk=prof_pk)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        review = Review.objects.get(pk=review_pk, professor=professor)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    # Only allow the review's creator or admin/staff to delete
    user_role = getattr(request.user, 'role', None)
    if review.creator_id != request.user.id and user_role not in ["ADMIN", "STAFF"]:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    review.delete()
    # Update professor's average rating
    avg_rating = professor.reviews.aggregate(Avg('rating'))['rating__avg']
    professor.rating = round(avg_rating, 1) if avg_rating else 0.0
    professor.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
