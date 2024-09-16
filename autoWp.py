import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sms_sender import clean_and_format_numbers, write_to_text


def send_extension_sms_to_user(driver, find_word, messages):
    # message mesajı ilə dinamic html`də text inputunu tapırıq
    message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@contenteditable="true" and contains(., "{find_word}")]'))
        )
    for message in messages[1:]:
        message_box.send_keys(message)
        send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')

        send_button.click()
        

        time.sleep(2)  # Mesajlar arasında gözləmə anı

def create_msg(row):
    fullname = row['fullname']
    if fullname == '-' or len(fullname) < 5:
        fullname = "Abonent"
    contract_id = row['contract_id']
    
    message = f"""Salam Hörmətli *{fullname}*, TV xidmətinin aylıq ödənişini etməyinizi xahiş edirik.%0A%0A
Aylıq borcunuz: *{row['amount']} AZN*%0A
Ödəniş kodunuz: {contract_id}%0A%0A
*GAMMANET*%0A
0124041088%0A
0776104888%0A
0774660505"""

    return message

def send_whatsapp_messages():
    #* Chrome profilinizin fiziki yolu. Məndə ubuntuda /home/giganet/.config/google-chrome/Default/ şəkilə göstərilir.
    chrome_profile_path = "/home/giganet/.config/google-chrome/Default/" 

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={chrome_profile_path}")
    # options.add_argument("--no-sandbox") #* Arxa fonda çalışmasını istəyirsizsə komentdən çıxarın   
    # options.add_argument("--headless") #* Arxa fonda çalışmasını istəyirsizsə komentdən çıxarın

    driver = webdriver.Chrome(options=options)
    #* Bir dəfə eləmək kifayətdir. Növbəti dəfə run etdikdə 2 sətri komentə alın
    # driver.get('https://web.whatsapp.com')
    # input("WhatsApp Web'e giriş yapın ve devam etmek için Enter'a basın...")


    deactives = pd.read_csv('Deaktivler.csv')
    for index, row in deactives.iterrows():
        try:
     
            message = create_msg(row)
            phone = clean_and_format_numbers([row['phone']])[0]
            url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
            driver.get(url)

            print("Saytın açılması gözlənilir")
            # Həm səhifənin yüklənməsi üçün həm də bloka düşməmək üçün
            time.sleep(10)  

            print("Saytın açılması gözləmə bitdi.")
            send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
            send_button.click()
            
            print(f"Mesajlar {phone} nömrəsinə göndərildi.")
            write_to_text(file_name="Success_phone", text= f"{phone}\n"+message + "\n\n", folder_name="TV")
            
            time.sleep(10)  # Həm səhifənin yüklənməsi üçün həm də bloka düşməmək üçün
            print("Növbətiyə keçmək üçün 10 saniyə gözləyin")

            # messages listindəki digər mesajları sıra ilə göndəririk
            # send_extension_sms_to_user(driver, message, messages)

        except Exception as e:
            e = str(e)[:100]
            text = f"{row['phone']} numarasına mesaj gönderilemedi: {e}"
            print(text)
            write_to_text(file_name="Error_Phone", text=text, folder_name="TV")
    driver.quit()


send_whatsapp_messages()