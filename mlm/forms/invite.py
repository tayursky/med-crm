from django import forms

from identity.models import Account


class InviteForm(forms.ModelForm):
    widgets = None

    phone = forms.CharField(
        label='Недостающие цифры +',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label='Придумайте пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['phone'].label += '%s****' % self.instance.person.get_phone()[:-4]

    def clean_phone(self):
        data = self.cleaned_data['phone']
        if data != self.instance.person.get_phone()[-4:]:
            raise forms.ValidationError('Неверные цифры')
        return data

    def clean_password2(self):
        if self.cleaned_data['password'] == self.instance.person.get_phone():
            raise forms.ValidationError('Пароль не должен совпадать с номером телефона')
        if len(self.cleaned_data['password']) < 5:
            raise forms.ValidationError('Пароль не меньше 5 символов')
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('Пароли должны совпадать')
        return self.cleaned_data['password']

    def save(self, *args, **kwargs):
        account = self.instance.person.account
        if not account:
            try:
                account = Account.objects.get(username=self.instance.person.get_phone())
            except Account.DoesNotExist:
                account = Account.objects.create_user(
                    self.instance.person.get_phone(), '', self.cleaned_data['password']
                )
        self.instance.person.account = account
        self.instance.person.account.set_password(self.cleaned_data['password'])
        self.instance.person.account.save()
        self.instance.token = None
        self.instance.person.save()
        return super().save(commit=True)
