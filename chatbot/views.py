from django.shortcuts import render

def chat_view(request):
    return render(request, 'chatbot/chat_widget.html')
