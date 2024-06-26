def get_main_menu(request):
    menu = []

    if request.user.is_anonymous:
        return {'mainmenu': menu}

    if request.user.is_accountant:
        menu.append({'title': "Главная страница", 'url_name': 'calculation:home'})
    else:
        menu.append({'title': "Главная страница", 'url_name': 'calculation:home'})
        menu.append({'title': "Добавить показания", 'url_name': 'calculation:addReadings'})
        menu.append({'title': "Добавить показания new", 'url_name': 'calculation:addReadingsNew'})

    return {'mainmenu': menu}
