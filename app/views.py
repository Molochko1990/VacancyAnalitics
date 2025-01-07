from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def statistics_view(request):
    # Здесь будет логика получения и обработки данных
    context = {}  # Контекст для передачи данных в шаблон
    return render(request, 'statistics.html', context)