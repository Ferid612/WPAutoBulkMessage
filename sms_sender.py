import hashlib
import json
from datetime import datetime, timedelta
import os


"""
    Bu fayl müştərilərimizə SMS göndermək üçün lazım olan funksiyalar üçün istifadə olunur.
"""

# "key": md5 of ( (md5 of your password) + LOGIN + MSG_BODY + MSISDN + SENDER )









# Numara parçalarında rakam olup olmadığını kontrol eden fonksiyon
def contains_digit(part):
    return any(char.isdigit() for char in part)



def clean_phone_procedure(
    phone,
    combination_texts,
    combination_texts_2,
    combination_texts_3,
    my_except,
    prefix_with_bug,
):
    """Bu funksiya verilən nömrənin təmizlənməsi və standarta formatlanması üçün yaradılmışdır. 

    Args:
        phone (str): müştərinin telefon nömrəsi
        combination_texts (list): ["(050)(055)","(050)(051)"]
        combination_texts_2 (list): ["(050)51)","(050)55)"] 
        combination_texts_3 (list):["050-051","050-055"]
        my_except (list): xarab nömrələri buraya yığırıq 
        prefix_with_bug (list): ["50", "51", "55"...]

    Returns:
        str: təmizlənmiş və standartlaşmış nömrə 
    """
    # Sağ sol boşluqdan təmizlənir, () kimi xətalar təmizlənir
    phone = phone.replace(") ", ")").replace("()", "(0")
    
    # nömrə (50) ilə başlayırsa (050) edirik 
    phone = (
        phone.replace(f"(", "(0", 1)
        if any(phone.startswith(f"({p})") for p in prefix_with_bug)
        else phone
    )
    # xətalı nömrənin düzəldilməsi
    phone = phone.replace("(00", "(0")
    # bug fix: 90 ilə başlayırsa (0 ilə başlamalıdır
    phone = phone.replace("90", "(0", 1) if phone.startswith("90") else phone
    # boşluqlar təmizlənir
    phone = phone.replace(" ", "")

    # əgər mörtərizə açılıb bağlanmayıb errprıi nömrələrə əlavə edilir
    if (phone.count(")") + phone.count("(")) == 1:
        my_except.append(phone)
    
    # nömrə 70,77 ilə başlayırsa 0 əlavə edirik 
    # nəticə 070, 077
    phone = "0" + phone if any(phone.startswith(p) for p in prefix_with_bug) else phone

    # nömrə daxilində bu kimi kombinasiyalar (050)(055) var isə
    # sağdakı prefix saxlanılır 
    # məs (050)(055)703335611
    # nəticə (050)703335611
    for item in combination_texts:
        if item in phone:
            phone = phone.replace(item, item[:5])

    # məs (050)51)703335611
    # nəticə (050)703335611
    for item in combination_texts_2:
        if item in phone:
            phone = phone.replace(item, item[:5])

    # məs 050-051703335611
    # nəticə 050703335611
    for item in combination_texts_3:
        if item in phone:
            phone = phone.replace(item, item[:3])

    # boşluqları təmizləyirik
    phone_numbers = phone.split()
    if not phone_numbers:
        return phone_numbers

    # nömrənin içindən rəqəm olmayanları təmizləyirik
    
    # phone_numbers listesində rəqəm olmayan bir hissə olup olmadığını kontrol edirik
    contains_non_digit_part = any(not part.isdigit() and not contains_digit(part) for part in phone_numbers)
    
    if contains_non_digit_part:
        # əgər rəqəm olmayan bir nüans varsa birinci parçanı seçirik
        phone = phone_numbers[0]
    else:
        # əks təqdirdə, listenin son elementini seçirik
        phone = phone_numbers[-1]

    # rəqəmləri birleşdir
    digits = "".join(filter(str.isdigit, phone))

    
    # İlk sıfırı sil ve uyğun prefix`i əlavə et
    if digits.startswith("0"):
        digits = "994" + digits[1:]

    return digits




