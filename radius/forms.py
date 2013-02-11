# -*- encoding: utf-8 -*-
from django import forms
from nas.models import Nas
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.forms import SplitDateTimeWidget

class SessionFilterForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False) 
    nas = forms.ModelMultipleChoiceField(label=u"Сервер доступа субаккаунта", queryset=Nas.objects.all(), required=False)
    id = forms.IntegerField(required=False)
    date_start = forms.DateTimeField(label = u'С даты', required=False, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label = u'По дату', required=False, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    only_active = forms.BooleanField(label = u'Только активные', widget = forms.widgets.CheckboxInput, required=False)