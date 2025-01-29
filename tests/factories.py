import factory
import faker
from django.contrib.auth import get_user_model

from cafe.models import Item
from users.models import EmailAddress

User = get_user_model()


class UserRegularFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: faker.Faker().email())
    password = factory.LazyFunction(lambda: faker.Faker().password())
    is_staff = False


class EmailAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    email_address = factory.LazyFunction(lambda: faker.Faker().email())
    verified = True
    user = factory.SubFactory(UserRegularFactory)


class UserRegularPasswordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: faker.Faker().email())
    password = 'asd'
    is_staff = False


class EmailAddressPasswordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    email_address = factory.LazyFunction(lambda: faker.Faker().email())
    verified = True
    user = factory.SubFactory(UserRegularPasswordFactory)


class UserAdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: faker.Faker().email())
    password = factory.LazyFunction(lambda: faker.Faker().password())
    is_staff = True


class EmailAddressAdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    email_address = factory.LazyFunction(lambda: faker.Faker().email())
    verified = True
    user = factory.SubFactory(UserAdminFactory)


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.LazyFunction(lambda: faker.Faker().random_element(['Паста', 'Суп', 'Пиво']))
    price = factory.LazyFunction(lambda: faker.Faker().random_int(min=200, max=700))
