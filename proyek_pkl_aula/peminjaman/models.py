from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Ruangan(models.Model):
    nama = models.CharField(max_length=100)
    kapasitas = models.IntegerField()
    fasilitas = models.TextField(blank=True)
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return self.nama


class Peminjaman(models.Model):
    STATUS_CHOICES = [
        ('MENUNGGU', 'Menunggu Verifikasi'),
        ('DISETUJUI', 'Disetujui'),
        ('DITOLAK', 'Ditolak'),
        ('MENUNGGU_PEMBATALAN', 'Menunggu Pembatalan'),
        ('DIBATALKAN', 'Dibatalkan oleh Pemohon'),
        ('SELESAI', 'Selesai'),
    ]
    
    HARI_CHOICES = [
        ('SENIN', 'Senin'),
        ('SELASA', 'Selasa'),
        ('RABU', 'Rabu'),
        ('KAMIS', 'Kamis'),
        ('JUMAT', 'Jumat'),
        ('SABTU', 'Sabtu'),
        ('MINGGU', 'Minggu'),
    ]

    peminjam = models.ForeignKey(User, on_delete=models.CASCADE)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.CASCADE)

    # Hari otomatis dari tanggal_mulai
    hari = models.CharField(
        max_length=10,
        choices=HARI_CHOICES,
        blank=True
    )

    tanggal_mulai = models.DateTimeField()
    tanggal_selesai = models.DateTimeField()
    nama_kegiatan = models.CharField(max_length=200)

    # Penanggung jawab
    penanggung_jawab = models.CharField(
        "Nama Penanggung Jawab Kegiatan",
        max_length=100,
        blank=True
    )
    no_hp_penanggung = models.CharField(
        "No. HP Penanggung Jawab",
        max_length=20,
        blank=True
    )

    keterangan = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='MENUNGGU'
    )

    # apakah user sudah mengajukan permintaan pembatalan (flag)
    minta_batal = models.BooleanField(
        "User mengajukan pembatalan?",
        default=False
    )

    # Alasan yang dituliskan user saat mengajukan pembatalan
    alasan_pembatalan = models.TextField(
        "Alasan Pembatalan oleh Pemohon",
        blank=True,
        null=True
    )

    # admin yang menyetujui pembatalan (nullable)
    pembatalan_disetujui_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pembatalan_disetujui_oleh'
    )
    pembatalan_disetujui_pada = models.DateTimeField(null=True, blank=True)

    catatan_admin = models.TextField(blank=True)

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # kalau tanggal_mulai ada, otomatis tentukan hari
        if self.tanggal_mulai:
            dt = timezone.localtime(self.tanggal_mulai)
            weekday = dt.weekday()  # Senin=0 ... Minggu=6
            mapping = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU', 'MINGGU']
            self.hari = mapping[weekday]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_kegiatan} - {self.ruangan}"
