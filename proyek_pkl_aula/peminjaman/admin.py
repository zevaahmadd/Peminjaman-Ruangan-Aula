from django.contrib import admin
from .models import Ruangan, Peminjaman

@admin.register(Ruangan)
class RuanganAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kapasitas')

@admin.register(Peminjaman)
class PeminjamanAdmin(admin.ModelAdmin):
    list_display = ('nama_kegiatan', 'ruangan', 'tanggal_mulai', 'status')
    list_filter = ('status', 'ruangan')
    search_fields = ('nama_kegiatan', 'peminjam__username')
