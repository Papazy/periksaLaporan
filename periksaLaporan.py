# ======================================================================
#         SISTEM PEMERIKSA HURUF MIRING DAN TYPO - VERSI LENGKAP
# ======================================================================
# Membutuhkan:
# 1. PyMuPDF   (pip install PyMuPDF)
# 2. PySastrawi (pip install PySastrawi)
# 3. File kamus "kbbi.txt"

import fitz  # PyMuPDF
import string
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class LaporanChecker:
    def __init__(self, kamus_filepath):
        """Inisialisasi checker dengan memuat kamus dan stemmer"""
        self.kamus = self.muat_kamus(kamus_filepath)
        if self.kamus:
            factory = StemmerFactory()
            self.stemmer = factory.create_stemmer()
            self.setup_patterns()
        
    def muat_kamus(self, filepath):
        """Memuat daftar kata dari file kbbi.txt"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                kamus = {line.strip().lower() for line in file if line.strip()}
                
                # Tambahkan kata-kata Indonesia dasar yang mungkin tidak ada di file
                kata_dasar_indonesia = {
                    'dan', 'atau', 'tetapi', 'namun', 'kemudian', 'lalu', 'maka',
                    'jika', 'kalau', 'apabila', 'bila', 'ketika', 'saat', 'waktu',
                    'setiap', 'semua', 'seluruh', 'sebagian', 'beberapa', 'banyak',
                    'sedikit', 'lebih', 'kurang', 'sama', 'beda', 'berbeda',
                    'ini', 'itu', 'tersebut', 'berikut', 'tadi', 'nanti',
                    'sudah', 'belum', 'sedang', 'akan', 'telah', 'pernah',
                    'tidak', 'bukan', 'tanpa', 'dengan', 'oleh', 'untuk',
                    'dari', 'ke', 'di', 'pada', 'dalam', 'luar', 'atas', 'bawah',
                    'antara', 'sekitar', 'hingga', 'sampai', 'sejak', 'selama',
                    'tentang', 'mengenai', 'terhadap', 'kepada', 'daripada',
                    'berdasarkan', 'melalui', 'menurut', 'sesuai', 'seperti',
                    'sebagai', 'adalah', 'merupakan', 'menjadi', 'dapat', 'bisa',
                    'harus', 'perlu', 'mungkin', 'pasti', 'tentu', 'jelas',
                    'baik', 'buruk', 'besar', 'kecil', 'tinggi', 'rendah',
                    'panjang', 'pendek', 'luas', 'sempit', 'tebal', 'tipis',
                    # Tambahan kata umum
                    'yang', 'juga', 'saja', 'masih', 'hanya', 'cukup', 'sangat',
                    'agak', 'hampir', 'sekali', 'kali', 'baru', 'lama', 'muda', 'tua',
                    # Kata yang sering ada di dokumen akademik
                    'latar', 'belakang', 'rumusan', 'masalah', 'tujuan', 'penelitian',
                    'analisis', 'pembahasan', 'kesimpulan', 'saran', 'daftar', 'pustaka',
                    'metode', 'metodologi', 'hasil', 'data', 'informasi', 'sistem'
                }
                kamus.update(kata_dasar_indonesia)
                
                print(f"Berhasil memuat {len(kamus)} kata dari kamus (termasuk kata dasar)")
                return kamus
        except FileNotFoundError:
            print(f"Peringatan: File kamus '{filepath}' tidak ditemukan.")
            print("Menggunakan kamus dasar minimal...")
            return self.get_minimal_kamus()
        except Exception as e:
            print(f"Error saat memuat kamus: {e}")
            return self.get_minimal_kamus()
    
    def get_minimal_kamus(self):
        """Kamus minimal jika file KBBI tidak tersedia"""
        return {
            # Kata hubung dan partikel
            'dan', 'atau', 'tetapi', 'namun', 'kemudian', 'lalu', 'maka', 'jadi',
            'jika', 'kalau', 'apabila', 'bila', 'ketika', 'saat', 'waktu', 'serta',
            'setiap', 'semua', 'seluruh', 'sebagian', 'beberapa', 'banyak', 'sedikit',
            
            # Kata tunjuk dan keterangan
            'ini', 'itu', 'tersebut', 'berikut', 'tadi', 'nanti', 'sekarang',
            'sudah', 'belum', 'sedang', 'akan', 'telah', 'pernah', 'sering', 'jarang',
            
            # Kata negasi dan preposisi
            'tidak', 'bukan', 'tanpa', 'dengan', 'oleh', 'untuk', 'bagi', 'kepada',
            'dari', 'ke', 'di', 'pada', 'dalam', 'luar', 'atas', 'bawah', 'depan',
            'belakang', 'samping', 'antara', 'sekitar', 'hingga', 'sampai', 'sejak',
            
            # Kata keterangan dan kata kerja umum
            'selama', 'tentang', 'mengenai', 'terhadap', 'daripada', 'berdasarkan',
            'melalui', 'menurut', 'sesuai', 'seperti', 'sebagai', 'adalah', 
            'merupakan', 'menjadi', 'dapat', 'bisa', 'harus', 'perlu', 'boleh',
            
            # Kata sifat dasar
            'baik', 'buruk', 'besar', 'kecil', 'tinggi', 'rendah', 'panjang', 
            'pendek', 'luas', 'sempit', 'tebal', 'tipis', 'baru', 'lama', 'muda', 'tua',
            
            # Kata akademik umum
            'latar', 'belakang', 'rumusan', 'masalah', 'tujuan', 'penelitian',
            'analisis', 'pembahasan', 'kesimpulan', 'saran', 'daftar', 'pustaka',
            'metode', 'metodologi', 'hasil', 'data', 'informasi', 'sistem'
        }
    
    def setup_patterns(self):
        """Setup pola regex untuk deteksi berbagai jenis teks"""
        # Pola untuk nama ilmiah (genus species)
        self.scientific_name_pattern = re.compile(r'\b[A-Z][a-z]+ [a-z]+\b')
        
        # Pola untuk nomor romawi
        self.roman_numeral_pattern = re.compile(r'^[ivxlcdm]+$', re.IGNORECASE)
        
        # Pola untuk nomor/kode (1.1, 1.2, dll)
        self.number_code_pattern = re.compile(r'^\d+(\.\d+)*$')
        
        # Pola untuk istilah Latin umum - DIPERBAIKI LEBIH SPESIFIK
        self.latin_patterns = [
            # Hanya frasa Latin lengkap, bukan bagian kata
            re.compile(r'^et\s+al\.?$', re.IGNORECASE),    # "et al" saja
            re.compile(r'^vs\.?$', re.IGNORECASE),         # "vs" saja
            re.compile(r'^viz\.?$', re.IGNORECASE),        # "viz" saja
            re.compile(r'^i\.e\.?$', re.IGNORECASE),       # "i.e." saja
            re.compile(r'^e\.g\.?$', re.IGNORECASE),       # "e.g." saja
            re.compile(r'^cf\.?$', re.IGNORECASE),         # "cf" saja
            re.compile(r'^ibid\.?$', re.IGNORECASE),       # "ibid" saja
            re.compile(r'^idem\.?$', re.IGNORECASE),       # "idem" saja
            re.compile(r'^loc\.?\s*cit\.?$', re.IGNORECASE), # "loc. cit" saja
            re.compile(r'^op\.?\s*cit\.?$', re.IGNORECASE),  # "op. cit" saja
            re.compile(r'^sic\.?$', re.IGNORECASE),        # "sic" saja
            re.compile(r'^passim\.?$', re.IGNORECASE),     # "passim" saja
            re.compile(r'^vide\.?$', re.IGNORECASE),       # "vide" saja
            re.compile(r'^videlicet\.?$', re.IGNORECASE),  # "videlicet" saja
            re.compile(r'^scilicet\.?$', re.IGNORECASE),   # "scilicet" saja
        ]
        
        # Daftar kata bahasa asing umum yang sering muncul
        self.common_foreign_words = {
            'weltanschauung', 'zeitgeist', 'schadenfreude', 'gemeinschaft', 
            'gesellschaft', 'kindergarten', 'wanderlust', 'realpolitik',
            'tsunami', 'karaoke', 'origami', 'samurai', 'geisha', 'sushi',
            'feng shui', 'tai chi', 'qi', 'yin yang', 'kung fu',
            'pizza', 'pasta', 'cappuccino', 'espresso', 'gelato',
            'ballet', 'cafe', 'boulevard', 'boutique', 'naive',
            'software', 'hardware', 'update', 'upgrade', 'download',
            'smartphone', 'laptop', 'tablet', 'website', 'online'
        }
        
        # Daftar kata bahasa daerah umum
        self.regional_words = {
            # Aceh
            'peusijuek', 'saman', 'rapai', 'seudati', 'ranup', 'lampoh',
            'gampong', 'keuchik', 'tueng', 'blang', 'krueng',
            # Jawa
            'gamelan', 'wayang', 'batik', 'gudeg', 'keris', 'blangkon',
            'lurik', 'joglo', 'pendopo', 'alun-alun', 'kretek',
            # Bali
            'pura', 'odalan', 'galungan', 'kuningan', 'nyepi', 'ogoh-ogoh',
            'subak', 'banjar', 'pecalang', 'canang', 'penjor',
            # Minang
            'rendang', 'randai', 'saluang', 'talempong', 'surau',
            'nagari', 'balairung', 'gadang', 'rangkiang', 'bundo',
            # Batak
            'gondang', 'margondang', 'ulos', 'sigale-gale', 'huta',
            'marga', 'dalihan', 'natolu', 'bona', 'pasogit',
            # Sunda
            'angklung', 'kecapi', 'suling', 'degung', 'jaipong',
            'pantun', 'pupuh', 'kawih', 'calung', 'karinding'
        }

        # Daftar kata yang sering salah eja
        self.common_typos = {
            'diatas': 'di atas',
            'dibawah': 'di bawah',
            'didalam': 'di dalam',
            'diluar': 'di luar',
            'dimana': 'di mana',
            'kemana': 'ke mana',
            'darimana': 'dari mana',
            'dimana-mana': 'di mana-mana',
            'disamping': 'di samping',
            'disebelah': 'di sebelah',
            'didepan': 'di depan',
            'dibelakang': 'di belakang',
            'dihadapan': 'di hadapan',
            'diantara': 'di antara',
            'kesana': 'ke sana',
            'kesini': 'ke sini',
            'kesitu': 'ke situ',
            'kesana-kemari': 'ke sana-kemari',
            'karna': 'karena',
            'dgn': 'dengan',
            'yg': 'yang',
            'dg': 'dengan',
            'krn': 'karena',
            'shg': 'sehingga',
            'spt': 'seperti',
            'thd': 'terhadap',
            'pd': 'pada',
            'utk': 'untuk',
            'sbg': 'sebagai',
            'dlm': 'dalam',
            'sblm': 'sebelum',
            'sdh': 'sudah',
            'blm': 'belum',
            'tdk': 'tidak',
            'hrs': 'harus',
            'bs': 'bisa',
            'dpt': 'dapat'
        }

    def is_number_or_code(self, word):
        """Deteksi nomor, kode, atau nomor romawi"""
        word_clean = word.strip(string.punctuation)
        
        # Cek nomor romawi
        if self.roman_numeral_pattern.match(word_clean):
            return True
            
        # Cek nomor/kode seperti 1.1, 1.2, dll
        if self.number_code_pattern.match(word_clean):
            return True
            
        # Cek angka biasa
        if word_clean.replace('.', '').replace(',', '').isdigit():
            return True
            
        return False

    def is_proper_noun(self, word, context=""):
        """
        Deteksi nama diri yang lebih sophisticated
        - Nama orang, tempat, organisasi tidak perlu miring
        - Nama ilmiah perlu miring
        """
        # Jika kata dimulai huruf kapital
        if word and word[0].isupper():
            # Cek apakah ini nama ilmiah (Genus species)
            if self.scientific_name_pattern.match(context) or \
               (len(word.split()) == 2 and all(w[0].isupper() for w in word.split())):
                return False  # Nama ilmiah harus miring
            
            # Cek apakah ini singkatan (semua huruf kapital)
            if word.isupper() and len(word) > 1:
                return True  # Singkatan biasanya nama diri
                
            # Nama diri lainnya
            return True
        
        return False

    def has_indonesian_affixes(self, word):
        """Cek apakah kata memiliki awalan/akhiran Indonesia"""
        word_lower = word.lower()
        
        # Awalan Indonesia yang umum
        indonesian_prefixes = [
            'ber', 'ter', 'me', 'pe', 'ke', 'se', 'di',
            'meng', 'peng', 'peny', 'pen', 'mem', 'pem',
            'men', 'per', 'pel', 'bel', 'tel', 'sel'
        ]
        
        # Akhiran Indonesia yang umum
        indonesian_suffixes = [
            'kan', 'an', 'nya', 'lah', 'kah', 'tah', 'i'
        ]
        
        # Cek awalan
        for prefix in indonesian_prefixes:
            if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
                # Cek apakah setelah awalan ada kata dasar yang dikenal
                remaining = word_lower[len(prefix):]
                
                base_word = self.stemmer.stem(word_lower)
                
                # Cek apakah kata dasar atau sisa kata adalah kata yang dikenal
                # Jika kata dasar sudah dikenal, tidak perlu cek sisa kata
                # debug
                print(f"Memeriksa awalan: {prefix}, sisa kata: {remaining}, kata dasar: {base_word}")
                
                # Jika kata dasar atau sisa kata ada di kamus
                if remaining in self.kamus or base_word in self.kamus:
                    print(f"Kata dengan awalan valid: %s", word_lower)
                    return True
                
                # Atau jika awalan + kata dasar masuk akal secara morfologi
                # if len(remaining) >= 3:  # Minimal 3 huruf setelah awalan
                #     return True
        
        # Cek akhiran
        for suffix in indonesian_suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                remaining = word_lower[:-len(suffix)]
                if remaining in self.kamus:
                    return True
        
        return False

    def is_likely_typo(self, word, base_word):
        """Deteksi kemungkinan typo berdasarkan berbagai indikator"""
        word_lower = word.lower()
        
        # Cek di daftar typo umum
        if word_lower in self.common_typos:
            return True, "common_typo", self.common_typos[word_lower]
        
        # Pola yang mengindikasikan typo
        typo_patterns = [
            # Huruf berulang yang tidak wajar
            r'(.)\1{2,}',  # 3+ huruf sama berturut-turut (contoh: seeeperti)
            
            # Pola ketikan yang salah
            r'[aeiou]{4,}',  # 4+ vokal berturut (contoh: keeeempat)
            r'[bcdfghjklmnpqrstvwxyz]{5,}',  # 5+ konsonan berturut
            
            # Kombinasi huruf yang tidak wajar dalam bahasa Indonesia
            r'[qx]',  # huruf q atau x tanpa u (jarang di Indonesia)
            r'[bcdfghjklmnpqrstvwxyz]{3}[aeiou][bcdfghjklmnpqrstvwxyz]{3}',  # pola asing
        ]
        
        typo_score = 0
        for pattern in typo_patterns:
            if re.search(pattern, word_lower):
                typo_score += 1
        
        # Cek panjang kata yang tidak wajar
        if len(word_lower) > 20:  # Kata terlalu panjang
            typo_score += 1
        
        # Cek karakter yang tidak biasa
        if re.search(r'[^a-zA-Z\-]', word_lower):  # Karakter selain huruf dan tanda hubung
            typo_score += 1
            
        return typo_score >= 2, "potential_typo", None

    def is_foreign_or_regional_word(self, word, base_word):
        """Deteksi kata asing atau daerah"""
        word_lower = word.lower()
        
        # PRIORITAS 1: Cek di kamus Indonesia TERLEBIH DAHULU
        if word_lower in self.kamus or base_word in self.kamus:
            return False, "indonesian"
        
        # PRIORITAS 2: Cek apakah kata memiliki awalan/akhiran Indonesia
        if self.has_indonesian_affixes(word_lower):
            return False, "indonesian_derived"
        
        # PRIORITAS 3: Daftar kata Indonesia umum yang sering salah terdeteksi
        common_indonesian = {
            'tetapi', 'ketika', 'setiap', 'namun', 'kemudian', 'selalu', 'sering',
            'kadang', 'biasanya', 'mungkin', 'seharusnya', 'sebaiknya', 'tentang',
            'terhadap', 'kepada', 'daripada', 'mengenai', 'melalui', 'berdasarkan',
            'termasuk', 'terutama', 'khususnya', 'umumnya', 'seringkali',
            'sekitar', 'antara', 'hingga', 'sampai', 'sejak', 'selama', 'sebelum',
            'sesudah', 'setelah', 'sewaktu', 'sementara', 'sedangkan', 'adapun',
            # Tambahan kata Indonesia yang mengandung 'et'
            'detail', 'complete', 'internet', 'target', 'budget', 'diet', 'eket', 
            'betet', 'metode', 'meter', 'paket', 'tiket', 'market', 'asset', 
            'reset', 'outlet', 'sistem', 'planet', 'genetik', 'atletik', 'estetik',
            'poetik', 'magnetik', 'kinetik', 'sintetik', 'diabetik', 'teoretis',
            'geometri', 'diameter', 'parameter', 'termometer', 'barometer',
            'interpretasi', 'penetrasi', 'vegetasi', 'kompetensi', 'kompetisi',
            # Kata Indonesia lainnya
            'efektif', 'efisien', 'optimal', 'maksimal', 'minimal', 'normal',
            'digital', 'global', 'lokal', 'personal', 'profesional', 'sosial',
            'nasional', 'internasional', 'regional', 'traditional', 'modern'
        }
        
        # Jika kata ada di daftar kata Indonesia umum
        if word_lower in common_indonesian or base_word in common_indonesian:
            return False, "indonesian"
        
        # PRIORITAS 4: Cek di daftar kata asing umum
        if word_lower in self.common_foreign_words:
            return True, "foreign"
            
        # PRIORITAS 5: Cek di daftar kata daerah
        if word_lower in self.regional_words:
            return True, "regional"
            
        # PRIORITAS 6: Cek pola Latin - HANYA untuk frasa lengkap, bukan bagian kata
        for pattern in self.latin_patterns:
            if pattern.fullmatch(word_lower):  # fullmatch untuk keseluruhan kata
                return True, "latin"
        
        # PRIORITAS 7: Heuristik untuk kata asing - LEBIH KETAT
        foreign_patterns = [
            r'^[qxz]',  # kata yang DIMULAI dengan q, x, z
            r'[aeiou]{3,}',  # vokal beruntun 3+  
            r'[bcdfghjklmnpqrstvwxyz]{4,}',  # konsonan beruntun 4+
            r'(sch|tch|ph|th|gh|tion|sion)$',  # pola asing di AKHIR kata
            r'^(ex|pre|post|anti|pro|trans)-',  # awalan asing dengan tanda hubung
        ]
        
        foreign_score = 0
        for pattern in foreign_patterns:
            if re.search(pattern, word_lower):
                foreign_score += 1
        
        # PENTING: Jangan deteksi kata dengan 'et' sebagai asing jika tidak ada pola lain
        if 'et' in word_lower and foreign_score == 0:
            return False, "indonesian_with_et"
        
        # Hanya tandai sebagai asing jika ada CUKUP indikator kuat
        if foreign_score >= 2 and len(word_lower) >= 5:  # Lebih ketat
            return True, "foreign_pattern"
        elif foreign_score >= 3 and len(word_lower) >= 4:  # Sangat ketat untuk kata pendek
            return True, "possible_foreign"
            
        # Default: anggap Indonesia jika tidak ada indikasi kuat sebagai asing
        return False, "indonesian_unknown"

    def analyze_word(self, word, base_word):
        """Analisis komprehensif untuk menentukan jenis kata"""
        word_lower = word.lower()
        
        # 0. Skip nomor dan kode
        if self.is_number_or_code(word):
            return "skip", "number_or_code", None
        
        # 1. Cek typo terlebih dahulu
        is_typo, typo_type, suggestion = self.is_likely_typo(word, base_word)
        if is_typo:
            return "typo", typo_type, suggestion
        
        # 2. Cek kata asing/daerah
        is_foreign, word_type = self.is_foreign_or_regional_word(word, base_word)
        if is_foreign:
            return "italic_needed", word_type, None
        elif word_type in ["indonesian", "indonesian_derived"]:
            return "correct", word_type, None
        
        # 3. Jika tidak ditemukan di mana-mana, kemungkinan typo atau kata tidak dikenal
        if (word_lower not in self.kamus and 
            base_word not in self.kamus and 
            word_lower not in self.common_foreign_words and
            word_lower not in self.regional_words and
            not self.has_indonesian_affixes(word_lower)):
            return "unknown", "not_found", None
        
        return "correct", "indonesian", None

    def get_word_context(self, span_text, word_index):
        """Mendapatkan konteks kata untuk analisis yang lebih baik"""
        words = span_text.split()
        start = max(0, word_index - 2)
        end = min(len(words), word_index + 3)
        return " ".join(words[start:end])

    def calculate_word_bbox(self, span, span_text, word_index, word):
        """Menghitung bounding box untuk kata tertentu dalam span"""
        # Dapatkan semua kata dalam span
        words = span_text.split()
        
        # Hitung posisi kata berdasarkan panjang karakter
        char_position = 0
        for i in range(word_index):
            char_position += len(words[i]) + 1  # +1 untuk spasi
        
        # Estimasi lebar per karakter
        span_width = span["bbox"][2] - span["bbox"][0]
        span_height = span["bbox"][3] - span["bbox"][1]
        total_chars = len(span_text)
        
        if total_chars > 0:
            char_width = span_width / total_chars
            
            # Hitung bounding box kata
            x0 = span["bbox"][0] + (char_position * char_width)
            x1 = x0 + (len(word) * char_width)
            y0 = span["bbox"][1]
            y1 = span["bbox"][3]
            
            return fitz.Rect(x0, y0, x1, y1)
        
        # Fallback jika gagal menghitung
        return fitz.Rect(span["bbox"])

    def periksa_dokumen(self, file_input, file_output):
        """Fungsi utama untuk memeriksa dokumen PDF"""
        if not self.kamus:
            print("Error: Kamus tidak tersedia")
            return
            
        try:
            doc = fitz.open(file_input)
        except Exception as e:
            print(f"Error: Tidak dapat membuka file '{file_input}'. {e}")
            return

        jumlah_italic = 0
        jumlah_typo = 0
        jumlah_unknown = 0
        panjang_kata_minimal = 2
        laporan_temuan = []

        print(f"Memulai pemeriksaan dokumen: {file_input}")
        print("=" * 60)
        
        for page_num, page in enumerate(doc):
            print(f"Halaman {page_num + 1}/{len(doc)}")
            
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Cek apakah teks sudah italic
                        font_name = span["font"].lower()
                        is_italic = any(marker in font_name for marker in 
                                      ['italic', 'oblique', 'slant'])
                        
                        span_text = span["text"]
                        words = span_text.split()
                        
                        # PEMERIKSAAN PER KATA INDIVIDUAL
                        for word_idx, original_word in enumerate(words):
                            # Bersihkan kata
                            cleaned_word = original_word.strip(string.punctuation).lower()
                            
                            # Skip kata pendek, angka, atau kosong
                            if (len(cleaned_word) < panjang_kata_minimal or 
                                cleaned_word.isdigit() or not cleaned_word):
                                continue
                            
                            # Stem kata
                            base_word = self.stemmer.stem(cleaned_word)
                            
                            # Dapatkan konteks
                            context = self.get_word_context(span_text, word_idx)
                            
                            # Analisis kata
                            is_proper = self.is_proper_noun(original_word, context)
                            
                            # Skip proper noun
                            if is_proper:
                                continue
                            
                            # Analisis komprehensif
                            analysis_result, detail_type, suggestion = self.analyze_word(cleaned_word, base_word)
                            
                            # Skip kata yang tidak perlu ditandai
                            if analysis_result in ["skip", "correct"]:
                                continue
                            
                            color = None
                            should_highlight = False
                            
                            if analysis_result == "typo":
                                color = [1, 0, 0]  # Merah untuk typo
                                should_highlight = True
                                jumlah_typo += 1
                                
                            elif analysis_result == "unknown":
                                color = [1, 0, 1]  # Magenta untuk kata tidak dikenal
                                should_highlight = True
                                jumlah_unknown += 1
                                
                            elif analysis_result == "italic_needed" and not is_italic:
                                # Kata asing/daerah yang perlu miring
                                if detail_type == "regional":
                                    color = [1, 1, 0]  # Kuning untuk kata daerah
                                elif detail_type == "foreign":
                                    color = [1, 0.5, 0]  # Oranye untuk kata asing
                                else:
                                    color = [1, 0.8, 0.8]  # Pink muda untuk lainnya
                                should_highlight = True
                                jumlah_italic += 1
                            
                            # TANDAI HANYA KATA INI SAJA
                            if should_highlight:
                                # Hitung bounding box untuk kata ini saja
                                word_rect = self.calculate_word_bbox(span, span_text, word_idx, original_word)
                                
                                # Tandai hanya kata ini
                                highlight = page.add_highlight_annot(word_rect)
                                highlight.set_colors({"stroke": color})
                                highlight.update()
                                
                                temuan = {
                                    'halaman': page_num + 1,
                                    'kata': original_word,
                                    'jenis': analysis_result,
                                    'detail': detail_type,
                                    'saran': suggestion,
                                    'konteks': context
                                }
                                laporan_temuan.append(temuan)
                                
                                if suggestion:
                                    print(f"  ✓ '{original_word}' ({detail_type}) → saran: '{suggestion}'")
                                else:
                                    print(f"  ✓ '{original_word}' ({detail_type}) - {context[:50]}...")

        # Simpan hasil
        total_masalah = jumlah_italic + jumlah_typo + jumlah_unknown
        
        if total_masalah > 0:
            doc.save(file_output, garbage=4, deflate=True)
            print("\n" + "=" * 60)
            print(f"RINGKASAN PEMERIKSAAN")
            print("=" * 60)
            print(f"Kata perlu huruf miring: {jumlah_italic}")
            print(f"Kemungkinan typo: {jumlah_typo}")
            print(f"Kata tidak dikenal: {jumlah_unknown}")
            print(f"Total masalah: {total_masalah}")
            print(f"File hasil: {file_output}")
            
            # Tampilkan legend warna
            print("\nLegend warna:")
            print("  🔴 Merah: Kemungkinan typo")
            print("  🟣 Magenta: Kata tidak dikenal")
            print("  🟡 Kuning: Kata daerah (perlu miring)")
            print("  🟠 Oranye: Kata asing (perlu miring)")
            print("  🩷 Pink: Lainnya (perlu miring)")
            
            # Tampilkan saran perbaikan
            typo_suggestions = [t for t in laporan_temuan if t['saran']]
            if typo_suggestions:
                print("\nSaran perbaikan:")
                for saran in typo_suggestions[:10]:  # Tampilkan 10 saran pertama
                    print(f"  '{saran['kata']}' → '{saran['saran']}'")
                if len(typo_suggestions) > 10:
                    print(f"  ... dan {len(typo_suggestions) - 10} saran lainnya")
                
        else:
            print("\n✅ Tidak ada masalah yang ditemukan!")

        doc.close()

def main():
    """Fungsi utama"""
    print("SISTEM PEMERIKSA HURUF MIRING DAN TYPO")
    print("=" * 40)
    
    # Inisialisasi checker
    checker = LaporanChecker("kbbi.txt")
    if not checker.kamus:
        return
    
    # File input dan output
    file_input = input("Masukkan nama file PDF input (default: laporan.pdf): ").strip()
    if not file_input:
        file_input = "laporan.pdf"
    
    file_output = input("Masukkan nama file PDF output (default: hasil_pemeriksaan.pdf): ").strip()
    if not file_output:
        file_output = "hasil_pemeriksaan.pdf"
    
    # Jalankan pemeriksaan
    checker.periksa_dokumen(file_input, file_output)

if __name__ == "__main__":
    main()