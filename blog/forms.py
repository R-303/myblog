from django import forms
from .models import Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=["nickname","email","body"]
        widgets={
            "nickname":forms.TextInput(
                attrs={"placeholder":"昵称"}
            ),
            "email":forms.EmailInput(
                attrs={"placeholder":"邮箱"}
            ),
            "body":forms.Textarea(
                attrs={
                    "placeholder":"写下你的看法",
                    "rows":4,
                }
            ),
        }

User=get_user_model()

class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model=User
        fields=["username","email"]
# UserCreationForm 自带 password1、password2 和密码校验，不用自己写密码哈希。