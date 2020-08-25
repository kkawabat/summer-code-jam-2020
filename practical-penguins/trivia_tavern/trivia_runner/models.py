from __future__ import annotations

import random
import string
from typing import List, Tuple

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from trivia_builder.models import TriviaQuiz, TriviaQuestion


def gen_session_code():
    session_code_val = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return session_code_val


class TriviaSession(models.Model):
    trivia_quiz = models.ForeignKey(TriviaQuiz, on_delete=models.CASCADE)
    session_code = models.CharField(max_length=6, unique=True,
                                    default=gen_session_code, editable=False)

    session_master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_master')

    start_time = models.DateTimeField(default=timezone.now)

    current_question_index = models.IntegerField(default=0)

    def __str__(self):
        return f'Active Quiz:{self.trivia_quiz.name} q#:{self.current_question_index} players:{self.scoredeck.count()}'

    def calc_final_tally(self) -> List[Tuple[int, str]]:
        """return a list of final (score, team) tuple in a list, sorted in descending order"""
        final_tally = [(score_card.calc_score(), score_card.player.team_name) for score_card in self.scoredeck]
        final_tally = list(reversed(sorted(final_tally, key=lambda x: x[0])))
        return final_tally

    def add_player_with_number(self, phone_number):
        """create new player and score card for phone number"""
        with transaction.atomic():
            # create score card
            score_card = ScoreCard.objects.create(session=self)
            score_card.save()

            # create player with score card
            player = Player.objects.create(active_session=self, phone_number=phone_number, score_card=score_card)
            player.save()

            # add player to session
            self.players.add(player)
            self.save()
        return player

    def is_name_taken(self, name):
        for card in self.scoredeck:
            if card.player.team_name == name:
                return True
        return False

    def get_current_question(self):
        return self.trivia_quiz.triviaquestion_set.get(question_index=self.current_question_index)


class ScoreCard(models.Model):
    """This model holds a player's answers for a trivia session"""
    session = models.ForeignKey(TriviaSession, on_delete=models.CASCADE, related_name='scoredeck')

    def calc_score(self) -> int:
        return sum([answer.is_correct() for answer in self.scorecardanswer_set])

    def get_result_details(self) -> str:
        answer_set = ScoreCardAnswer.objects.filter(player=self.player)
        question_results = [answer.result_detail() for i, answer in enumerate(answer_set, start=1)]
        return '\n'.join(question_results)

    def answer_question(self, player_response, question):
        with transaction.atomic():
            score_card_answer = ScoreCardAnswer.object.create(value=player_response, question=question, score_card=self)
            score_card_answer.save()
            self.scorecardanswer_set.add(score_card_answer)
            self.save()

    def question_answered(self, question) -> bool:
        return self.scorecardanswer_set.filter(question=question).exists()


class ScoreCardAnswer(models.Model):
    value = models.CharField(max_length=500, default='')
    question = models.ForeignKey(TriviaQuestion, on_delete=models.CASCADE)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE)

    def is_correct(self) -> bool:
        return self.value.upper() == self.question.question_answer.upper()

    def result_detail(self) -> str:
        if self.is_correct():
            result = f'{self.question.question_text}\n' \
                     f'your answer: {self.value} is correct\n'
        else:
            result = f'{self.question.question_text}\n' \
                     f'your answer: {self.value} is incorrect\n' \
                     f'correct answer: {self.question.question_answer}'
        return result


class Player(models.Model):
    score_card = models.OneToOneField(ScoreCard, null=True, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=24, default='')
    phone_number = PhoneNumberField()

    def __str__(self):
        return f'Player {self.team_name}, currently playing {self.score_card.session.trivia_quiz.name}'
