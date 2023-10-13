from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime
from rango.bing_search import run_query
from django.contrib.auth.models import User
from rango.models import UserProfile
from django.utils import timezone

# registration imports
from rango.forms import UserForm, UserProfileForm

# authentication import
from django.contrib.auth.decorators import login_required

# login imports
from django.contrib.auth import authenticate, login

# logout import
from django.contrib.auth import logout

# class-based views imports
from django.views import View
from django.utils.decorators import method_decorator

# Create your views here.
# def index(request):
#     context_dict = {}

#     page_list = Page.objects.order_by('-views')[0:5]
#     category_list = Category.objects.order_by('-likes')[0:5]

#     context_dict['boldmessage'] = "Crunchy, creamy, cookie, candy, cupcake!"
#     context_dict['categories'] = category_list
#     context_dict['pages'] = page_list
    
#     visitor_cookie_handler(request)
#     #context_dict['visits'] = request.session['visits']

#     response = render(request, 'rango/index.html', context=context_dict)
#     return response

class IndexView(View):
    def get(self, request):
        context = {}
        page_list = Page.objects.order_by('-views')[0:5]
        category_list = Category.objects.order_by('-likes')[0:5]

        context['boldmessage'] = "Crunchy, creamy, cookie, candy, cupcake!"
        context['categories'] = category_list
        context['pages'] = page_list
        
        visitor_cookie_handler(request)
        context['visits'] = request.session['visits']

        return render(request, 'rango/index.html', context)

# def about(request):
#     context_dict = {}
#     visitor_cookie_handler(request)
#     context_dict['visits'] = request.session['visits']

#     return render(request, 'rango/about.html', context_dict)

class AboutView(View):
    def get(self, request):
        context = {}
        visitor_cookie_handler(request)
        context['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context)

# def show_category(request, category_name_slug):
#     context_dict = {}
#     result_list = []
#     query=""
#     if request.method == 'POST':
#         query = request.POST['query'].strip()
#         if query:
#             result_list = run_query(query)
        
#     try:
#         category = Category.objects.get(slug=category_name_slug)
#         pages = Page.objects.filter(category=category).order_by('-views')
    
#         context_dict['category'] = category
#         context_dict['pages'] = pages        
#         context_dict['result_list'] = result_list        

#     except Category.DoesNotExist:
#         context_dict['category'] = None
#         context_dict['pages'] = None

#     return render(request, 'rango/category.html', context=context_dict)

class ShowCategoryView(View):
    
    def populate_context(self, category_name_slug):
        context = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
        
            context['category'] = category
            context['pages'] = pages

        except Category.DoesNotExist:
            context['category'] = None
            context['pages'] = None

        return context

    def get(self, request, category_name_slug):
        context = self.populate_context(category_name_slug)
        return render(request, 'rango/category.html', context)
    
    # bing search
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        context = self.populate_context(category_name_slug)
        
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context['result_list'] = result_list
            context['query'] = query
        return render(request, 'rango/category.html', context)

# @login_required
# def add_category(request):
#     form = CategoryForm()

#     if request.method == 'POST':
#         form = CategoryForm(request.POST)

#         if form.is_valid():
#             form.save(commit=True)
#             return redirect('/rango/')
#         else:
#             print(form.errors)
    
#     return render(request, 'rango/add_category.html', {'form': form})

class AddCategoryView(View):
    
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)
        
        return render(request, 'rango/add_category.html', {'form': form})

# @login_required
# def add_page(request, category_name_slug):

#     try:
#         category = Category.objects.get(slug=category_name_slug)
#     except:
#         category = None

#     if category is None:
#         return redirect('/rango/')

#     form = PageForm()

#     if request.method == 'POST':
        
#         form = PageForm(request.POST)

#         if form.is_valid():
#             if category:
#                 page = form.save(commit=False)
#                 page.category = category
#                 page.views = 0
#                 page.save()
            
#             return redirect(reverse('rango:show_category',
#                                     kwargs={'category_name_slug':
#                                             category_name_slug}))
        
#         else:
#             print(form.errors)
#     context_dict = {'form': form, 'category': category}
#     return render(request, 'rango/add_page.html', context=context_dict)

class AddPageView(View):
    def find_category(self, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        return category

    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        category = self.find_category(category_name_slug)
        
        if category is None:
            return redirect('/rango/')
        
        form = PageForm()
        context = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        
        form = PageForm(request.POST)
        category = self.find_category(category_name_slug)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            
            return redirect(reverse('rango:show_category',
                                    kwargs={'category_name_slug':
                                            category_name_slug}))
        
        else:
            print(form.errors)
        context = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context)

# def register(request):
#     registered = False

#     if request.method == 'POST':
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)

#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()

