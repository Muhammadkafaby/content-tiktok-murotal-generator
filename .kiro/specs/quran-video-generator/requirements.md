# Requirements Document

## Introduction

Sistem auto-generate video quotes Al-Quran untuk konten TikTok. Sistem akan secara otomatis memilih ayat random, mengambil audio murotal, menggabungkan dengan background video pemandangan aesthetic, dan menghasilkan video siap posting. Diakses melalui web interface dan di-deploy menggunakan Docker di VPS.

## Requirements

### Requirement 1

**User Story:** Sebagai content creator, saya ingin sistem otomatis generate video quotes Quran, sehingga saya tidak perlu membuat konten secara manual.

#### Acceptance Criteria

1. WHEN sistem melakukan generate THEN sistem SHALL memilih ayat secara random dari 6236 ayat Al-Quran
2. WHEN ayat dipilih THEN sistem SHALL mengambil teks Arab, terjemahan Indonesia, dan audio murotal dari API
3. WHEN video di-generate THEN sistem SHALL menggabungkan background video pemandangan dengan overlay teks ayat dan audio murotal
4. WHEN video selesai di-generate THEN sistem SHALL menyimpan video dalam format MP4 dengan rasio 9:16 (TikTok)
5. WHEN generate batch THEN sistem SHALL dapat membuat multiple video sekaligus tanpa duplikasi ayat

### Requirement 2

**User Story:** Sebagai user, saya ingin mengakses sistem melalui web interface, sehingga saya dapat mengelola dan download video dengan mudah.

#### Acceptance Criteria

1. WHEN user mengakses website THEN sistem SHALL menampilkan dashboard dengan daftar video yang sudah di-generate
2. WHEN user klik tombol generate THEN sistem SHALL memulai proses generate video baru
3. WHEN video selesai di-generate THEN sistem SHALL menampilkan preview dan tombol download
4. WHEN user ingin generate batch THEN sistem SHALL menyediakan input jumlah video yang ingin di-generate
5. WHEN proses generate berjalan THEN sistem SHALL menampilkan progress/status generate

### Requirement 3

**User Story:** Sebagai user, saya ingin memilih qari dan style background, sehingga video yang dihasilkan sesuai preferensi saya.

#### Acceptance Criteria

1. WHEN user membuka settings THEN sistem SHALL menampilkan pilihan qari (Alafasy, Abdul Basit, Sudais, dll)
2. WHEN user memilih qari THEN sistem SHALL menggunakan audio murotal dari qari tersebut
3. WHEN generate video THEN sistem SHALL random memilih background video dari koleksi pemandangan aesthetic
4. WHEN video di-generate THEN sistem SHALL menampilkan teks Arab dengan font kaligrafi yang jelas terbaca
5. WHEN video di-generate THEN sistem SHALL menampilkan terjemahan Indonesia di bawah teks Arab

### Requirement 4

**User Story:** Sebagai admin VPS, saya ingin sistem berjalan dalam Docker container, sehingga mudah di-deploy dan dikelola.

#### Acceptance Criteria

1. WHEN deploy aplikasi THEN sistem SHALL dapat dijalankan menggunakan docker-compose
2. WHEN container berjalan THEN sistem SHALL dapat diakses melalui IP public VPS pada port tertentu
3. WHEN sistem restart THEN sistem SHALL mempertahankan data video yang sudah di-generate
4. WHEN sistem berjalan THEN sistem SHALL menyimpan video di volume persistent
5. WHEN sistem error THEN sistem SHALL mencatat log untuk debugging

### Requirement 5

**User Story:** Sebagai user, saya ingin sistem dapat auto-generate video secara terjadwal, sehingga konten tersedia tanpa harus trigger manual.

#### Acceptance Criteria

1. WHEN scheduler aktif THEN sistem SHALL generate video sesuai jadwal yang ditentukan (misal 5 video/hari)
2. WHEN jadwal generate THEN sistem SHALL dapat dikonfigurasi melalui web interface
3. WHEN auto-generate berjalan THEN sistem SHALL mencatat history generate di dashboard
4. WHEN storage hampir penuh THEN sistem SHALL memberikan notifikasi di dashboard


### Requirement 6

**User Story:** Sebagai content creator, saya ingin sistem dapat auto-posting video ke TikTok, sehingga saya tidak perlu upload manual.

#### Acceptance Criteria

1. WHEN user mengaktifkan auto-posting THEN sistem SHALL dapat login ke TikTok menggunakan session cookies yang tersimpan
2. WHEN video selesai di-generate THEN sistem SHALL dapat otomatis upload video ke TikTok via headless browser
3. WHEN upload video THEN sistem SHALL mengisi caption dengan teks ayat dan hashtag yang relevan (mode template atau AI-generated)
4. WHEN posting berhasil THEN sistem SHALL mencatat status posting di dashboard
5. WHEN posting gagal THEN sistem SHALL retry dan mencatat error untuk debugging
6. WHEN user setup TikTok account THEN sistem SHALL menyediakan interface untuk login dan menyimpan session


### Requirement 7

**User Story:** Sebagai content creator, saya ingin caption video di-generate secara otomatis oleh AI, sehingga caption lebih engaging dan bervariasi.

#### Acceptance Criteria

1. WHEN user memilih mode AI caption THEN sistem SHALL menggunakan OpenAI API untuk generate caption
2. WHEN AI generate caption THEN sistem SHALL menyertakan nama surah, nomor ayat, dan hikmah/konteks dari ayat
3. WHEN AI generate caption THEN sistem SHALL menambahkan emoji dan hashtag yang relevan
4. WHEN OpenAI API tidak tersedia THEN sistem SHALL fallback ke mode template statis
5. WHEN user memilih mode template THEN sistem SHALL menggunakan format caption sederhana tanpa AI


### Requirement 8

**User Story:** Sebagai content creator, saya ingin teks Arab dan terjemahan muncul sinkron mengikuti audio murottal, sehingga penonton dapat membaca ayat bersamaan dengan bacaan qari.

#### Acceptance Criteria

1. WHEN video di-generate THEN sistem SHALL menampilkan teks Arab yang sinkron dengan timing audio murottal
2. WHEN audio murottal diputar THEN sistem SHALL menampilkan terjemahan Indonesia yang muncul setelah teks Arab selesai dibacakan
3. WHEN ayat memiliki multiple segments THEN sistem SHALL membagi teks menjadi bagian-bagian yang sesuai dengan jeda bacaan qari
4. WHEN teks ditampilkan THEN sistem SHALL menggunakan animasi fade-in/fade-out yang smooth untuk transisi antar segment
5. WHEN audio murottal memiliki durasi tertentu THEN sistem SHALL menyesuaikan timing tampilan teks agar selesai bersamaan dengan audio
