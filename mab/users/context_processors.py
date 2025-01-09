def get_main_menu(request):
    menu = []

    if request.user.is_anonymous:
        return {'mainmenu': menu}

    if request.user.is_accountant:
        menu.append({'title': "Главная страница", 'url_name': 'calculation:accruals'})
        menu.append({'title': "Создать начисления", 'url_name': 'calculation:createAccruals'})
    else:
        menu.append({'title': "Главная страница", 'url_name': 'calculation:customers'})
        menu.append({'title': "Добавить показания", 'url_name': 'calculation:addReadings'})

    return {'mainmenu': menu}
