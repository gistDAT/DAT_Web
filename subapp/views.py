from django.shortcuts import render

# Create your views here.

def sub_view(request):
    return render(request, 'subapp/sub_view.html', context={}, )