def clean_and_format_numbers(phone_list):
    """Bu funksiya verilən telefon nömrələrini bir bir standartlaşdıraraq sms göndərmək üçün uyğun formata çevirir.
    Əgər bu standartlaşdırma mümkün olmazsa həmin hissəni boş olaraq qaytaracaqdır. 
    Standart forma bu cürür:  994<prefix><telefon nömrəsi> məs: 994703335611
    

    Args:
        phone_list (list): Billing sistemində əlaqə nömrəsi bölməsinə qeyd olunmuş telefon nömrələri 

    Returns:
        list: Daxil olan nömrələrin formatlı halı
    """
    
    formatted_phones = [] # təmizlənmiş və formatlanmış nömrələri bu siyahıya əlavə edəcəyik
    prefixs = ["050", "051", "055", "070", "077", "099", "010"] # Azərbaycandakı operator prefixləri
    prefix_with_bug = ["50", "51", "55", "70", "77", "99", "10"] # prefixlərin 0 olmadan yazıldığı hal
    formatted_phones_json = {} #köhnə nörmə : yeni formatlanmış və təmizlənmiş nömrə 
    my_except = [] # xətalı olaraq qəbul etdiyim nüanslar

    # billingdə bir çox nömrə prefixlərin kombinasiyalı halı ilə yazılmışdır 
    # məs: (050)(055)703335611
    # o səbəbdən bunları detect eləmək üçün bu tipdəki bütün kombinasiyaları yığırıq
    combination_texts = [f"({p1})({p2})" for p1 in prefixs for p2 in prefixs] 

    # bəzi nömrələr isə bu cür yazılmışdır
    # məs: (050)55)703335611 
    # bu tipdəki bütün kombinasiyaları yığırıq 
    combination_texts_2 = [
        f"(0{p1}){p2})" for p1 in prefix_with_bug for p2 in prefix_with_bug
    ]
    # bəzi fərqli nüanslardan biri: 050-055 703335611
    combination_texts_3 = [f"{p1}-{p2}" for p1 in prefixs for p2 in prefixs]
    
    # nömrələrin başlamalı olduğu #* STANDARTLAR bunlardır
    # məx: 99470, 99477, 99499, 99410
    must_start_prefixes = [f"994{prefix}" for prefix in prefix_with_bug]

    
    #! diqqət, hazır ol, başla!
    # hər bir nömrə üçün əməliyyata başlayırıq. 
    for phone in phone_list:
      
        # Əgər nömrə STANDARTA uyursa nömrəni formatlanmış nömrələrin olduğu listə əlavə edirik
        if any([phone.startswith(prefix) for prefix in must_start_prefixes]):
            formatted_phones.append(phone)
            continue

        # nömrənin ilk halını itirməmək üçün qeyd alırıq
        first_phone = phone

        
        #* filter 1
        # bəzən biling`in nömrə sütununda 2 nömrə `;` vasitəsi ilə bir-birindən ayrılmış halda yazılır
        # məs: 0703335611;0773335612 
        # nəticə: 0773335612 
        phone = (
            phone.split(";")[1] # bu zaman ikinci nömrə üzərindən əməliyyata davam edirik 
            if len(phone.split(";")) > 1 and len(phone.split(";")[1].strip()) > 1 # burada yoxlayırıq ki ikinci nömrə mövcuddurmu və boşluqdan ibarət deyilmi
            else phone.split(";")[0] # əgər ikinci nömrə mövcud olmasa, yəni nömrə ; ilə ayrılmış şəkildə yazılmayıbsa nömrənin özü ilə davam edirik
        )
        
        #* 'filter 1' ilə eyni, lakin bu dəfə ayrıcımız: ',' ile ayrılmışdır
        # məs: 0703335611,0773335612 
        # nəticə: 0773335612 
        phone = (
            phone.split(",")[1]
            if len(phone.split(",")) > 1 and len(phone.split(",")[1].strip()) > 1
            else phone.split(",")[0]
        )

        #* filter 1 ilə eyni, lakin bu dəfə nömrələr bir birindən boşluq vasitəsi ilə ayrılır 
        # məs: 0703335611 0773335612 
        # nəticə 0773335612
        phone = (
            "0" + phone.split("  0")[1]
            if len(phone.split("  0")) > 1
            else phone.split(",")[0]
        )

        #* filter 1 ilə eyni, lakin bu dəfə nömrələr bir birindən boşluq və `(` vasitəsi ilə ayrılır 
        # məs: 0703335611 (0773335612) 
        # nəticə (0773335612)
        phone = (
            "(0" + phone.split(" (0")[1]
            if len(phone.split(" (0")) > 1
            else phone.split(",")[0]
        )

        # cüt nömrələri təmizlədikdən və birini seçdikdən seçilmiş nömrənin təmizləyir və formatlayırıq
        # nəticə: 994<prefix><telefon nömrəsi> halında olmalıdır 
        # məs: 99070335612 
        digits = clean_phone_procedure(
            phone,
            combination_texts,
            combination_texts_2,
            combination_texts_3,
            my_except,
            prefix_with_bug,
        )
        if not digits:
            continue


        # Nəticə 12 mərtəbəli olmalıdır
        if len(digits) == 12:
            formatted_phones.append(digits)
        
        # əgər 12 mərtəbəbən çoxdursa yenidən baxmaq üçün ":check" textini əlavə edirik
        elif len(digits) > 12:
            formatted_phones.append(digits[:12])
            digits = digits[:12] + " :check"

        else:
            # əgər formatlamadan sonra nəticə uğursuz olarsa yəni alınan nəticə 12 mərtəbədən dən az olarsa 
            # bu dəfə  #* filter 1 prosedurunu yenidən başladırıq. Lakin bu dəfə ikinci nömrəni yox ilk nömrə üzərindən əməliyyata davam edirik 
            # split edib ilk nömrəni götürürük
            # təbii ki ilkin olaraq bu sözlərin olub olmasığını yoxlayırıq və nömrənin ilk halı üzərində işləyirik
            if "," in first_phone or ";" in first_phone:
                phone = first_phone.split(";")[0].split(",")[0]
                
                # nömrəni yenidən təmizləmə və formatlama prosesinə göndəririk 
                digits = clean_phone_procedure(
                    phone,
                    combination_texts,
                    combination_texts_2,
                    combination_texts_3,
                    my_except,
                    prefix_with_bug,
                )
                # əgər nəticə uğursuzdursa pas keçirik
                if not digits:
                    continue
                
                # nəticə 12 mərtəbəlidirsə uğurlu olaraq qeydi edirik
                if len(digits) == 12:
                    formatted_phones.append(digits)

            
                # əgər 12 mərtəbəbən çoxdursa yenidən baxmaq üçün ":check" textini əlavə edirik
                elif len(digits) > 12:
                    formatted_phones.append(digits[:12])
                    digits = digits[:12] + " :check"

                # yox əgər 12 rəqəmdən azdırsa artıq xətalı olaraq qeyd edirik. Buradan sonra artıq bir ümüdimiz yoxdur
                else:
                    digits = digits + " :Hatali veya Eksik Numara"
            
            # problemli olaraq qeyd edirik
            else:
                digits = digits + " :Hatali veya Eksik Numara"

        
        # əgər nömrə daxilində bu simvollar varsa və standart qaydaya uyğun olaraq başlayırsa, split edib ilk sözü götürüb onun üzərindən proseduru yenidən başladıdırıq.
        if ("," in first_phone or ";" in first_phone) and not any(
            [phone.startswith(prefix) for prefix in must_start_prefixes]
        ):
            # split edib ilk hissəni götürürük
            phone = first_phone.split(";")[0].split(",")[0]
            
            # nömrəni yenidən təmizləmə və formatlama prosesinə göndəririk 
            digits = clean_phone_procedure(
                phone,
                combination_texts,
                combination_texts_2,
                combination_texts_3,
                my_except,
                prefix_with_bug,
            )
            # nəticə uğursuzdursa öas keçirik
            if not digits:
                continue
            
            # nəticə 12 mərtəbəlidirsə uğurlu olaraq qeydi edirik
            if len(digits) == 12:
                formatted_phones.append(digits)

            # əgər 12 mərtəbəbən çoxdursa yenidən baxmaq üçün ":check" textini əlavə edirik
            elif len(digits) > 12:
                formatted_phones.append(digits[:12])
                digits = digits[:12] + " :check"

            # yox əgər 12 rəqəmdən azdırsa artıq xətalı olaraq qeyd edirik. Buradan sonra artıq bir ümüdimiz yoxdur
            else:
                digits = digits + " :Hatali veya Eksik Numara"

        # və bütün prosesdən sonra köhnə nömrənin qarşısında yenisini qeyd edirrik  
        formatted_phones_json[first_phone] = digits

        #* dövr bitdi
        
   

    # qeyri standart nömrələrin siyahısı
    none_standart_phones = [
        phone
        for phone in formatted_phones
        if not any([phone.startswith(prefix) for prefix in must_start_prefixes])
    ]
    
    # bütün təmiz nömrələrin siyahısı 
    last_result_phones = [
        phone for phone in formatted_phones if phone not in none_standart_phones
    ]
    
    # təmiz və standart nömrələri return edirik 
    return last_result_phones


