# Course Administration API

In this project, I create a Python backend system using FastAPI web framework and MongoDB database for course information storage. The system allows users to access course details, view chapers, rate individual chapters, and aggregate ratings.

## API Endpoints design

| Endpoint                          | Request Type | Description                                                    |
| --------------------------------- | ------------ | -------------------------------------------------------------- |
| /courses                          | GET          | Get a list of all available courses with sorting options.      |
| /courses/{course_id}              | GET          | Get the overview of a specific course identified by course_id. |
| /courses/{course_id}/{chapter_id} | GET          | Get information about a specific chapter within a course.      |
| /courses/{course_id}/{chapter_id} | POST         | Rate a specific chapter within a course.                       |
