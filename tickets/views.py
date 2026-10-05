from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.serializers import TicketCreateSerializer
from tickets.services import TicketService


class TicketCreateView(APIView):
    """
    POST /api/v1/tickets/
    Создание тикета.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = TicketService.create_ticket(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        response_serializer = TicketCreateSerializer(ticket)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )