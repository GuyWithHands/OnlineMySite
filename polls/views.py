from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question, Response
from django.contrib.auth.decorators import login_required

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

@login_required
def index(request):
    unvoted_question_list = []
    voted_question_list = []
    for q in Question.objects.all():
        if Response.objects.filter(question=q, user=request.user).exists():
            voted_question_list.append(q)
        else:
            unvoted_question_list.append(q)
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"unvoted_question_list": unvoted_question_list, "voted_question_list": voted_question_list}
    return render(request, "polls/index.html", context)

@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not Response.objects.filter(question=question, user=request.user).exists():
        return HttpResponseRedirect(reverse("polls:detail", args=(question.id,)))
    return render(request, "polls/results.html", {"question": question, "response": Response.objects.filter(question=question, user=request.user).first()})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        if (not Response.objects.filter(user=request.user, question=question).exists()):
            selected_response = Response(user=request.user, question=question, choice=selected_choice)
            selected_choice.votes += 1
            selected_choice.save()
            selected_response.save()
        else:
            return render(
                request,
                "polls/detail.html",
                {
                    "question": question,
                    "error_message": "You already voted you numbskull.",
                },
            )
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))