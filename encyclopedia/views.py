from django.shortcuts import render
from . import util
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import random
import markdown2


class NewTopicForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(widget=forms.Textarea, label="Content")


class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="Content")


def index(request):
    list_of_items = []
    query = request.GET.get('q')
    if query:
        topic = util.get_entry(query)
        if topic:
            return render(request, "encyclopedia/entry.html", {
                "entry": topic,
                "title": query
            })
        else:
            for item in util.list_entries():
                if query.lower() in item.lower():
                    list_of_items.append(item)
            return render(request, "encyclopedia/search.html", {
                "list_of_items": list_of_items,
            })
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def title(request, title):
    entry = util.get_entry(title)
    if entry:
        entry_html = markdown2.markdown(entry)
        return render(request, "encyclopedia/entry.html", {
            "entry": entry_html,
            "title": title
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })


def create(request):
    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(topic):
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "error_message": "A topic with this title already exists."
                })
            util.save_entry(topic, content)
            return HttpResponseRedirect(reverse("encyclopedia:index"))
    else:
        form = NewTopicForm()
    return render(request, "encyclopedia/create.html", {
        "form": form
    })


def edit(request, title):
    data = util.get_entry(title)
    form = EditForm(initial={'content': data})

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:title", args=[title]))

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


def random_entry(request):
    entries = util.list_entries()
    entry = random.choice(entries)
    if entry:
        return render(request, "encyclopedia/random.html", {
            "entry": entry,
            "title": entry
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
