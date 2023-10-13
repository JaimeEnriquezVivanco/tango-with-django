from django.test import TestCase
from rango.models import Category
from django.urls import reverse

def add_category(name, views=0, likes=0):
  category = Category.objects.get_or_create(name=name)[0]
  category.views = views
  category.likes = likes

  category.save()
  return category

# Create your tests here.
class CategoryMethodTests(TestCase):

  def test_ensure_views_are_positive(self):
    """
    Ensure number of views for a Category are >=0
    """
    category = add_category('test', -1, 0)

    self.assertEqual((category.views >= 0), True)

  def test_slug_line_creation(self):
    """
    Check when category is created
    proper slug is also created
    i.e: "CaTeGoRy NamE" -> 'category-name'
    """
    category = add_category('TesT sTrinG')
    category.save() # saving creates slug

    self.assertEqual(category.slug, 'test-string')

class IndexViewTests(TestCase):
  def test_index_view_with_no_categories(self):
    """
    If no categories exist, display message
    """
    response = self.client.get(reverse('rango:index'))

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'There are no categories present.')
    self.assertQuerySetEqual(response.context['categories'], [])
  
  def test_index_view_with_categories(self):
    """
    Checks whether categories are displayed correctly when present.
    """
    add_category('Python', 1, 1)
    add_category('C++', 1, 1)
    add_category('Erlang', 1, 1)

    response = self.client.get(reverse('rango:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Python')
    self.assertContains(response, 'C++')
    self.assertContains(response, 'Erlang')

    num_categories = len(response.context['categories'])
    self.assertEquals(num_categories, 3)