#             user.set_password(user.password)
#             user.save()

#             profile = profile_form.save(commit=False)
#             profile.user = user

#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']

#             profile.save()

#             registered = True
#         else:
#             # print problems to terminal
#             print(user_form.errors, profile_form.errors)
#     else:
#         # if request is not POST,
#         # render form using 2 ModelForm instances
#         user_form = UserForm()
#         profile_form = UserProfileForm()

#     return render(request,
#                   'rango/register.html',
#                   context = {'user_form': user_form,
#                              'profile_form': profile_form,
#                              'registered': registered
#                             }
#             )

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(username=username, password=password)

#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return redirect(reverse('rango:index'))
#             else:
#                 return HttpResponse("Your Rango account is disabled.")
#         else:
#             print(f'Invalid login details: {username}, {password}')
#             return HttpResponse("Invalid login details supplied.")
#     else:
#         return render(request, 'rango/login.html')
    
# @login_required
# def restricted(request):
#     return render(request, 'rango/restricted.html')

class RestrictedView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'rango/restricted.html')

# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect(reverse('rango:index'))

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', 1))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# def search(request):
#     result_list = []
#     query=""
#     if request.method == 'POST':
#         query = request.POST['query'].strip()
#         if query:
#             result_list = run_query(query)
    
#     return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})
    
# def goto_url(request):
#     page_id = None

#     if request.method == 'GET':
#         try:
#             page_id = request.GET.get('page_id')
        
#             page = Page.objects.get(id=page_id)
#             page.views = page.views + 1
#             page.save()

#             return redirect(page.url)

#         except:
#             return redirect(reverse('rango:index'))
        
class GotoUrlView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')
        
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))

        page.views = page.views + 1
        page.last_visit = timezone.now()
        page.save()
        return redirect(page.url)
    
@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

    context = {}
    context['form'] = form
    return render(request, 'rango/profile_registration.html', context=context)

class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context = {'form': form}
        return render(request, 'rango/profile_registration.html', context)
    
    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect(reverse('rango:index'))
        
        else:
            print(form.errors)

        context = {'form': form}
        return render(request, 'rango/profile_registration.html', context)        

class ProfileView(View):
    def find_user(self, username):
        try:
            user = User.objects.get(username=username)
            return user
        except:
            return None

    @method_decorator(login_required)
    def get(self, request, username):
        user = self.find_user(username)

        if not user: #user does not exist
            return redirect(reverse('rango:index'))
        
        # get_or_create() returns tuple
        # element 0 is requested object
        profile = UserProfile.objects.get_or_create(user=user)[0]

        form = UserProfileForm({'website': profile.website,
                                'picture': profile.picture
        })
        
        context = {'form': form,
                   'profile': profile,
                   'selected_user': user
        }

        return render(request, 'rango/profile.html', context)
    
    # update user's own profile
    @method_decorator(login_required)
    def post(self, request, username):
        user = self.find_user(username)

        if not user: #user does not exist
           return redirect(reverse('rango:index'))
        
        profile = UserProfile.objects.get_or_create(user=user)[0]

        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango/profile.html'), user.username)
        else:
            print(form.errors)
        
        context = {'form': form,
                   'profile': profile,
                   'selected_user': user,
        }

        return render(request, 'rango/profile.html', context)
    
class ListProfilesView(View):
    def get(self, request):
        #users = User.objects.all().order_by('username')
        profiles = UserProfile.objects.all().order_by('user__username')
        context = {'profiles': profiles}

        return render(request, 'rango/list_profiles.html', context)
    
class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        category_id = int(category_id)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        
        category.likes += 1
        category.save()
        return HttpResponse(category.likes)
    
# aux func
def get_category_list(max_results=0, starts_with=''):
    '''
    Returns list of categories that start with *starts_with*
    Returns all categories if query is empty
    '''
    matches = Category.objects.filter(name__istartswith=starts_with)
    
    if not starts_with:
        #empty query returns all categories
        pass
    elif max_results != 0 and len(matches) > max_results:
        matches = matches[0:max_results]
    
    return matches

class CategorySuggestionView(View):
    def get(self, request):
        if request.GET:
            suggestion_query = request.GET['suggestion_query']
            matches = get_category_list(8, suggestion_query)
        
        context = {'categories': matches}

        return render(request,
                      'rango/categories.html',
                      context)
    
class AddSearchResultView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_name = request.GET.get('category_name')
        category = Category.objects.get(name=category_name)
        
        new_page = Page(
            category=category,
            title = request.GET.get('title'),
            url = request.GET.get('url')
        )
        new_page.save()

        pages = Page.objects.filter(category=category).order_by('-views')

        context = {'pages': pages}

        return render(request,
                      'rango/category-pages.html',
                      context)