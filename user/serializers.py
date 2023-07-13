from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from group.serializers import UserSerializer
from .models import Profile
from rest_framework.response import Response

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

          # return Response({"token":token})
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        try:

          prof = Profile.objects.get(email = self.user)
          serializer = UserSerializer(prof,many = False)
          data["data"] = serializer.data
        except:
          pass
        return data 