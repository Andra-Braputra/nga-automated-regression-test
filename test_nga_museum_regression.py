import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

class TestNGAMuseumAutomation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Konfigurasi global browser, dijalankan sekali sebelum semua tes dimulai."""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()
        cls.base_url = "https://www.nga.gov/"
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        """Menutup browser secara bersih, dijalankan sekali setelah semua fungsi tes selesai."""
        cls.driver.quit()

    def reset_to_home(self):
        """Helper: membersihkan session dan mengembalikan browser ke Beranda."""
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()
        time.sleep(2)

    def do_search(self, keyword):
        """
        Helper: buka beranda, klik tombol ikon kaca pembesar, masukkan kata kunci,
        lalu tekan Enter. Menggunakan mekanisme pencarian yang sama seperti TC_POS_002
        (sudah terverifikasi benar).
        """
        self.reset_to_home()
        search_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[2]/div/button"
        )))
        search_button.click()
        search_input = self.wait.until(
            EC.visibility_of_element_located((By.ID, "aws-search-input"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

    # ==========================================
    # --- 10 POSITIVE SCENARIOS ---
    # ==========================================

    def test_tc_pos_001_verify_main_logo(self):
        """Verifikasi elemen logo utama NGA terlihat di Beranda."""
        self.reset_to_home()
        logo_link = self.wait.until(EC.presence_of_element_located((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[1]/div[1]/div/a[2]"
        )))
        self.assertTrue(logo_link.is_displayed())
        print("TC_POS_001: Pas (Logo utama terverifikasi)")

    def test_tc_pos_002_search_artist(self):
        """Verifikasi fitur pencarian seniman berhasil membuka halaman hasil."""
        self.do_search("Monet")
        self.wait.until(EC.url_contains("search"))
        self.assertIn("search", self.driver.current_url,
                      "URL tidak mengarah ke halaman pencarian!")
        print("TC_POS_002: Pas (Pencarian nama seniman berhasil)")

    def test_tc_pos_003_open_exhibitions_menu(self):
        """Verifikasi menu Exhibitions dapat dibuka dari navigasi utama."""
        self.reset_to_home()
        exhibitions_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Exhibitions"))
        )
        exhibitions_link.click()
        self.wait.until(EC.url_contains("exhibitions"))
        self.assertIn("exhibitions", self.driver.current_url)
        print("TC_POS_003: Pas (Menu Exhibitions terbuka)")

    def test_tc_pos_004_open_directions_menu(self):
        """Verifikasi menu Directions/Visit dapat dibuka dari navigasi utama."""
        self.reset_to_home()
        directions_link = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[2]/nav[1]/ul/li[2]/a"
        )))
        directions_link.click()
        self.wait.until(EC.url_contains("visit"))
        self.assertIn("visit", self.driver.current_url)
        print("TC_POS_004: Pas (Halaman Directions/Visit terbuka)")

    def test_tc_pos_005_click_art_object_card(self):
        """Buka halaman Art Search lalu klik kartu karya seni pertama."""
        self.reset_to_home()
        
        self.driver.get(f"{self.base_url}artwork-search")

        first_artwork_link = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/main/div/div/div/div/div/div/div[2]/div/ul/li[1]/div/div[3]/h4/a"
        )))
        first_artwork_link.click()
        
        self.wait.until(lambda driver: "search" not in driver.current_url.lower())
        
        self.assertTrue(len(self.driver.current_url) > len(self.base_url), f"Gagal memuat detail objek. URL aktif: {self.driver.current_url}")
        print("TC_POS_005: Pas (Halaman detail karya seni berhasil terbuka)")

    def test_tc_pos_006_verify_high_res_image_loads(self):
        """
        Verifikasi gambar utama karya seni berhasil termuat pada halaman detail.
        PERBAIKAN: Tidak ada ID 'mainimage' pada website NGA. Selector diganti ke
        CSS yang mencari tag <img> dalam area konten utama halaman detail.
        """
        self.reset_to_home()
        self.driver.get(f"{self.base_url}collection/art-object-page.10638.html")

        # Gambar utama karya seni berada dalam elemen semantic konten halaman detail
        main_image = self.wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "main img, article img, figure img"
        )))
        self.assertTrue(main_image.is_displayed(),
                        "Gambar utama karya seni tidak terlihat di halaman!")
        print("TC_POS_006: Pas (Gambar utama karya seni berhasil termuat)")

    def test_tc_pos_007_verify_artwork_metadata_text(self):
        """Verifikasi judul h1 tidak kosong pada halaman detail karya seni."""
        self.reset_to_home()
        self.driver.get(f"{self.base_url}collection/art-object-page.10638.html")

        title_element = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        title_text = title_element.text.strip()
        self.assertGreater(len(title_text), 0, "Metadata judul h1 kosong!")
        print("TC_POS_007: Pas (Metadata teks judul karya seni valid)")

    def test_tc_pos_008_open_visit_page(self):
        """Verifikasi mega menu Visit dan submenu Plan Your Visit dapat terbuka."""
        self.reset_to_home()
        
        # 1. Klik tombol menu utama "Visit" menggunakan XPath presisi Anda
        visit_dropdown_trigger = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[1]/ul/li[1]/button"
        )))
        visit_dropdown_trigger.click()
        
        # 2. Tunggu panel tirai sub-menu muncul di layar, lalu klik tautan teks "Plan Your Visit"
        plan_visit_link = self.wait.until(EC.element_to_be_clickable((
            By.LINK_TEXT, "Plan Your Visit"
        )))
        plan_visit_link.click()
        
        # 3. Tunggu dan validasi perpindahan URL halaman informasi kunjungan
        self.wait.until(EC.url_contains("visit"))
        self.assertIn("visit", self.driver.current_url.lower(), f"Gagal memuat halaman kunjungan. URL aktif: {self.driver.current_url}")
        print("TC_POS_008: Pas (Halaman Plan Your Visit sukses diakses via mega menu)")

    def test_tc_pos_009_open_calendar_events(self):
        """
        Verifikasi halaman kalender acara dapat diakses dan memuat konten.
        PERBAIKAN: Validasi bukan hanya URL, tapi juga memastikan konten h1
        halaman kalender berhasil ter-render.
        """
        self.reset_to_home()
        self.driver.get(f"{self.base_url}calendar.html")

        # Halaman kalender memiliki heading h1 sebagai penanda konten termuat
        heading = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertTrue(heading.is_displayed(),
                        "Heading halaman kalender tidak terlihat!")
        print("TC_POS_009: Pas (Halaman Kalender Acara termuat)")

    def test_tc_pos_010_logo_click_redirects_home(self):
        """
        Verifikasi klik logo NGA dari halaman lain mengembalikan user ke Beranda.
        PERBAIKAN: Tidak ada class 'nga-logo' pada website. Menggunakan XPath logo
        yang sudah terverifikasi benar di TC_POS_001.
        """
        self.reset_to_home()
        # Navigasi ke halaman lain terlebih dahulu
        self.driver.get(f"{self.base_url}visit.html")
        time.sleep(1)

        # Gunakan XPath yang sama dengan TC_POS_001 (sudah terverifikasi)
        logo_link = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[1]/div[1]/div/a[2]"
        )))
        logo_link.click()
        self.wait.until(EC.url_to_be(self.base_url))
        self.assertEqual(self.driver.current_url, self.base_url,
                         "Klik logo tidak mengarahkan kembali ke Beranda!")
        print("TC_POS_010: Pas (Navigasi balik ke Beranda via logo)")

    # ==========================================
    # --- 10 NEGATIVE SCENARIOS ---
    # ==========================================

    def test_tc_neg_011_search_no_results(self):
        """
        Verifikasi pesan 'tidak ada hasil' muncul untuk kata kunci fiktif.
        PERBAIKAN: Gunakan mekanisme pencarian nyata (tombol + aws-search-input),
        lalu scan teks body secara fleksibel — lebih tahan terhadap perubahan markup
        dibanding XPath spesifik.
        """
        self.do_search("xyz123abc999unknown")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        has_no_result = any(phrase in body_text for phrase in [
            "no results", "0 results", "no matches",
            "couldn't find", "did not match", "not found"
        ])
        self.assertTrue(has_no_result,
                        "Indikator 'tidak ada hasil' tidak ditemukan di halaman!")
        print("TC_NEG_011: Pas (Pesan 'tidak ada hasil' muncul)")

    def test_tc_neg_012_empty_search_input(self):
        """
        Verifikasi pencarian dengan input kosong tidak menyebabkan error fatal.
        PERBAIKAN: Gunakan mekanisme pencarian nyata (tombol + aws-search-input)
        bukan URL 'global-search-page.html' yang tidak ada di website.
        """
        self.reset_to_home()
        search_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[2]/div/button"
        )))
        search_button.click()
        search_input = self.wait.until(
            EC.visibility_of_element_located((By.ID, "aws-search-input"))
        )
        search_input.clear()
        # Kirim tanpa isi (Enter langsung)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman tidak dapat dimuat setelah pencarian kosong!")
        print("TC_NEG_012: Pas (Pencarian input kosong ditangani aman)")

    def test_tc_neg_013_invalid_art_id_404(self):
        """
        Verifikasi halaman merespons dengan baik untuk ID karya seni tidak valid.
        Baik itu 404, redirect, atau fallback — halaman harus tetap memuat konten.
        """
        self.reset_to_home()
        self.driver.get(f"{self.base_url}collection/art-object-page.abcdeXYZ.html")
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed())
        # Pastikan halaman tidak kosong total (ada minimal konten fallback/error)
        body_text = body.text.strip()
        self.assertGreater(len(body_text), 0,
                           "Halaman tampak kosong total untuk ID tidak valid!")
        print("TC_NEG_013: Pas (Respons URL ID tidak valid berhasil ditangani)")

    def test_tc_neg_014_script_injection_defense(self):
        """
        Verifikasi sistem aman dari script injection via input pencarian.
        PERBAIKAN: Gunakan mekanisme pencarian nyata + cek apakah alert JS terpicu
        (indikator XSS). Tidak menggunakan URL 'global-search-page.html' yang tidak ada.
        """
        self.do_search("<script>alert('xss')</script>")
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed())
        # Verifikasi: tidak boleh ada dialog alert JavaScript yang muncul
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            self.fail("BAHAYA: Alert JavaScript terdeteksi — potensi celah XSS!")
        except NoAlertPresentException:
            pass  # Tidak ada alert = sistem aman
        print("TC_NEG_014: Pas (Sistem aman dari injeksi skrip berbahaya)")

    def test_tc_neg_015_extreme_long_input(self):
        """
        Verifikasi form pencarian stabil saat menerima input sangat panjang (300 karakter).
        PERBAIKAN: Gunakan mekanisme pencarian nyata (tombol + aws-search-input)
        bukan 'global-search-page.html' + By.NAME 'search' yang tidak ada.
        """
        self.reset_to_home()
        search_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[2]/div/button"
        )))
        search_button.click()
        search_input = self.wait.until(
            EC.visibility_of_element_located((By.ID, "aws-search-input"))
        )
        search_input.clear()
        # Input panjang ekstrem 300 karakter
        search_input.send_keys("A" * 300)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman tidak dapat dimuat setelah input ekstrem panjang!")
        print("TC_NEG_015: Pas (Form input stabil menahan masukan kata kunci ekstrem)")

    def test_tc_neg_016_invalid_year_range_logic(self):
        """
        Verifikasi sistem tidak crash untuk filter tahun terbalik (start > end).
        PERBAIKAN: URL yang benar adalah 'collection-search-result.html'
        (bukan 'collection/collection-search.html' yang merupakan halaman form pencarian).
        """
        self.reset_to_home()
        self.driver.get(
            f"{self.base_url}collection-search-result.html"
            "?year_start=2026&year_end=1500"
        )
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman crash untuk filter tahun terbalik!")
        print("TC_NEG_016: Pas (Sistem menangani logika filter tahun terbalik tanpa crash)")

    def test_tc_neg_017_white_spaces_only_search(self):
        """
        Verifikasi pencarian yang hanya berisi spasi tidak menyebabkan error.
        PERBAIKAN: Gunakan mekanisme pencarian nyata bukan URL 'global-search-page.html'.
        """
        self.reset_to_home()
        search_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "/html/body/div[2]/div[1]/header/div[2]/nav/div[2]/div/button"
        )))
        search_button.click()
        search_input = self.wait.until(
            EC.visibility_of_element_located((By.ID, "aws-search-input"))
        )
        search_input.clear()
        # Input hanya berisi spasi
        search_input.send_keys("     ")
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman tidak dapat dimuat setelah pencarian spasi!")
        print("TC_NEG_017: Pas (Pencarian spasi kosong berturut-turut ditangani)")

    def test_tc_neg_018_malicious_redirect_url(self):
        """
        Verifikasi sistem tidak mengizinkan open redirect ke domain eksternal
        via parameter URL.
        """
        self.reset_to_home()
        self.driver.get(f"{self.base_url}?redirect=https://google.com")
        time.sleep(2)
        self.assertIn("nga.gov", self.driver.current_url,
                      "BAHAYA: Redirect ke domain eksternal terdeteksi (Open Redirect)!")
        print("TC_NEG_018: Pas (Sistem kebal dari celah Open Redirect via parameter)")

    def test_tc_neg_019_negative_pagination_page(self):
        """
        Verifikasi sistem menangani nomor halaman negatif dengan aman.
        PERBAIKAN: Menggunakan 'collection-search-result.html' dan parameter
        'pageNumber' sesuai dokumentasi URL NGA yang sesungguhnya.
        """
        self.reset_to_home()
        self.driver.get(
            f"{self.base_url}collection-search-result.html?pageNumber=-5"
        )
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman crash untuk parameter pageNumber negatif!")
        print("TC_NEG_019: Pas (Input nomor halaman negatif ditangani dengan aman)")

    def test_tc_neg_020_alphabet_input_in_year_filter(self):
        """
        Verifikasi sistem menangani input huruf pada kolom filter angka tahun.
        PERBAIKAN: Menggunakan 'collection-search-result.html' sebagai URL hasil
        pencarian yang valid (bukan 'collection/collection-search.html').
        """
        self.reset_to_home()
        self.driver.get(
            f"{self.base_url}collection-search-result.html"
            "?year_start=tahun_baru"
        )
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        "Halaman crash untuk input huruf pada filter tahun!")
        print("TC_NEG_020: Pas (Input huruf pada kolom filter tahun berhasil diredam)")


# --- BLOK EKSEKUSI RUNNER UNITTEST ---
if __name__ == "__main__":
    print("=== Menjalankan Pengujian Regresi Berbasis Unittest (nga.gov) ===\n")
    unittest.main(verbosity=2)