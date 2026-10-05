from django.urls import path

from tickets.views import TicketCreateView

urlpatterns = [
    path("", TicketCreateView.as_view(), name="ticket-create"),
]