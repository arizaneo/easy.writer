# easy.writer
Easy Writer software for LCD Panel Control Boards

Geliştirme taleplerine uygun olarak aşağıdaki kod bölümlerine yorumlar eklendi:

Auto WP ayarının varsayılan olarak aktif yapılması için combo_wp.set("1") önerildi.

FTDI/VGA frekans ayarı zaten kullanıcı tarafından değiştirilebilir; istersen dosyaya kaydetme de ekleyebiliriz.

Log kaydı için output_text kısmındaki veriler .txt dosyasına da yönlendirilebilir.

EasyWriter ile senkronizasyon için trigger_isp() fonksiyonu genişletilebilir; örneğin EasyWriter log dosyası okunarak izleme yapılabilir.

