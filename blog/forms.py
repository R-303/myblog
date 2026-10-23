from django import forms
from .models import Comment

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