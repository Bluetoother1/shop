from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BonusTransaction


@login_required
def bonus_history(request):
    # Получаем все транзакции для текущего пользователя
    transactions = BonusTransaction.objects.filter(
        user=request.user).order_by('-created_at')

    # Передаем транзакции в шаблон
    return render(request, 'bonussystem/bonus.html', {'transactions': transactions})
