from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'analyses/home.html') # homepage = analyse page
