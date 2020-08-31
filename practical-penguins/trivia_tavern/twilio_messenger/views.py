from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from phonenumber_field.phonenumber import PhoneNumber

from trivia_runner.models import TriviaSession, Player


class SMSBot:
    """SMSBot is a helper class to implement the main receving 'sms_reply'
    functions and process the input received from texts
    @send: send a string 'msg' to a phone number 'recipient'
    @register: register a new player with a 'phone_number' for requested 'active_session'
    """

    @staticmethod
    def send(msg: str, recipient: PhoneNumber):
        """send will send a message 'msg' to a 'recipient'
        This is not really a view method, but a helper method for the main
        sms_reply method
        """
        twilio_number = settings.HOST_TWILIO_NUMBER
        client = settings.TWILIO_CLIENT
        message = client.messages.create(
            body=msg,
            from_=twilio_number,
            to=recipient.as_international
        )
        return message

    @staticmethod
    def register_player_to_session(number, active_session, invited=True):
        active_session.add_player_with_number(number)

        if invited:
            welcome = (f'Hello! You\'ve been invited to play trivia by {active_session.session_master.username}. '
                       f'If you\'re not expecting this, just text back !quit and we won\'t bother you anymore!'
                       f'Otherwise, please text back a team name to join')
        else:
            welcome = (f'You registered to play "{active_session.trivia_quiz.name}." '
                       f'Please choose a team name to join'
                       f'If you didn\'t mean to do this, text !quit at any time')

        SMSBot.send(welcome, number)

    @staticmethod
    def set_team_name(team_name, player):
        team_name = team_name.strip()
        if player.score_card.session.is_name_taken(team_name):
            msg = f"team {team_name} already exists, please choose another name"

        else:

            if player.team_name == '':
                msg = f'Your team name is now "{team_name}" please wait for session to begin'
            else:
                msg = f'Your team has been updated! You are now on team "{team_name}"'

            player.team_name = team_name
            player.save()

        SMSBot.send(msg, player.phone_number)

    @staticmethod
    def remove_player_from_session(player):
        session_master = player.score_card.session.session_master
        SMSBot.send(f'You have quit {session_master.username}\'s game', player.phone_number)
        player.score_card.delete()

    @staticmethod
    def pre_quiz(body, player):
        if body.split('/')[0].upper() == '!EDIT':
            new_team_name = body.split('/')[1]
            SMSBot.set_team_name(new_team_name, player)
        else:
            please_wait = ('The host hasn\'t started the quiz yet, patience is a virtue! '
                           'If you want to change teams, text !EDIT/newteamname before the quiz starts.')
            SMSBot.send(please_wait, player.phone_number)

    @staticmethod
    def evaluate_answer(body, player):
        trivia_session = player.score_card.session
        current_question = trivia_session.get_current_question()

        if player.score_card.question_answered(current_question):
            return SMSBot.send('You already submitted your answer!', player.phone_number)
        else:
            player.score_card.answer_question(body, current_question)
            return SMSBot.send('Answer received! Please wait for the next question...', player.phone_number)

    @staticmethod
    def question_timeout(trivia_session):
        current_question = trivia_session.get_current_question()

        for card in trivia_session.scoredeck.all():
            # answer blank for current question if they have not answered yet
            if not card.question_answered(current_question):
                card.answer_question("", current_question)
                SMSBot.send("times up, you answered blank for this question", card.player.phone_number)

    @staticmethod
    def send_question_to_players(trivia_session):
        current_question = trivia_session.get_current_question()

        for card in trivia_session.scoredeck.all():
            SMSBot.send(str(current_question), card.player.phone_number)

    @staticmethod
    def announce_result(trivia_session, winner):
        # send result of the session and delete the card/player
        for card in trivia_session.scoredeck.all():
            goodbye = (f'The session has ended, thanks for playing!\n'
                       f'Team {winner} was the winner!\n'
                       f'Your score was: {card.calc_score()}/{trivia_session.trivia_quiz.get_question_count}')

            SMSBot.send(goodbye, card.player.phone_number)
            SMSBot.send(card.get_result_details(), card.player.phone_number)
            card.delete()


@csrf_exempt
def sms_reply(request):
    """sms_reply is a handler method that triggers when the url 'sms' is
    navigated to. Your Twilio account should be configured to point to:
    <this-site>/sms so that those texts will be recieved here and processed
    by this function. You can think of this like a 'main' method

    For testing purposes, the developer recommends ngrok to host a temporary
    server and domain name that points to your localhost
    (for example http://a2b0fd3c60b6.ngrok.io) and set your
    twilio account settings in Phone Numbers > Manage Numbers > Active numbers
    under "Messaging" and set a webhook to <url>/sms/ BUT do not forget the
    trailing slash!
    """

    # Get details about the message that just came in
    phone_number = request.POST.get('From', None)
    body = request.POST.get('Body', None)

    # get player with phone_number
    try:
        player = Player.objects.get(phone_number=phone_number)
    # if number is not recognized check to see if number is session code
    except Player.DoesNotExist:
        session_code = body.strip().upper()
        try:
            session = TriviaSession.object.get(session_code=session_code)
            SMSBot.register_player_to_session(phone_number, session)
        except TriviaSession.DoesNotExist:
            msg = (f'This number is not linked to any running trivia session and {body} is not recognized as a valid '
                   f'session code. Please send a valid session code to start quiz')
            SMSBot.send(msg, phone_number)
        return redirect('/')

    if body.upper() == '!QUIT':
        SMSBot.remove_player_from_session(player)
    elif player.team_name == '':
        SMSBot.set_team_name(body, player)
    elif player.score_card.session.current_question_index == 0:
        SMSBot.pre_quiz(body, player)
    else:
        SMSBot.evaluate_answer(body, player)

    # no page to display, sorry :(, redirect to home
    return redirect('/')
