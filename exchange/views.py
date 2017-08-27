# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from exchange.forms import AddTaskForm
from exchange.models import Task, ComplitedTask, ExtUser
import vk
import httplib
import re
import json
from ethjsonrpc import EthJsonRpc
from django.conf import settings


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



def get_eth(key_from, task_price):
    # Тут стучимся в эфир
    compiled = u"0x6060604052341561000f57600080fd5b5b61099c8061001f6000396000f30060606040523615610076576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063095ea7b31461007b57806318160ddd146100d557806323b872dd146100fe57806370a0823114610177578063a9059cbb146101c4578063dd62ed3e1461021e575b600080fd5b341561008657600080fd5b6100bb600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803590602001909190505061028a565b604051808215151515815260200191505060405180910390f35b34156100e057600080fd5b6100e8610412565b6040518082815260200191505060405180910390f35b341561010957600080fd5b61015d600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610418565b604051808215151515815260200191505060405180910390f35b341561018257600080fd5b6101ae600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506106c9565b6040518082815260200191505060405180910390f35b34156101cf57600080fd5b610204600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610713565b604051808215151515815260200191505060405180910390f35b341561022957600080fd5b610274600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506108af565b6040518082815260200191505060405180910390f35b60008082148061031657506000600260003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054145b151561032157600080fd5b81600260003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a3600190505b92915050565b60005481565b600080600260008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490506104ec83600160008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461093790919063ffffffff16565b600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000208190555061058183600160008873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461095690919063ffffffff16565b600160008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055506105d7838261095690919063ffffffff16565b600260008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508373ffffffffffffffffffffffffffffffffffffffff168573ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef856040518082815260200191505060405180910390a3600191505b509392505050565b6000600160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b919050565b600061076782600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461095690919063ffffffff16565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055506107fc82600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461093790919063ffffffff16565b600160008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190505b92915050565b6000600260008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490505b92915050565b600080828401905083811015151561094b57fe5b8091505b5092915050565b600082821115151561096457fe5b81830390505b929150505600a165627a7a72305820555bd5fd700426621f595ca4d327cb2441e425da32bc02af1980faedabc29e880029"
    c = EthJsonRpc('127.0.0.1', 8545)
    c.net_version()
    # continued from above
    contract_tx = c.create_contract(settings.GENERAL_KEY, compiled, gas=300000)
    contract_addr = c.get_contract_address(contract_tx)
    value = task_price/(10**18)
    tx = c.call_with_transaction(settings.GENERAL_KEY, contract_addr, 'transferFrom({0}, {1}, {2})'.format( settings.GENERAL_KEY, key_from, value), ['Hello, world'])
    return tx


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
            if get_eth(task.user, task.price):
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