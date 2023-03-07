import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time
import numpy as np
import os
import requests
from datetime import datetime

# Set URL server untuk mengirim data
url = "http://coba/api/online"

def send_data_to_server(filename, code, accuracy_percentage):
    # Validate accuracy
    if accuracy_percentage < 0 or accuracy_percentage > 100:
        print("Invalid accuracy percentage!")
        return

    imgFile = open(filename, "rb")
    dataJson = {
        "machineName": "m23",
        "result": code,
        "accuracy": accuracy_percentage
    }
    fileImage = {
        "Image": imgFile
    }
    res_server = requests.post(url, files=fileImage, data=dataJson)
    print(res_server.content)

    # Close image file
    imgFile.close()


def BarcodeReader():
    cap = cv2.VideoCapture(0)
    detek = np.zeros((10,))
    prev_frame_time = 0
    hasil = 0
    
    # Kamus kode unik ke jenis kartu remi
    code_to_card = {
        # ===============================Spades===============================
		'314': '2 of spades',
        '189': '3 of spades',
		'99': '4 of spades',
		'156': '5 of spades',
		'123': '6 of spades',
        '347': '7 of spades',
		'11': '8 of spades',
		'404': '9 of spades',
        '235': '10 of spades',
		'167': 'Jack of spades',
		'415': 'Queen of spades',
		'279': 'king of spades',
        '49D': 'AS of spades',
		# ===============================Hearts===============================
		'224': '2 of hearts',
		'134': '3 of hearts',
        '257': '4 of hearts',
        '112': '5 of hearts',
		'516': '6 of hearts',
		'77': '7 of hearts',
        '29B': '8 of hearts',
		'33': '10 of hearts',
        '101': '9 of hearts',
		'358': 'jack of hearts',
		'336': 'queen of hearts',
		'268': 'king of hearts',
		'448': 'AS of hearts',
		# ===============================Diamonds===============================
		'325': '2 of diamonds',
		'178': '3 of diamonds',
		'22': '4 of diamonds',
		'55': '5 of diamonds',
        '527': '6 of diamonds',
		'303': '7 of diamonds',
        '19A': '8 of diamonds',
		'48C': '9 of diamonds',
		'46A': '10 of diamonds',
		'213': 'jack of diamonds',
		'369': 'queen of diamonds',
		'39C': 'king of diamonds',
		'44': 'AS of diamonds',
		# ===============================Clubs===============================
		'66':'2 of clubs',
		'38B':'3 of clubs',
        '202': '4 of clubs',
		'426':'5 of clubs',
		'246':'6 of clubs',
		'145':'7 of clubs',
		'88':'8 of clubs',
        '37A': '9 of clubs',
		'459':'10 of clubs',
		'437':'jack of clubs',
		'47B':'queen of clubs',
		'28A':'king of clubs',
		'505':'AS of clubs'
    }
    
    # Initialize counters and image capture flag
    unique_codes = []
    successful_reads = 0
    unsuccessful_reads = 0
    img_count = 0
    save_image = False

    # Define default value for code
    code = ''

    while True:
        _, img = cap.read()
        detectedBarcodes = decode(img, symbols=[ZBarSymbol.CODE39])

        if detectedBarcodes:
            for barcode in detectedBarcodes:
                # Print the barcode data
                code = str(barcode.data)[2:-1] # mengambil kode unik dari data barcode
                if code in code_to_card:
                    card_type = code_to_card[code]
                    # Increment successful reads
                    successful_reads += 1
                else:
                    # Increment unsuccessful reads
                    unsuccessful_reads += 1

                # Add barcode code to list
                unique_codes.append(code)

            # Check if 30 unique barcodes have been detected
            if len(unique_codes) == 30:
                # Reset unique_codes list
                unique_codes = []

                # Check if all codes detected are valid
                all_codes_valid = all(code in code_to_card for code in unique_codes)

                # If all codes are valid, calculate accuracy percentage
                if all_codes_valid:
                    accuracy = successful_reads / (successful_reads + unsuccessful_reads)
                    accuracy_percentage = accuracy * 100
                else:
                    accuracy_percentage = "Invalid"
                    
                # Save image if required
                if save_image:
                    # Apply median blur to image before saving
                    img = cv2.medianBlur(img, 7)

                    # Create folder if it doesn't exist
                    if not os.path.exists("screenshoot"):
                        os.makedirs("screenshoot")

                    # Buat nama file dengan timestamp
                    dt = datetime.now()
                    ts = datetime.timestamp(dt)
                    filename = f"screenshoot/captured_image_{int(ts)}.jpg"

                    cv2.imwrite(filename, img)
                    print(f"Image {filename} saved!")

                    # Kirim data ke server
                    send_data_to_server(filename, code, accuracy_percentage)

                    # Reset successful and unsuccessful read counters
                    successful_reads = 0
                    unsuccessful_reads = 0

                save_image = True # Tambahkan baris ini


                save_image = True # Tambahkan baris ini
                
        else:
            # Add text to image indicating barcode not detected
            cv2.putText(img, "", (img.shape[1]-420, img.shape[0]-50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), thickness=2)

        # Show only the image without barcode detection
        resized_img = cv2.resize(img, (1980, 1180))
        cv2.imshow("Simpan Gambar", resized_img)
                
        # Show barcode detection only if detected
        card_img = img.copy()
        cv2.putText(card_img, code_to_card.get(code), (card_img.shape[1]-300, card_img.shape[0]-50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), thickness=2)
        resized_card_img = cv2.resize(card_img, (640, 480))
        cv2.imshow('Detected Kartu', resized_card_img)
    
    # Show FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        cv2.putText(img, "FPS "+"{:.2f}".format(fps), (20,50),cv2.FONT_HERSHEY_COMPLEX, 0.8,(0,255,0),2)
    
        key = cv2.waitKey(1)
        if key == 27:
            break    
    cv2.destroyAllWindows()

if __name__ == "__main__":
	BarcodeReader() 


