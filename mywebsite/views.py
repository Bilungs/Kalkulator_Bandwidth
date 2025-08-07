from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import BandwidthForm
from routeros_api import RouterOsApiPool
import subprocess
import json
from .forms import QueueConfigForm
from .models import QueueConfig
import paramiko

# Dictionary kebutuhan bandwidth per aplikasi
BW_PER_APP = {
    "Zoom": 2,
    "Google Meet": 2,
    "Microsoft Teams": 1,
    "Mobile Legend": 2,
    "PUBG Mobile": 0.0425,
    "Free Fire": 0.0636,
    "WhatsApp": 0.060,
    "LINE": 0.063,
    "WeChat": 0.0641,
    "Instagram": 2,
    "TikTok": 2.2,
    "Facebook": 3.1,
    "YouTube 360p": 5.7,
    "YouTube 480p": 14,
    "YouTube 720p60": 30,
    "YouTube 1080p60": 40,
    "YouTube 4K": 80,
    "Bstation": 9.2,
    "Blibli TV": 7.1,
    "Twitch": 2.1,
    "OBS": 3.58,
    "Prims Live Studio": 2.1,
    "ChatGPT": 0.459,
    "Gemini": 0.100,
    "Meta AI": 0.869,
    "DeepSeek": 0.00503,
    "Black Box": 0.600,
    "Roblox" : 0.146484375,
}

# View halaman index
def index(request):
    return render(request, 'index.html')

# View kalkulator bandwidth
def kalkulator_view(request):
    hasil = {}
    total = 0
    if request.method == 'POST':
        form = BandwidthForm(request.POST)
        if form.is_valid():
            apps = form.cleaned_data['aplikasi']
            jumlah = form.cleaned_data['jumlah_perangkat']
            for app in apps:
                bw = BW_PER_APP.get(app, 1)
                total_app = bw * jumlah
                total_app += 0.1 * total_app  # Tambah 10% overhead
                hasil[app] = round(total_app, 2)
            total = round(sum(hasil.values()), 2)
    else:
        form = BandwidthForm()
    return render(request, 'kalkulator.html', {
        'form': form,
        'hasil': hasil,
        'total': total
    })

# Ping ke IP MikroTik
def ping_mikrotik(ip_address):
    try:
        output = subprocess.check_output(['ping', '-n', '1', ip_address], universal_newlines=True)
        return "TTL=" in output
    except subprocess.CalledProcessError:
        return False

# Fungsi bantu: setting queue ke MikroTik
def set_queue_routeros(ip_address, username, password, name, target, max_limit):
    api_pool = RouterOsApiPool(
        host=ip_address,
        username=username,
        password=password,
        port=8728,
        plaintext_login=True
    )
    api = api_pool.get_api()
    queue = api.get_resource('/queue/simple')

    # Hapus queue lama jika ada
    existing = queue.get(name=name)
    for q in existing:
        queue.remove(id=q['id'])

    # Tambah queue baru
    queue.add(
        name=name,
        target=target,
        max_limit=f"{max_limit}M/{max_limit}M"
    )
    api_pool.disconnect()

# Endpoint API untuk menerima request dari JavaScript
@csrf_exempt
def set_queue(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Ambil data dari POST JSON
        ip_mikrotik = "192.168.88.1"  # IP MikroTik
        username = "admin"
        password = "admin123"
        queue_name = data.get("queue_name")
        target_ip = data.get("ip_address")
        max_limit = f'{data.get("bandwidth")}M/{data.get("bandwidth")}M'

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip_mikrotik, username=username, password=password)

            # Cek apakah queue dengan nama tersebut sudah ada
            check_cmd = f'/queue simple print where name="{queue_name}"'
            stdin, stdout, stderr = ssh.exec_command(check_cmd)
            output = stdout.read().decode()

            if queue_name in output:
                ssh.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'Queue "{queue_name}" sudah ada di MikroTik.'
                }, status=400)

            # Jika tidak ada, tambahkan queue
            add_cmd = f'/queue simple add name="{queue_name}" target={target_ip} max-limit={max_limit}'
            stdin, stdout, stderr = ssh.exec_command(add_cmd)
            result = stdout.read().decode()
            error = stderr.read().decode()
            ssh.close()

            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=500)
            return JsonResponse({'status': 'success', 'message': result})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'failed', 'message': 'Invalid request'}, status=400)

def queue_config_view(request):
    if request.method == 'POST':
        form = QueueConfigForm(request.POST)
        if form.is_valid():
            queue = form.save()  # simpan ke database

            # Kirim ke MikroTik via Paramiko
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(queue.ip_address, username=queue.username, password=queue.password)

                cmd = f'/queue simple add name={queue.queue_name} target={queue.target} max-limit={queue.max_limit}'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read().decode()
                error = stderr.read().decode()
                ssh.close()

                if error:
                    return render(request, 'config_result.html', {
                        'success': False,
                        'message': error
                    })
                return render(request, 'config_result.html', {
                    'success': True,
                    'message': 'Konfigurasi berhasil dikirim ke MikroTik.'
                })

            except Exception as e:
                return render(request, 'config_result.html', {
                    'success': False,
                    'message': str(e)
                })
    else:
        form = QueueConfigForm()

    return render(request, 'queue_config.html', {'form': form})