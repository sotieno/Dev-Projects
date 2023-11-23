"""
Courses endpoints that retrieve courses.
"""

import contextlib
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends

# Import the get_db instance from dependencies.py
from src.dependencies import get_db

router = APIRouter()

# Get all courses
@router.get('/courses')
async def get_courses(sort_by: str = 'date', domain: str = None, db = Depends(get_db)):
    """
    Retrieve a list of courses with optional sorting and filtering.

    Parameters:
    - sort_by (str): Specifies the sorting criterion
        ('date', 'rating', or 'alphabetical'). Default is 'date'.
    - domain (str): Filters courses based on the specified domain.
        Default is None.

    Returns:
    List of courses based on the specified sorting and filtering criteria.
    """

    # Update the rating.total and rating.count for each course based on the sum of chapter ratings
    # This prepares the data for sorting by rating later in the code
    for course in db.courses.find():
        total = 0
        count = 0
        for chapter in course['chapters']:
            with contextlib.suppress(KeyError):
                total += chapter['rating']['total']
                count += chapter['rating']['count']
        db.courses.update_one({'_id': course['_id']}, {
            '$set': {'rating': {'total': total, 'count': count}}})

    # Determine sorting criteria and order based on the 'sort_by' parameter

    # Sorting by date in descending order
    if sort_by == 'date':
        sort_field = 'date'
        sort_order = -1

    # Sorting by rating in descending order
    elif sort_by == 'rating':
        sort_field = 'rating.total'
        sort_order = -1

    # Sorting alphabetically in ascending order
    else:
        sort_field = 'name'
        sort_order = 1

    # Construct the query for optional filtering based on the 'domain' parameter
    query = {}
    if domain:
        query['domain'] = domain

    # Retrieve and return the list of courses, applying sorting and filtering
    courses = db.courses.find(query, {
        'name': 1, 'date': 1, 'description': 1, 'domain': 1, 'rating': 1,
        '_id': 0}).sort(sort_field, sort_order)
    return list(courses)

# Get course overview by course_id
@router.get('/courses/{course_id}')
def get_course(course_id: str, db = Depends(get_db)):
    """
        Get details of a specific course by providing its ID.

        Args:
            course_id (str): The ID of the course to retrieve.
            include_chapters (bool, optional): Flag to include chapters in the response. Defaults to True.

        Returns:
            dict: Details of the specified course.
        """
    # Retrieve course details from the database
    course = db.courses.find_one({'_id': ObjectId(course_id)}, {'_id': 0, 'chapters': 0})

    # Check if the course exists
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')

    # Transform the rating structure for better response format
    try:
        course['rating'] = course['rating']['total']
    except KeyError:
        course['rating'] = 'Not rated yet'

    return course

# Rate chapter
@router.post('/courses/{course_id}/{chapter_id}')
def rate_chapter(course_id: str, chapter_id: str, rating: int = Query(..., gt=-2, lt=2), db = Depends(get_db)):
    """
        Rate a specific chapter within a course.

        Args:
            course_id (str): The ID of the course containing the chapter.
            chapter_id (str): The ID of the chapter to be rated.
            rating (int): The rating to assign to the chapter. Should be between -2 and 2 (inclusive).

        Returns:
            dict: Details of the rated chapter.
    """

    # Retrieve course details from the database
    course = db.courses.find_one({'_id': ObjectId(course_id)}, {'_id': 0, })

    # Check if the course exists
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')

    # Retrieve the list of chapters from the course
    chapters = course.get('chapters', [])

    # Retrieve the specified chapter
    try:
        chapter = chapters[int(chapter_id)]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=404, detail='Chapter not found') from e

    # Update the rating for the chapter
    try:
        chapter['rating']['total'] += rating
        chapter['rating']['count'] += 1
    except KeyError:
        chapter['rating'] = {'total': rating, 'count': 1}

    # Update the chapters in the course
    db.courses.update_one({'_id': ObjectId(course_id)}, {'$set': {'chapters': chapters}})
    return chapter
