from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from . models import Task
from django.views import View

class TaskList(ListView):
    model = Task
    context_object_name='task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if the user is authenticated
        if self.request.user.is_authenticated:
            # Filter tasks based on the authenticated user
            context['task'] = context['task'].filter(user=self.request.user)
            context['count'] = context['task'].filter(complete=False).count()
        else:
            # If user is not authenticated, provide an empty queryset
            context['task'] = Task.objects.none()
            context['count'] = 0
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['task'] = context['task'].filter(title__icontains=search_input)
            context['search_input'] = search_input

        return context
    
class TaskDetail(DetailView):
    model = Task
    context_object_name='task'
    template_name = 'todo/task.html'
    
class TaskCreate(CreateView):
    model = Task
    # fields = "__all__"
    fields= ['title', 'description', 'complete']
    # fields = ['title','description']
    success_url = reverse_lazy('task')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
class TaskUpdate(UpdateView):
    model = Task
    fields= ['title', 'description', 'complete']
    success_url = reverse_lazy('task')
    
class TaskDelete(DeleteView):
    model = Task
    context_object_name='task'
    success_url = reverse_lazy('task')
      
class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = "__all__"
    redirect_authenticated_user = False
    
    def get_success_url(self):
        return reverse_lazy('task')
    
class CustomLogoutView(View):
    template_name = 'todo/logout.html' 

    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('task'))  
    

class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:  # Fix typo here
            return redirect('task')
        return super(RegisterPage, self).get(*args, **kwargs) 