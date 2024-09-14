import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#! Chrome profilinizin fiziki yolu. Məndə ubuntuda /home/giganet/.config/google-chrome/Default/ şəkilə göstərilir.
chrome_profile_path = "/home/giganet/.config/google-chrome/Default/" 


options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")
driver = webdriver.Chrome(options=options)
# options.add_argument("--no-sandbox") #! Arxa fonda çalışmasını istəyirsizsə komentdən çıxarın   
# options.add_argument("--headless") #! Arxa fonda çalışmasını istəyirsizsə komentdən çıxarın


#! Bir dəfə eləmək kifayətdir. Növbəti dəfə run etdikdə 2 sətri komentə alın
driver.get('https://web.whatsapp.com')
input("WhatsApp Web'e giriş yapın ve devam etmek için Enter'a basın...")


numbers = ["994703335610", "994507737203", "5560771112"] #Nömrələr
messages = ["Sən də qaqaş!", "Mən də qaqaş!"]

for number in numbers:
    url = f"https://web.whatsapp.com/send?phone={number}&text={messages[0]}"
    driver.get(url)

    time.sleep(30)  # Həm səhifənin yüklənməsi üçün həm də bloka düşməmək üçün

    try:
        # messages[0] mesajı ilə dinamic html`də text inputunu tapırıq
        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@contenteditable="true" and contains(., "{messages[0]}")]'))
        )
        send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        send_button.click()

        # messages listindəki digər mesajları sıra ilə göndəririk
        for message in messages[1:]:
            message_box.send_keys(message)
            send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')

            send_button.click()

            time.sleep(2)  # Mesajlar arasında gözləmə anı

        print(f"Mesajlar {number} numarasına gönderildi.")

    except Exception as e:
        print(f"{number} numarasına mesaj gönderilemedi: {e}")

driver.quit()