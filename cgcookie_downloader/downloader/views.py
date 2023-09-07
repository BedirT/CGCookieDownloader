from django.shortcuts import render
from django.http import JsonResponse
from .utils import download_course

def check_login(request):
    # Use Selenium to check if the user is logged in
    logged_in = check_user_logged_in()  # Implement this function based on your Selenium logic
    return JsonResponse({'logged_in': logged_in})

def index(request):
    browser_opened = False
    message = ""
    if request.method == 'POST':
        course_url = request.POST.get('course_url')
        save_path = request.POST.get('save_path')
        prefix_option = request.POST.get('prefix_option') == 'on'
        skip_if_exists = request.POST.get('skip_if_exists') == 'on'
        success, message = download_course(course_url, save_path, prefix_option, skip_if_exists)
        if not success:
            # If there's an issue (e.g., login wasn't detected), display an error message
            message = "There was an issue with the download. Please ensure you're logged in and try again."
        browser_opened = True
        
    return render(request, 'index.html', {'message': message, 'browser_opened': browser_opened})
