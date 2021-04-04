## Software Requirements
* python 3.6+
* redis
* postgresql

## Application setup & running
1. Clone the repo and `cd` into the folder
2. Create virtual environment (optional)
3. Execute `pip install -r requirements.txt`
4. Rename **.env.sample** to **.env** and fill in the values.
5. Execute `python manage.py populate_database`
6. Execute `python manage.py run runserver`

## Testing
To run tests execute `python manage.py test -k`