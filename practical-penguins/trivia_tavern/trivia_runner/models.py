from __future__ import annotations

import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from trivia_builder.models import TriviaQuiz, TriviaQuestion
from phonenumber_field.modelfields import PhoneNumberField

from twilio_messenger.models import ScoreCard


class Player(models.Model):
    team_name = models.CharField(max_length=24, default='')
    phone_number = PhoneNumberField()
    # Model name needs to be in quotes according to
    # https://docs.djangoproject.com/en/3.0/ref/models/fields/#foreignkey
    active_session = models.ForeignKey('TriviaSession', on_delete=models.CASCADE)

    def get_answers(self):
        answer_set = PlayerAnswer.objects.filter(player=self)
        answers = ""
        for i, answer in enumerate(answer_set, start=1):
            if answer.is_correct():
                answers += f'Question {i}: your answer: {answer.value} is correct\n'
            else:
                answers += f'Question {i}: your answer: {answer.value} ' \
                           f'does not match {answer.question.question_answer}\n'
        return answers

    def __str__(self):
        return f'{self.phone_number} playing {self.active_session.trivia_quiz.name}'


class PlayerAnswer(models.Model):
    value = models.CharField(max_length=500, default='')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(TriviaQuestion, on_delete=models.CASCADE)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE)

    def is_correct(self):
        return self.value.upper() == self.question.question_answer.upper()


def gen_session_code():
    session_code_val = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return session_code_val


class TriviaSession(models.Model):
    trivia_quiz = models.ForeignKey(TriviaQuiz, on_delete=models.CASCADE)
    session_code = models.CharField(max_length=6, unique=True,
                                    default=gen_session_code, editable=False)
    current_question_index = models.IntegerField(default=0)
    session_master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_master')
    start_time = models.DateTimeField(default=timezone.now)
    players = models.ManyToManyField(Player, related_name='quiz_players')

    def __str__(self):
        return (f'Active Quiz:{self.trivia_quiz.name} '
                f'q#:{self.current_question_index} '
                f' players:{self.players.count()}'
                )