# text = "Bu bir test"
# send_sms(994703335611, text, sender="Telecom Inv", unicode="false")



def create_folder(full_folder_name):
    """Qovluq yaratmaq üçün istifadə olunur. Qovluqlar `Documents` qovluğunun daxilində yaradılır.
    Əgər qovluğun yolu /qovluq1/qovluq2/qovluq3 olaraq verilibsə bu ardıcıllıqla da qovluqlar iç içə yaradılır.

    Args:
        full_folder_name (str): qovluğun yolu

    Returns:
        folder_name (str): Qovluğun Documents daxilindəki bütün yolu.
    """

    folder_name = "Documents"
    folders = full_folder_name.split("/")
    # Əgər qovluq yolunda `Documents` bildirilibsə onu nəzərə almırıq. Çünki zatən belə bir qovluq mövcuddur.
    if folders[0] == folder_name:
        folders = folders[1:]
    # İç içə qovluqların yaradılması
    for item in folders:
        folder_name = folder_name + "/" + item
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    return folder_name


def write_to_text(file_name: str, text: str, folder_name: str, add_now_time=False):
    """Text faylı yaratmaq üçün istifadə olunur.
        Text faylları Documents/Logs/Text_Files/ qovluğunun daxilində yarıdılır
    Args:
        file_name (str): Faylın adı
        text (str): Daxilindəki yazı
        folder_name (str): Faylın yolu. yazmaq istədiyimiz qovluğun adı
        add_now_time (bool, optional): Faylın sonuna tarix əlavə edilsinmi? Defaults to False.
    """
    folder_name = "Documents/Logs/Text_Files/" + folder_name
    folder_name = create_folder(folder_name)
    if add_now_time:
        file_name = (
            f"{folder_name}/{file_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
        )
    else:
        file_name = f"{folder_name}/{file_name}.txt"

    if not os.path.isfile(file_name):
        with open(file_name, "w") as file:
            file.writelines(text)
            file.close()
            
            # custom_print(f"The text was successfully written to {file_name} file.")

    else:
        with open(file_name, "a") as file:
            file.writelines("\n\n")
            file.writelines(text)
            file.close()
        # custom_print(f"The text was successfully appended to {file_name} file.")
