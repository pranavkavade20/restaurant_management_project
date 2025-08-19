from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields =["comment"]
        widgets = {
            "comment" : forms.Textarea(attrs={
                "rows":5,
                "placeholder":"Share your thoughts about our food or service.",
                "class":"w-full px-4 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#e23744]"
            })
        }
        labels ={"comment":"Your Feedback"}