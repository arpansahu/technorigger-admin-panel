from django.shortcuts import render
from django.template import RequestContext


def handler400(request, *args, **argv):
    return render(request, 'error/error_400.html', context={})


def handler500(request, *args, **argv):
    return render(request, 'error/error_500.html', context={})


def handler403(request, *args, **argv):
    return render(request, 'error/error_403.html', context={})


def handler404(request, *args, **argv):
    return render(request, 'error/error_404.html', context={})
