from django import forms
from .models import QueueConfig

class BandwidthForm(forms.Form):
    APLIKASI_CHOICES = [
        ("Zoom", "Zoom"),
        ("Google Meet", "Google Meet"),
        ("Microsoft Teams", "Microsoft Teams"),
        ("WhatsApp", "WhatsApp"),
        ("LINE", "LINE"),   
        ("WeChat", "WeChat"), 
        ("Instagram", "Instagram"),
        ("TikTok", "TikTok"),
        ("Facebook", "Facebook"),
        ("YouTube 360p", "YouTube 360p"),
        ("YouTube 480p", "YouTube 480p"),
        ("YouTube 720p60", "YouTube 720p60"),
        ("YouTube 1080p60", "YouTube 1080p60"),
        ("YouTube 4K", "YouTube 4K"),
        ("Bstation", "Bstation"),
        ("Blibli TV", "Blibli TV"),
        ("Netflix", "Netflix"),
        ("Twitch", "Twitch"),
        ("OBS", "OBS"),
        ("Prims Live Studio", "Prims Live Studio"),
        ("ChatGPT", "ChatGPT"),
        ("Gemini", "Gemini"),
        ("Meta AI", "Meta AI"),
        ("DeepSeek", "DeepSeek"),
        ("Black Box", "Black Box"),
        ("Mobile Legend", "Mobile Legend"),
        ("PUBG Mobile", "PUBG Mobile"),
        ("Free Fire", "Free Fire"),
        ("Roblox", "Roblox"),
    ]

    aplikasi = forms.MultipleChoiceField(
        choices=APLIKASI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Pilih Aplikasi yang Digunakan"
    )
    jumlah_perangkat = forms.IntegerField(min_value=1, label="Jumlah Perangkat")


    jumlah_perangkat = forms.IntegerField(
    min_value=1,
    label="Jumlah Perangkat",
    widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Masukkan jumlah perangkat yang digunakan'
    }))

class QueueConfigForm(forms.ModelForm):
    class Meta:
        model = QueueConfig
        fields = ['ip_address', 'username', 'password', 'queue_name', 'target', 'max_limit']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }