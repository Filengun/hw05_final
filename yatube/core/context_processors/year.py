import datetime


def year(request):
    today = datetime.datetime.now().year
    return {'year': today}
