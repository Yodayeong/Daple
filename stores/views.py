from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import urllib
import json
from urllib import parse
from urllib import request
from .models import Store
from .forms import StoreForm
from reviews.models import Review, Comment
from reviews.forms import ReviewForm, CommentForm
from django.http import JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
import requests
import json

from accounts.models import User


def index(request):
    data = Store.objects.all()

    context = {
        'stores': data
    }

    if request.method == 'POST':
        jsonObject = json.loads(request.body)
        for i in range(len(jsonObject)):
            if not Store.objects.filter(kakao_id=jsonObject[i]['id']).exists():
                db = Store.objects.create(
                    store_address=jsonObject[i]['address_name'],
                    store_tel=jsonObject[i]['phone'],
                    store_name=jsonObject[i]['place_name'],
                    store_url=jsonObject[i]['place_url'],
                    store_x=jsonObject[i]['x'],
                    store_y=jsonObject[i]['y'],
                    kakao_id=jsonObject[i]['id'])
                db.save()


    return render(request, 'stores/index.html', context)


def detail(request, pk):
    data = Store.objects.get(pk=pk)
    # reviews = data.store_reviews.all()
    # comment = data.comment.all()

    reviews = Review.objects.filter(store_id=pk).order_by('-pk')
    sum_rating = 0
    for review in reviews:
        sum_rating += review.review_rating
    people_num = len(reviews)
    if sum_rating:
        avg_rating = sum_rating / people_num
    else:
        avg_rating = 0
    
    comments = Comment.objects.all().order_by('-pk')
    comment_form = CommentForm()
    context = {
        'store_data': data,
        'reviews': reviews,
        'comment_form': comment_form,
        'comments': comments,
        'avg_rating': avg_rating,
        'people_num': people_num,
        # 'store_star': avg_rating * 10,
    }
    # context ={
    #     'store_data':data,
    #     # 'reviews':reviews,
    #     # 'comment':comment
    # }

    return render(request, 'stores/detail.html', context)


@login_required
def create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            new.user = request.user
            # new.review = request.review
            new.save()
            return redirect('stores:index')
    else:
        form = StoreForm()
    context = {
        'form': form
    }
    return render(request, 'stores/create.html', context)


@login_required
def edit(request, pk):
    data = Store.objects.get(pk=pk)
    if (request.user == data.user) and (data.Is_owner == True):
        if request.method == 'POST':
            store_form = StoreForm(request.POST, request.FILES, instance=data)
            if store_form.is_valid():
                store_form.save()
                return redirect('stores:detail', data.pk)
        else:
            store_form = StoreForm(instance=data)

        context = {
            'store_form': store_form
        }

        return render(request, 'stores/edit.html', context)
    else:

        return redirect("stores:detail", data.pk)


@login_required
def delete(request, pk):
    data = Store.objects.get(pk=pk)
    if (request.user == data.user) and (data.Is_owner == True):
        data.delete()
        return redirect('stores:index')


def kakao_search():
    searching = '합정 스타벅스'
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {
        "Authorization": "KakaoAK 0f23477b2b3262f820c688ff81fdf916"
    }
    places = requests.get(url, headers=headers).json()['documents']
    print(places)


def store_like(request, pk):
    store = get_object_or_404(Store, pk=pk)

    if store.store_liked.filter(id=request.user.id).exists():
        # if request.user in store.store_liked.all():
        store.store_liked.remove(request.user)
        is_liked = False
    else:
        store.store_liked.add(request.user)
        is_liked = True
    context = {'isLiked': is_liked, 'likeCount': store.store_liked.count()}
    return JsonResponse(context)


def db_save(request):

    return redirect('stores:index')
