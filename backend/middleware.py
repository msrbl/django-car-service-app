from django.urls import resolve

class ExcludeFromAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список эндпоинтов, которые не требуют аутентификации
        excluded_endpoints = ['register', 'login', 'schema-swagger-ui']  # Добавьте нужные эндпоинты

        try:
            # Получаем имя эндпоинта из запроса
            match = resolve(request.path_info)
            endpoint_name = match.url_name

            if endpoint_name in excluded_endpoints:
                # Пропускаем аутентификацию для выбранных эндпоинтов
                return self.get_response(request)
        except Exception as e:
            # Обрабатываем исключения для случаев, когда URL не распознан
            pass

        # Для остальных запросов
        return self.get_response(request)