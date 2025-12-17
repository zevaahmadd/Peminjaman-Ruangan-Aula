from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout
from django.http import HttpResponseForbidden

from .models import Peminjaman, Ruangan
from .forms import PeminjamanForm, RegisterForm

# ----------------------
# helper: refresh status
# ----------------------
def refresh_expired_to_selesai():
    """
    Tandai otomatis peminjaman yang tadinya DISETUJUI tapi waktu selesai-nya sudah lewat
    menjadi SELESAI. Dipanggil di view yang sering diakses (home, jadwal, riwayat, admin).
    """
    now = timezone.now()
    Peminjaman.objects.filter(status='DISETUJUI', tanggal_selesai__lt=now).update(status='SELESAI')

# -------------------------
# helper: tandai event sudah selesai
# -------------------------
def mark_finished():
    """
    Tandai peminjaman yg tadinya DISETUJUI tapi waktunya sudah lewat -> jadi SELESAI
    Dipanggil sebelum query agar halaman selalu up-to-date.
    """
    now = timezone.now()
    Peminjaman.objects.filter(status='DISETUJUI', tanggal_selesai__lt=now).update(status='SELESAI')

def home(request):
    # update status dulu
    mark_finished()

    # ambil 5 jadwal terdekat yang sudah disetujui (masih berlaku)
    upcoming = Peminjaman.objects.filter(
        status='DISETUJUI',
        tanggal_selesai__gte=timezone.now()
    ).order_by('tanggal_mulai')[:5]

    return render(request, 'peminjaman/home.html', {'upcoming': upcoming})

def jadwal(request):
    peminjaman = Peminjaman.objects.filter(status='DISETUJUI').order_by('tanggal_mulai')
    return render(request, 'peminjaman/jadwal.html', {'peminjaman': peminjaman})

@login_required
def ajukan_peminjaman(request):
    if request.method == 'POST':
        form = PeminjamanForm(request.POST)
        if form.is_valid():
            peminjaman = form.save(commit=False)
            peminjaman.peminjam = request.user

            # cek bentrok jadwal (hanya yang sudah disetujui menghalangi)
            bentrok = Peminjaman.objects.filter(
                ruangan=peminjaman.ruangan,
                status='DISETUJUI',
                tanggal_mulai__lt=peminjaman.tanggal_selesai,
                tanggal_selesai__gt=peminjaman.tanggal_mulai,
            ).exists()

            if bentrok:
                messages.error(request, 'Jadwal tersebut sudah terpakai. Silakan pilih waktu lain.')
            else:
                peminjaman.save()
                messages.success(request, 'Pengajuan peminjaman berhasil dikirim. Menunggu verifikasi admin.')
                return redirect('riwayat')
        else:
            # debugging singkat: hapus nanti
            print(form.errors)
    else:
        form = PeminjamanForm()

    return render(request, 'peminjaman/ajukan.html', {'form': form})

@login_required
def riwayat(request):
    # update status dulu
    mark_finished()

    if request.user.is_staff:
        # admin lihat semua pengajuan
        peminjaman = Peminjaman.objects.all().order_by('-dibuat_pada')
    else:
        # user biasa hanya lihat punyanya sendiri
        peminjaman = Peminjaman.objects.filter(peminjam=request.user).order_by('-dibuat_pada')

    return render(request, 'peminjaman/riwayat.html', {'peminjaman': peminjaman})

def is_admin(user):
    return user.is_staff

@user_passes_test(lambda u: u.is_staff)
def pengajuan_admin(request):
    # update status dulu
    mark_finished()

    status_filter = request.GET.get('status')
    peminjaman = Peminjaman.objects.all().order_by('-dibuat_pada')
    if status_filter:
        peminjaman = peminjaman.filter(status=status_filter)

    return render(request, 'peminjaman/pengajuan_admin.html', {'peminjaman': peminjaman})


@user_passes_test(lambda u: u.is_staff)
def proses_pengajuan(request, pk):
    pem = get_object_or_404(Peminjaman, pk=pk)

    if request.method == 'POST':
        aksi = request.POST.get('aksi')
        catatan = request.POST.get('catatan_admin', '')
        pem.catatan_admin = catatan

        if aksi == 'setujui':
            pem.status = 'DISETUJUI'
            pem.minta_batal = False
        elif aksi == 'tolak':
            pem.status = 'DITOLAK'
            pem.minta_batal = False
        elif aksi == 'setujui_batal' or aksi == 'setujui_pembatalan':
            # admin menyetujui permintaan pembatalan user
            pem.status = 'DIBATALKAN'
            pem.minta_batal = False
        elif aksi == 'tolak_batal' or aksi == 'tolak_pembatalan':
            # admin menolak permintaan pembatalan; kembalikan ke DISETUJUI
            pem.minta_batal = False
            pem.status = 'DISETUJUI'
        # tambahkan elif jika butuh aksi lain

        pem.save()
        messages.success(request, 'Pengajuan berhasil diproses.')
        return redirect('pengajuan_admin')

    return render(request, 'peminjaman/proses_pengajuan.html', {'peminjaman': pem})

