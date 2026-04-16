from django import forms
from .models import ChatGroup, User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'phone_no', 'profile_pic', 'about', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone_no': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'profile_pic': forms.ClearableFileInput(),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.ModelForm):
    # Define the widget and its attributes right here
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Group Name', 'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'phone_no', 'profile_pic', 'about']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone_no': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'profile_pic': forms.ClearableFileInput(),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }