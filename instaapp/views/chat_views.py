from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from instaapp.models.chatroom import ChatRoom, Message
from instaapp.models.user import CustomUser
from instaapp.serializers import ChatRoomSerializer, MessageSerializer, UserSerializer

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.chatrooms.all()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_chatroom(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=400)

        try:
            other_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        # Check if chat room already exists
        chatroom = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()
        if chatroom:
            return Response({'chatroom_id': chatroom.id}, status=200)

        # Create new chat room
        chatroom = ChatRoom.objects.create()
        chatroom.participants.add(request.user, other_user)
        chatroom.save()
        return Response({'chatroom_id': chatroom.id}, status=201)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def messages(self, request, pk=None):
        chatroom = self.get_object()
        messages = chatroom.messages.order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request, pk=None):
        chatroom = self.get_object()
        content = request.data.get('content')
        receiver_id = request.data.get('receiver_id')
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=404)

        if content:
            message = Message.objects.create(chatroom=chatroom, sender=request.user, receiver=receiver, content=content)
            serializer = MessageSerializer(message)
            return Response(serializer.data)
        return Response({'error': 'Message content is required'}, status=400)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_chatrooms(self, request):
        user = request.user
        chatrooms = ChatRoom.objects.filter(participants=user)
        data = []
        for chatroom in chatrooms:
            other_users = chatroom.participants.exclude(id=user.id)
            for other_user in other_users:
                data.append({
                    'chatroom_id': chatroom.id,
                    'user': UserSerializer(other_user).data,
                })
        return Response(data)
