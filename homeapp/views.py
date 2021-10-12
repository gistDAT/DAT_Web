from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from homeapp.models import places


def home_view(request):

    if request.method == "POST":
        # temp = request.POST.get('place_input'
        temp = request.POST.get('place_input')

        new_place = places()
        new_place.text = temp
        new_place.save()
        return render(request,'homeapp/home_view.html', context={'text': temp})
    else:
        return render(request, 'homeapp/home_view.html', context={'text': '장소를 입력하세요!'})