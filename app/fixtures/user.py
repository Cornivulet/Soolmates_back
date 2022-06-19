import random

import factory
from faker import Faker

import app.models

fake = Faker('fr_FR')

gender_list = [
    "male",
    "female",
    "other"
]

male_firstnames_list = [
    "Thomas",
    "Roger",
    "Victor",
    "Jean",
    "Paul",
    "Martin",
    "Pierre",
    "Jacques",
    "Abdalzahk",
    "Fellipe"
]
female_firstnames_list = [
    "Marie",
    "Flore",
    "Diane",
    "Alberta",
    "Miryam",
    "Tsukiko",
    "Amira",
    "Ilya",
    "Sophie",
    "Lena"
]
valid_non_binary_first_names = [
    "Morgan",
    "Camille",
    "Ange",
    "Aeris",
    "Aurore"
]
criterias = [
    "F",
    "A",
    "U",
    "L"
]


class UserFactory(factory.Factory):
    class Meta:
        model = app.models.User

    gender = fake.random.choice(gender_list)
    match gender:
        case "male":
            name = random.choice(male_firstnames_list)
        case "female":
            name = random.choice(female_firstnames_list)
        case "other":
            name = random.choice(valid_non_binary_first_names)
    age = random.randint(18, 60)
    image = "temp"
    is_active = True
    description = fake.text()
    email = fake.email()
    password = "Azerty123"
    is_superuser = False
    is_staff = False
    date_joined = fake.date_time_between(start_date="-1y", end_date="now")
    lf_criteria = fake.random.choices(criterias)
    lf_age_from = random.randint(18, 60)
    lf_age_to = random.randint(lf_age_from, 60)
    lf_gender = random.choices(gender_list)
