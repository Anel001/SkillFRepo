from django import forms
from django.forms import Textarea
from .models import Notice, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class NoticeForm(forms.ModelForm):
    #content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Notice
        fields = ['Author', 'title', 'content', 'category']
        exclude = ('Author',)


class NoticeEditForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Notice
        fields = ['title', 'content', 'category']


class ComForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['com_text',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['com_text'].widget = Textarea(attrs={'rows': 5})
