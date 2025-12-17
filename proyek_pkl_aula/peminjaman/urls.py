from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jadwal/', views.jadwal, name='jadwal'),
    path('ajukan/', views.ajukan_peminjaman, name='ajukan'),
    path('riwayat/', views.riwayat, name='riwayat'),

    # ============================
    # ADMIN / DASHBOARD PEMINJAMAN
    # ============================
    path('pengajuan-admin/', views.pengajuan_admin, name='pengajuan_admin'),
    path('pengajuan-admin/<int:pk>/', views.proses_pengajuan, name='proses_pengajuan'),

    # menghapus peminjaman (user atau admin)
    path('peminjaman/<int:pk>/hapus/', views.hapus_peminjaman, name='hapus_peminjaman'),

    # user mengajukan pembatalan
    path('peminjaman/<int:pk>/batalkan/', views.batalkan_peminjaman, name='batalkan_peminjaman'),

    # admin menyetujui permintaan pembatalan
    path(
        'peminjaman/<int:pk>/setujui-pembatalan/',
        views.setujui_pembatalan,
        name='setujui_pembatalan'
    ),

    # admin menolak permintaan pembatalan
    path(
        'peminjaman/<int:pk>/tolak-pembatalan/',
        views.tolak_pembatalan,
        name='tolak_pembatalan'
    ),

    # ============================
    # AUTH
    # ============================
    path('login/', auth_views.LoginView.as_view(template_name='peminjaman/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
]
