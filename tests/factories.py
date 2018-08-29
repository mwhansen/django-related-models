from __future__ import unicode_literals

import factory

from .models import MockPerson
from .models import MockPet
from .models import MockPersonLocation
from .models import MockTaggedItem


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = MockPerson

    first_name = factory.Sequence(lambda n: '\xd3scarNumber{}'.format(n))
    last_name = factory.Sequence(lambda n: 'Ib\xe1\xf1ezNumber{}'.format(n))


class PetFactory(factory.DjangoModelFactory):
    class Meta:
        model = MockPet

    name = factory.Sequence(lambda n: 'Buddy{}'.format(n))
    owner = factory.SubFactory(PersonFactory)


class PersonLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = MockPersonLocation

    address1 = factory.Sequence(lambda n: 'Middle of Nowhere.'.format(n))
    address2 = factory.Sequence(lambda n: 'No number, obviously.'.format(n))
    owner = factory.SubFactory(PersonFactory)


class TaggedItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = MockTaggedItem
