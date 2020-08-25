from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, ListView
from django.contrib import messages

from trivia_builder.models import TriviaQuestion
from trivia_runner.models import TriviaSession
from twilio_messenger.views import SMSBot

from .forms import PhoneNumberForm


class ActiveTriviaSessionListView(ListView):
    model = TriviaSession
    template_name = 'session-list.html'
    context_object_name = 'active_sessions'
    ordering = ['-start_time']
    paginate_by = 10


def setup(request, trivia_session):
    if 'phone_number' in request.POST:
        phonenumber_form = PhoneNumberForm(request.POST)
        if phonenumber_form.is_valid():
            # Add a new player instance to session, then clear form
            player = phonenumber_form.save(commit=False)
            player.active_session = trivia_session
            player.save()
            messages.success(request, f'Invite sent to {player.phone_number}!')
            SMSBot.register_player_to_session(player, trivia_session, invited=True)
            phonenumber_form = PhoneNumberForm()
    else:
        phonenumber_form = PhoneNumberForm()

    return render(request, 'session-setup-page.html', {'trivia_session': trivia_session, 'form': phonenumber_form})


def times_up(request, trivia_session):
    SMSBot.question_timeout(trivia_session)
    cur_question = TriviaQuestion.objects.get(quiz=trivia_session.trivia_quiz,
                                              question_index=trivia_session.current_question_index)
    return render(request, 'session-question-page.html',
                  {'trivia_session': trivia_session, 'cur_question': cur_question})


def question(request, trivia_session):
    SMSBot.send_question_to_players(trivia_session)
    cur_question = TriviaQuestion.objects.get(quiz=trivia_session.trivia_quiz,
                                              question_index=trivia_session.current_question_index)
    return render(request, 'session-question-page.html',
                  {'trivia_session': trivia_session, 'cur_question': cur_question})


def end_screen(request, trivia_session):
    tally = trivia_session.calc_final_tally()
    winner = tally[0][0] if len(tally) != 0 else "No one participated :("

    tally_results = {'winner': winner, 'tally': tally}

    SMSBot.announce_result(trivia_session, winner)
    return render(request, 'session-end-page.html',
                  {'trivia_session': trivia_session, 'tally_results': tally_results})


@csrf_exempt
def active_trivia(request, pk):
    trivia_session = get_object_or_404(TriviaSession, pk=pk)

    if request.method == 'POST':
        if 'next-question' in request.POST:
            trivia_session.current_question_index = trivia_session.current_question_index + 1
        elif 'show-results' in request.POST:
            trivia_session.current_question_index = -1
        elif 'times-up' in request.POST:
            return times_up(request, trivia_session)

    if trivia_session.current_question_index == 0:
        response = setup(request, trivia_session)
    elif trivia_session.current_question_index > 0:
        response = question(request, trivia_session)
    elif trivia_session.current_question_index < 0:
        response = end_screen(request, trivia_session)
    else:
        return HttpResponseNotFound(f"trivia_session current_question_index "
                                    f"invalid value {trivia_session.current_question_index}")
    trivia_session.save()
    return response


class TriviaQuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TriviaSession
    success_url = '/quiz'

    def test_func(self):
        trivia_session = self.get_object()
        if self.request.user == trivia_session.session_master:
            return True
        return False
