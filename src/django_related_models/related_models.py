from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class GetDefaultManagerMixin(object):
    """
    A mixin which provides a method to get a default manager for
    a given model.  This is useful if the normal ":attr:`objects`" manager
    associated to that class has some built-in filtering.
    """
    def get_default_manager(self, model):
        """
        Returns a default manager for *model*.

        :rtype: :class:`django.db.models.manager.Manager`
        """
        return model._default_manager


class ModelMap(GetDefaultManagerMixin, object):
    """
    This purpose of this class is to hold information and provide
    utility functions about getting all instances where :attr:`field` is
    a foreign key to :attr:`instance` which is of type :attr:`instance_type`.

    The :attr:`model` is the model associated to :attr:`field`.

    The :attr:`target_field` attribute is the field on the type
    of :attr:`instance`.  Similarly, :attr:`target_model`
    is the model of :attr:`instance`.

    This class also abstracts away some of the difference between
    normal foreign keys and generic foreign keys.  In the case of a
    generic foreign key, :attr:`generic_foreign_key` will be set to that
    field, :attr:`field` will be the concrete "object id" field, and
    :attr:`target_field` will be the primary key on :attr:`target_model`.
    """

    def __init__(self, instance_type, field):
        if isinstance(field, GenericForeignKey):
            # For generic foreign keys, fk_field is the name of the
            # field which needs to be updated and the target field
            # will be the primary key of *model*
            self.generic_foreign_key = field
            self.field = field.model._meta.get_field(field.fk_field)
            self.target_field = instance_type._meta.pk
        else:
            self.generic_foreign_key = None
            self.field = field
            self.target_field = field.target_field

        self.model = self.field.model
        self.target_model = self.target_field.model

    def get_default_manager(self, model=None):
        """
        Returns a default manager for *model*.  If *model* is ``None``,
        then it will return a default manager for :attr:`model`, which
        is the same as :attr:`field.model`.

        :rtype: :class:`django.db.models.manager.Manager`
        """
        model = model or self.model
        return super(ModelMap, self).get_default_manager(model)

    def get_related_objects(self, instance, **kwargs):
        """
        Returns a :class:`~django.db.models.QuerySet` for :attr:`model`
        for the rows that are associated to *instance*.

        Any *kwargs* passed in will be additional filters applied to the
        queryset.

        :type instance: :attr:`model`
        :rtype: :class:`django.db.models.QuerySet`
        """
        # If we have a generic foreign key, we need to additionally
        # filter by the content type of the target model
        if self.generic_foreign_key is not None:
            content_type = ContentType.objects.get_for_model(self.target_model)
            kwargs = dict({
                self.generic_foreign_key.ct_field: content_type
            }, **kwargs)

        kwargs = dict({
            self.field.name: getattr(instance, self.target_field.name)
        }, **kwargs)
        return self.get_default_manager().filter(**kwargs)


class RelatedModels(GetDefaultManagerMixin, object):
    """
    This class is designed to help finding all of the other models
    related to a given model.
    """
    def __init__(
            self,
            include=None,
            include_apps=None,
            exclude=None,
            exclude_apps=None):
        self.include = include
        self.include_apps = include_apps
        self.exclude = set(exclude or [])
        self.exclude_apps = set(exclude_apps or [])
        self.generic_foreign_key_cache = {}

    def _model_matches(self, model, model_list, app_list):
        """
        Returns whether or not *model* appears in *model_list* or it's app
        appears in *app_list*.

        :rtype: bool
        """
        if model_list is not None and model in model_list:
            return True
        if app_list is not None and model._meta.app_label in app_list:
            return True
        return False

    def should_consider(self, other_model):
        """
        Returns whether or not we should consider the fields on
        *other_model*.

        :rtype: bool
        """
        if self._model_matches(other_model, self.exclude, self.exclude_apps):
            return False

        if self._model_matches(other_model, self.include, self.include_apps):
            return True

        return self.include is None and self.include_apps is None

    def should_include_field(self, field, model):
        """
        Returns whether or not *field* is (or should be considered) as a
        a foreign key to *model*.

        :rtype: bool
        """
        related_model = getattr(field, 'related_model', None)
        related_model_matches = related_model == model
        generic_foreign_key = isinstance(field, GenericForeignKey)

        if generic_foreign_key:
            return True
        else:
            return (
                related_model_matches and field.concrete and not field.many_to_many
            )

    def should_include_virtual_field(self, field, model):
        """
        Returns whether or not the virtual *field* should be considered
        as a foreign key to *model*.

        Currently, we only support
        :class:`~django.contrib.contenttypes.fields.GenericForeignKey`
        field.  Additionally, we check to see if there are rows in
        the database which reference *model*.

        :rtype: bool
        """
        return (
            isinstance(field, GenericForeignKey) and
            self.has_generic_foreign_key_to_model(field, model)
        )

    def has_generic_foreign_key_to_model(self, field, model):
        """
        Returns whether or not the generic foreign key *field* has any
        references to *model*.

        We cache the content types which are referenced by *field*
        into :attr:`generic_foreign_key_cache`.

        :rtype: bool
        """
        content_type_ids = self.generic_foreign_key_cache.get(field)
        if content_type_ids is None:
            content_type_ids = set(
                self.get_default_manager(field.model).values_list(
                    field.ct_field,
                    flat=True
                ).order_by().distinct()
            )
            self.generic_foreign_key_cache[field] = content_type_ids

        if not content_type_ids:
            return False

        ct = ContentType.objects.get_for_model(model)
        return ct.id in content_type_ids

    def has_virutal_fields(self, model):
        return hasattr(model._meta, 'virtual_fields')

    def get_related_fields(self, model, other_model):
        """
        Returns all of the fields on *other_model* which are (or could be)
        foreign keys to *model*.

        :type model: :class:`django.db.models.Model`
        :type other_model: :class:`django.db.models.Model`

        :rtype: List[Field]
        """
        real_fields = [
            field
            for field in other_model._meta.get_fields()
            if self.should_include_field(field, model)
        ]

        if self.has_virutal_fields(other_model):
            virtual_fields = [
                field
                for field in other_model._meta.virtual_fields
                if self.should_include_virtual_field(field, model)
            ]
            return real_fields + virtual_fields
        else:
            return real_fields

    def get_referring_models(self, model):
        """
        Returns all of the models which have a (possibly generic)foreign key to
        *model*.

        :rtype: Dict[Model, List[Field]]
        """
        referring_models = {
            other_model: self.get_related_fields(model, other_model)
            for other_model in apps.get_models(include_auto_created=True)
            if self.should_consider(other_model)
        }
        return {
            other_model: fields
            for other_model, fields in referring_models.items()
            if fields
        }


def get_related_objects(instance, **kwargs):
    """
    Returns all the instances of all the models which have a (possibly generic) foreign key to
    *instance*.

    :rtype: Dict[Field, List[Object]]
    """
    model = instance._meta.model
    related_models = RelatedModels()
    referring_models = related_models.get_referring_models(model)

    all_related_objects = {}
    for reffering_model, fields in referring_models.items():
        for field in fields:
            objects_map = ModelMap(type(instance), field)
            related_objects = objects_map.get_related_objects(instance, **kwargs)
            if related_objects:
                all_related_objects[field] = [obj for obj in related_objects]
    return all_related_objects
