# Test Hawsr
## Test 1:
There are some points to improve in the provided models which are in my opinion:
- Unless there is a need for flexibility to add more user types, it is better to swap out the role choices to a simple 'is_admin' boolean field. 
- If the phone number is not required than it shouldn't be unique.
- Phone field would benefit from a regex validator.
- I believe the user notifications model shouldn't allow a "null" value for user and notification fields.
- Created field in basemodel should be changed to use auto_add_now because it is not a user editable field.
- Status should be per user notification.
- Notification and user in UserNotification should be unique together.
- It would be cleaner to upload files to a directory.
- Concerning the choices, it is a project preference, dealing with IntegerChoices means that the data will take less space in the database, but it will be a bit ambiguous when developing although that could be fixed through a modified serializer. In my opinion, unless there is an expectency of +10 million rows in the database, it is not worth using IntegerChoices but rather opt to use TextChoices.
- In case of an authentication system, the user model would need:
    - Password.
    - User object manager.


## Test 2:
### Installation:
```bash
# 1: Create a virtual environment (virtualenv or conda...)
python -m virtualenv venv

#2: Activate virtual environment
source venv/bin/activate

#3: Install dependencies
pip install -r requirements.txt

#4: Migrate
python manage.py migrate

#5: Run
python manage.py runserver
```


### Documentation
Docs can be found at any of these links (requires running server to check):
 - [Swagger-UI](http://localhost:8000/api/schema/swagger-ui/)
 - [Redoc](http://localhost:8000/api/schema/swagger-ui/)
