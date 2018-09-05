import abc

from django.test import TestCase
from tests.factories import PersonFactory
from tests.factories import PersonLocationFactory
from tests.factories import PetFactory
from tests.factories import TaggedItemFactory
from tests.test_app_1.models import MockPersonLocation
from tests.test_app_1.models import MockPet
from tests.test_app_2.models import MockTaggedItem

from django_related_models.related_models import ModelMap
from django_related_models.related_models import RelatedModels
from django_related_models.related_models import get_related_objects


class GetRelatedModelsTests(TestCase):

    def test_get_related_fk_objects(self):
        person = PersonFactory.create()
        for i in range(3):
            PetFactory.create(owner=person)
        location = PersonLocationFactory.create(owner=person)

        related_objects = get_related_objects(person)
        self.assertEqual(len(related_objects[MockPet.owner.field]), 3)

        for pet in related_objects[MockPet.owner.field]:
            self.assertEqual(pet.owner.id, person.id)
        self.assertEqual(len(related_objects[MockPersonLocation.owner.field]), 1)

        for location in related_objects[MockPersonLocation.owner.field]:
            self.assertEqual(location.owner.id, person.id)

    def test_get_related_generic_fk_objects(self):
        person = PersonFactory.create()
        tagged_item = TaggedItemFactory.create(
            tag='dog-person',
            content_object=person
        )
        related_objects = get_related_objects(person)
        self.assertEqual(len(related_objects[MockTaggedItem.content_object]), 1)
        for tagged_item in related_objects[MockTaggedItem.content_object]:
            self.assertEqual(tagged_item.content_object.id, person.id)


class ModelMapTestsMixin(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def setUpTestData(cls):
        super(ModelMapTestsMixin, cls).setUpTestData()
        cls.instance = PersonFactory.create()
        cls.field = cls.get_field()
        cls.model_map = cls.get_model_map()

    @classmethod
    def get_model_map(cls, **kwargs):
        kwargs = dict({
            'target_model': type(cls.instance),
            'field': cls.field,
        }, **kwargs)
        return ModelMap(**kwargs)

    @classmethod
    @abc.abstractmethod
    def get_field(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def get_related_object(cls):
        pass


class ModelMapTests(ModelMapTestsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(ModelMapTests, cls).setUpTestData()
        cls.pet = PetFactory.create(owner=cls.instance)

    @classmethod
    def get_field(cls):
        return MockPet._meta.get_field('owner')

    def test_field(self):
        self.assertEqual(self.model_map.field, self.field)

    def test_model(self):
        self.assertEqual(self.model_map.model, MockPet)

    def test_generic_foreign_key(self):
        self.assertIsNone(self.model_map.generic_foreign_key)

    def test_get_related_objects(self):
        new_pet = PetFactory.create(owner=self.instance)
        self.assertEqual(
            list(self.model_map.get_related_objects(self.instance)),
            [self.pet, new_pet]
        )

    def test_get_related_objects_extra_kwargs(self):
        new_pet = PetFactory.create(owner=self.instance)
        self.assertEqual(
            list(self.model_map.get_related_objects(self.instance, pk=new_pet.pk)),
            [new_pet]
        )


class ModelMapGenericForeignKeyTests(ModelMapTestsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(ModelMapGenericForeignKeyTests, cls).setUpTestData()
        cls.tagged_item = TaggedItemFactory.create(
            tag='dog-person',
            content_object=cls.instance
        )

    @classmethod
    def get_field(cls):
        return MockTaggedItem._meta.get_field('content_object')

    @classmethod
    def get_related_object(cls):
        return cls.tagged_item

    def test_field(self):
        self.assertEqual(
            self.model_map.field,
            MockTaggedItem._meta.get_field('object_id')
        )

    def test_model(self):
        self.assertEqual(self.model_map.model, MockTaggedItem)

    def test_generic_foreign_key(self):
        self.assertEqual(self.model_map.generic_foreign_key, self.get_field())

    def test_get_related_objects(self):
        self.assertEqual(
            list(self.model_map.get_related_objects(self.instance)),
            [self.tagged_item]
        )

    def test_get_related_objects_extra_kwargs(self):
        tagged_item = TaggedItemFactory.create(
            tag='cat-person',
            content_object=self.instance
        )
        self.assertEqual(
            list(self.model_map.get_related_objects(self.instance, pk=tagged_item.pk)),
            [tagged_item]
        )


class RelatedModelsTests(TestCase):
    def setUp(self):
        super(RelatedModelsTests, self).setUp()
        self.related_models = RelatedModels()

    def test_should_consider(self):
        self.assertTrue(self.related_models.should_consider(MockPet))

    def test_should_consider_excluded_model(self):
        rm = RelatedModels(exclude=[MockPet])
        self.assertFalse(rm.should_consider(MockPet))

    def test_should_consider_excluded_app(self):
        rm = RelatedModels(exclude_apps=[MockPet._meta.app_label])
        self.assertFalse(rm.should_consider(MockPet))

    def test_should_consider_included_app_true(self):
        rm = RelatedModels(include_apps=[MockPet._meta.app_label])
        self.assertTrue(rm.should_consider(MockPet))

    def test_should_consider_included_app_false(self):
        rm = RelatedModels(include_apps=[MockPet._meta.app_label])
        self.assertFalse(rm.should_consider(MockTaggedItem))
