from channels.routing import ProtocolTypeRouter, URLRouter
import trivia_runner.routing

application = ProtocolTypeRouter({
    'http': URLRouter(trivia_runner.routing.urlpatterns),
})