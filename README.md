[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

Training django and DRF project.

Part of [Open Classrooms](https://openclassrooms.com) "DA Python" formation, 10th Project.

# SoftDesk API

SoftDesk API serves endpoints to consult and modify SoftDesk data designated for SoftDesk Front-end apps (Website, Android and IOS mobile apps)

## Postman Documentation:

https://documenter.getpostman.com/view/17349279/UVR8o7FG

## Local testing

### Creating Virtual environment and downloading the program:

You need Python 3 (tested on 3.9.5), git and venv installed on your machine.

Open a terminal and navigate into the folder you want SoftDesk API to be downloaded, and run the following commands:

* On Linux or macOS:
```bash
git clone https://github.com/YoannDeb/SoftDesk.git
cd SoftDesk
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cd SoftDesk
python manage.py runserver
```

* On Windows:
```bash
git clone https://github.com/YoannDeb/SoftDesk.git
cd SoftDesk
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
cd softDesk
python manage.py runserver
```

### Initializing database and run the program:

with virtual environnement activated (see previous chapter):

```bash
cd SoftDesk
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

SoftDesk will be accessible at http://127.0.0.1:8000

See [documentation](https://documenter.getpostman.com/view/17349279/UVR8o7FG) to see details about endpoints.