from django.shortcuts import render
from .models import Employee

# Create your views here.
def testmysql(request):
    employee = Employee.objects.all()
    context = {
        'user_ssn': employee[0].ssn,
        'user_name': employee[0].lname,
    }
    return render(request, 'home.html', context)
