from django.http import HttpResponse

def home(request):
    return HttpResponse("<H1>HOME PAGE</H1>")
