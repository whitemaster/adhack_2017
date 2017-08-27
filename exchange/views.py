# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from exchange.forms import AddTaskForm
from exchange.models import Task, ComplitedTask, ExtUser
import vk
import httplib
import re
import json

def get_user_id(link, vkapi):
    id = link
    if 'vk.com/' in link: #  проверяем эту ссылку
        id = link.split('/')[-1]  # если да, то получаем его последнюю часть
    if not id.replace('id', '').isdigit(): # если в нем после отсечения 'id' сами цифры - это и есть id
        id = vkapi.utils.resolveScreenName(screen_name=id)['object_id'] # если нет, получаем id с помощью метода API
    else:
        id = id.replace('id', '')
    return int(id)


# count это количество запросов (и количество постов = 100 * count постов)
def get_likes(user_id, cnt, vkapi):
    import time
    # подписки пользователя
    subscriptions_list = vkapi.users.getSubscriptions(user_id=user_id,extended=0)['groups']['items']
    # формируем список id, который нужно передать в следующий метод
    groups_list = ['-' + str(x) for x in subscriptions_list]
    posts = {}
    # формируем ленту новостей
    newsfeed = vkapi.newsfeed.get(
        filters='post',
        source_ids=', '.join(groups_list),
        count=100, timeout=10)
    # добавляем посты в словарь в формате id_поста: id_группы
    posts.update({x['post_id']: x['source_id'] for x in newsfeed['items']})
    # нужно для получения следующей партии
    # если требуется более одного запроса — делаем остаток в цикле
    if cnt != 1:
        for c in range(cnt - 1):
            next_from = newsfeed['new_from']
            kwargs = {
                'from': next_from,
                'filters': 'post',
                'source_ids': ', '.join(groups_list),
                'count': 100,
                'timeout': 10
            }
            newsfeed = vkapi.newsfeed.get(**kwargs)

            posts.update({x['post_id']: x['source_id'] for x in newsfeed['items']})
            time.sleep(1)
    liked_posts = []

    print('Лайкнутые посты:')
    for post in posts.items():
        try:
            itemID = post[0]
            ownerID = post[1]
            timeOut = 5
            isLiked = vkapi.likes.isLiked(
                user_id=user_id,
                item_id=itemID,
                type='post',
                owner_id=ownerID,
                timeout=timeOut)
        except Exception:
            isLiked = 0

        if isLiked:
            liked_posts.append('vk.com/wall{0}_{1}'.format(post[1], post[0]))
            print('vk.com/wall{}_{}'.format(post[1], post[0]))
            time.sleep(1)
    return liked_posts


def get_vk(access_token, user_id, post_id, owner_id):
    get_request =  '/method/likes.isLiked?user_id=' + user_id
    get_request+= '&type=post&owner_id=' + owner_id
    get_request+= '&v=5.68&item_id=' + post_id
    get_request+= '&access_token='+ access_token
    local_connect = httplib.HTTPSConnection('api.vk.com', 443)
    local_connect.request('GET', get_request)
    a=local_connect.getresponse().read()
    return a


@login_required
def task_check(request, task_id, ext_user_id):
    # ТК метод будет вызываться из контракта, то должны явно передать юзер_id
    user = ExtUser.objects.get(id=ext_user_id)

    task = Task.objects.get(id=task_id)
    access_token = user.social_auth.get().access_token
    session = vk.Session(access_token=access_token)
    api = vk.API(session)
    user_id = user.social_auth.get().uid
    # Разбираем строку с постом на post_id, и
    link = task.post_link
    ankor = link.find("wall")
    post_id = link[ankor+4:]
    ankor = post_id.find("%2Fall")
    if ankor>0:
        post_id = post_id[:ankor]
    ankor = post_id.find("_")
    owner_id = post_id[:ankor]
    post_id = post_id[ankor+1:]

    is_licked=get_vk(access_token, user_id, post_id, owner_id)
    is_licked = json.loads(is_licked)
    is_licked = is_licked['response']['liked']

    if is_licked:
        # Увеличиваем счётчик выполненных задач
        task.count += 1
        # Если достигли нужного количества выполнний задания, задание завершено
        if task.count >= task.max_count:
            task.status = Task.STATUS_DONE
        task.save()
        # Надо скрыть задание для пользователя навсегда, и дать ему награду
        ct = ComplitedTask(
            user=user,
            task=task
        )
        ct.save()
        user.balans += task.price
        user.save()

    return HttpResponse(is_licked)


@login_required
def add_task(request):
    if request.method == 'POST':
        task_form = AddTaskForm(request.POST)
        task = task_form.save(commit=False)
        if request.user.balans >= task.price*task.max_count:
            task.user = request.user
            task.status = task.STATUS_ACTIVE
            task.save()
            # снимим нужную сумму с баланса юзера
            request.user.balans-= task.price*task.max_count
            request.user.save()
            return redirect('task_list')
        else:
            # не хватило денег
            from django.contrib import messages
            messages.add_message(request, messages.ERROR, 'На вашем счету недостаточно средств для создания такой задачи!')

    else:
        task_form = AddTaskForm()

    return render(request, 'core/add_task.html', {'task_form':task_form, 'link':'add'})


@login_required
def task_list(request):
    tasks = Task.objects.filter(status=Task.STATUS_ACTIVE).exclude(complited__user=request.user).order_by('-create_time')
    return render(request, 'core/task_list.html', {'tasks':tasks, 'link':'list'})