@login_required
def hapus_peminjaman(request, pk):
    pem = get_object_or_404(Peminjaman, pk=pk)

    # hanya pemilik atau admin yang boleh
    if not (request.user.is_staff or pem.peminjam == request.user):
        messages.error(request, 'Anda tidak boleh menghapus pengajuan ini.')
        return redirect('riwayat')

    # user biasa hanya boleh hapus yang MENUNGGU atau DITOLAK
    if (not request.user.is_staff) and pem.status not in ['MENUNGGU', 'DITOLAK']:
        messages.error(request, 'Pengajuan yang sudah disetujui atau dibatalkan tidak dapat dihapus.')
        return redirect('riwayat')

    if request.method == 'POST':
        pem.delete()
        messages.success(request, 'Pengajuan berhasil dihapus.')
        if request.user.is_staff:
            return redirect('pengajuan_admin')
        else:
            return redirect('riwayat')

    # jika akses GET, kembalikan ke daftar
    if request.user.is_staff:
        return redirect('pengajuan_admin')
    return redirect('riwayat')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat. Silakan login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'peminjaman/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def batalkan_peminjaman(request, pk):
    """
    User mengajukan permintaan pembatalan (tidak langsung batal).
    Admin harus konfirmasi lewat halaman admin.
    """
    pem = get_object_or_404(Peminjaman, pk=pk)

    # cek kepemilikan (kecuali admin)
    if pem.peminjam != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak punya izin membatalkan pengajuan ini.")
        return redirect('riwayat')

    # hanya yang DISUSUJUI yang bisa diminta batal
    if pem.status != 'DISETUJUI':
        messages.error(request, "Hanya pengajuan yang sudah DISETUJUI yang bisa diminta pembatalan.")
        return redirect('riwayat')

    # kalau sudah pernah minta batal, jangan dobel
    if pem.minta_batal:
        messages.info(request, "Permintaan pembatalan untuk pengajuan ini sudah dikirim dan menunggu admin.")
        return redirect('riwayat')

    if request.method == 'POST':
        alasan = request.POST.get('alasan', '').strip()
        if not alasan:
            messages.error(request, "Alasan pembatalan wajib diisi.")
            return redirect('riwayat')

        pem.minta_batal = True
        pem.alasan_pembatalan = alasan
        pem.save()

        messages.success(request, "Permintaan pembatalan berhasil dikirim. Menunggu konfirmasi admin.")
        return redirect('riwayat')

    # kalau diakses GET (mis. lewat link), arahkan ke riwayat saja
    return redirect('riwayat')


# ------------------------
# Admin: konfirmasi minta batal
# ------------------------
@user_passes_test(is_admin)
def setujui_pembatalan(request, pk):
    pem = get_object_or_404(Peminjaman, pk=pk)

    # hanya peminjaman yang sedang minta batal bisa disetujui pembatalannya
    if not pem.minta_batal:
        messages.error(request, "Tidak ada permintaan pembatalan untuk pengajuan ini.")
        return redirect('pengajuan_admin')

    if request.method == 'POST':
        catatan = request.POST.get('catatan_admin', '').strip()
        if catatan:
            pem.catatan_admin = catatan

        pem.status = 'DIBATALKAN'
        pem.minta_batal = False
        pem.save()

        messages.success(request, "Permintaan pembatalan disetujui — pengajuan dibatalkan.")
        return redirect('pengajuan_admin')

    # Jika ingin sebuah konfirmasi halaman sebelum POST, buat template; untuk sekarang redirect.
    messages.info(request, "Harap konfirmasi lewat form proses pengajuan.")
    return redirect('pengajuan_admin')


@user_passes_test(is_admin)
def tolak_pembatalan(request, pk):
    pem = get_object_or_404(Peminjaman, pk=pk)

    if not pem.minta_batal:
        messages.error(request, "Tidak ada permintaan pembatalan untuk pengajuan ini.")
        return redirect('pengajuan_admin')

    if request.method == 'POST':
        catatan = request.POST.get('catatan_admin', '').strip()
        if not catatan:
            messages.error(request, "Berikan alasan penolakan pembatalan (catatan admin).")
            return redirect('pengajuan_admin')

        pem.minta_batal = False
        # tetap biarkan status sebelumnya (biasanya DISETUJUI)
        pem.save()
        messages.success(request, "Permintaan pembatalan ditolak. Status kembali aktif.")
        return redirect('pengajuan_admin')

    messages.info(request, "Harap konfirmasi lewat form proses pengajuan.")
    return redirect('pengajuan_admin')
