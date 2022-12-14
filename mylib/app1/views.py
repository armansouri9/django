from multiprocessing import context
from django.shortcuts import render
from . import models
from django.views import generic
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from . import forms
# Create your views here.


# def index(request):
#     """
#     View function for home page of site.
#     """
#     # Generate counts of some of the main objects
#     num_books=models.Book.objects.all().count()
#     num_instances=models.BookInstance.objects.all().count()
#     # Available books (status = 'a')
#     num_instances_available=models.BookInstance.objects.filter(status__exact='a').count()
#     num_authors=models.Author.objects.count()  # The 'all()' is implied by default.
    
#     # Render the HTML template index.html with the data in the context variable
#     return render(
#         request,
#         'app1/index.html',
#         context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors},
#     )


class index(generic.TemplateView):

    template_name = "app1/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['num_books'] = models.Book.objects.all().count()
        context['num_instances'] = models.BookInstance.objects.all().count()
        context['num_instances_available'] = models.BookInstance.objects.filter(status__exact='a').count()
        context['num_authors'] = models.Author.objects.count()

        return context


class BookListView(generic.ListView):
    model =models.Book
    template_name="app1/book_list.html"


class BookDetailView(generic.DetailView):
    model=models.Book
    template_name="app1/book_detail.html"

class AuthorListView(LoginRequiredMixin,generic.ListView):
    login_url='/accounts/login/'
    redirect_field_name='next'

    model=models.Author
    template_name="app1/author_list.html"

login_required()
def auth_check(request):
    context={'groups':request.user.groups.all()}
    return render(request,'app1/auth_check.html',context)



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = models.BookInstance
    template_name ='app1/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return models.BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')







# from django.contrib.auth.decorators import permission_required

# @permission_required('catalog.can_mark_returned')
# @permission_required('catalog.can_edit')
# def my_view(request):
#     pass

# from django.contrib.auth.mixins import PermissionRequiredMixin

# class MyView(PermissionRequiredMixin, View):
#     permission_required = 'catalog.can_mark_returned'
#     # Or multiple permissions
#     permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
#     # Note that 'catalog.can_edit' is just an example
#     # the catalog application doesn't have such permission!





# @permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(models.BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = forms.RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('app1:my-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = forms.RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'app1/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})