from django.shortcuts import render, redirect
from generator.models import quote
from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache
from datetime import datetime, timedelta
import requests
import random
import os
import json
# Create your views here.


def save_json(request):
    url = "https://dummyjson.com/quotes"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data['quotes']:  # Access the 'quotes' list in the JSON response
            quotes_instance = quote(
                author=item['author'],
                content=item['quote'],
            )
            quotes_instance.save()  # Save the instance to the database

        return HttpResponse('Quotes fetched and saved successfully')
    else:
        return HttpResponse(f'Failed to fetch quotes, status code: {response.status_code}')


def set_quote_of_the_day():
    # Get current date and time
    now = datetime.now()

    # Calculate seconds until the end of the current day
    seconds_until_midnight = (24*60*60) - (now.hour*60*60 + now.minute*60 + now.second)

    # Fetch a new random quote
    random_quote = quote.objects.order_by('?').first()

    # Set cache timeout to seconds until midnight
    cache.set('quote_of_the_day', random_quote, timeout=seconds_until_midnight)

def get_quote_of_the_day():
    # Retrieve the quote of the day from the cache
    quote_of_the_day = cache.get('quote_of_the_day')

    if not quote_of_the_day:
        # If not cached or expired, fetch a new quote and set it for the day
        set_quote_of_the_day()
        quote_of_the_day = cache.get('quote_of_the_day')

    return quote_of_the_day

def index(request):
    # Check if the quote is already cached
    quote_of_the_day = get_quote_of_the_day()
    
    if not quote_of_the_day:
        # If not cached, fetch a new random quote
        random_quote = quote.objects.order_by('?').first()
        # Cache it for 24 hours
        cache.set('quote_of_the_day', random_quote, timeout=60*60*24)
        quote_of_the_day = random_quote
    
    return render(request, 'index.html', {
        'author': quote_of_the_day.author,
        'quote': quote_of_the_day.content,
    })


def search(request):
    quote_of_the_day = get_quote_of_the_day()
    if request.method == "POST":
        search = request.POST.get('name')
        if search:
            name = search.title()
            quotes_found = quote.objects.filter(author=name)
            if quotes_found.exists():
                chosen_quote = random.choice(quotes_found)
                return render(request, 'index.html', {'author': chosen_quote.author, 'quote': chosen_quote.content, 'results': True})
            else:
            	error="Author not found"
            	return render(request, 'index.html', {'err':error,'author':quote_of_the_day.author,'quote':quote_of_the_day.content})
        else:
            err2="Please enter author name"
            return render(request, 'index.html',{'err2':err2,'author':quote_of_the_day.author,'quote':quote_of_the_day.content})
    else:
        return render(request, 'index.html',{'author':quote_of_the_day.author,'quote':quote_of_the_day.content})






