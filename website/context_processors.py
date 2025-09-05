from .models import Passenger, Driver

def usertype_context(request):
    usertype = None
    if request.user.is_authenticated:
        if Passenger.objects.filter(user=request.user).exists():
            usertype = 'PASSENGER'
        elif Driver.objects.filter(user=request.user).exists():
            usertype = 'DRIVER'
    return {'usertype': usertype}
