"""
This module contains the core classes needed to work with products in
Plata. The core classes should be used directly and not replaced even
if you provide your own product model implementation.

The core models are:

* ``TaxClass``
* ``ProductPrice``

(FIXME: They aren't enough abstract yet. Product, ProductVariation,
ProductImage, OptionGroup and Option should be moved somewhere else.)
"""

from django.db import models

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

import plata
from plata.compat import product as itertools_product
from plata.fields import CurrencyField
from plata.shop.models import Price, PriceManager, TaxClass


class CategoryManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def public(self):
        return self.filter(is_active=True, is_internal=False)


class Category(models.Model):
    """
    Categories are both used for external and internal organization of products.
    If the ``is_internal`` flag is set, categories will never appear in the shop
    but can be used f.e. to group discountable products together.
    """

    is_active = models.BooleanField(_('is active'), default=True)
    is_internal = models.BooleanField(_('is internal'), default=False,
        help_text=_('Only used to internally organize products, f.e. for discounting.'))

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    description = models.TextField(_('description'), blank=True)

    parent = models.ForeignKey('self', blank=True, null=True,
        limit_choices_to={'parent__isnull': True},
        related_name='children', verbose_name=_('parent'))

    class Meta:
        ordering = ['parent__ordering', 'parent__name', 'ordering', 'name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    objects = CategoryManager()

    def __unicode__(self):
        if self.parent_id:
            return u'%s - %s' % (self.parent, self.name)
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('plata_category_detail', (), {'object_id': self.pk})


class ProductPrice(Price):
    product = models.ForeignKey('product.Product', verbose_name=_('product'),
        related_name='prices')

    objects = PriceManager()
