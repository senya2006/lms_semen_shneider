from collections import defaultdict
import functools
import requests
import os
import psutil


# Decorator for caching with the LFU algorithm
def cache(max_limit=64):
    def internal(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            cache_key = (args, tuple(kwargs.items()))

            if cache_key in deco._cache:
                # Increasing frequency of use
                deco._usage_freq[cache_key] += 1
                return deco._cache[cache_key]

            result = f(*args, **kwargs)

            if len(deco._cache) >= max_limit:
                # Finding the key with the lowest frequency of use
                lfu_key = min(deco._usage_freq, key=deco._usage_freq.get)
                # Remove it from the cache and from the usage counter
                del deco._cache[lfu_key]
                del deco._usage_freq[lfu_key]

            # Save the result to cache and set the frequency of use to 1
            deco._cache[cache_key] = result
            deco._usage_freq[cache_key] = 1

            return result

        deco._cache = {}
        deco._usage_freq = defaultdict(int)
        return deco

    return internal


# Decorator for memory metering
def profile_memory(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        result = f(*args, **kwargs)
        mem_after = process.memory_info().rss
        print(f"Memory usage: {((mem_after - mem_before) / 1024):.2f} KB")
        return result

    return wrapper


# Function using decorators
@profile_memory
@cache(max_limit=5)
def fetch_url(url, first_n=100):
    """Fetch a given url"""
    res = requests.get(url)
    return res.content[:first_n] if first_n else res.content


# Examples
fetch_url('https://google.com')
fetch_url('https://google.com')
fetch_url('https://ithillel.ua')
fetch_url('https://github.com/')
fetch_url('https://mail.google.com/')
fetch_url('https://youtube.com')
fetch_url('https://google.com/maps')
