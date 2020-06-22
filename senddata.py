import RPi.GPIO as GPIO
import time
import MySQLdb
from PIL import Image
import glob
import os
import base64
GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.IN) #PIR
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT) #BUzzer

count = 1

db = MySQLdb.connect("localhost","suicide","suicide","suicide_db" ) #this line connects database
cursor = db.cursor()

try:
    time.sleep(2) # to stabilize sensor
    while True:
        print(str(GPIO.input(23)))
        if GPIO.input(23):
            check_person = ""
            list_of_files = glob.glob('Images/*') # * means all if need specific format then *.csv
            count = max(list_of_files, key=os.path.getctime)
            with open(count, "rb") as f:
                photo = f.read()
                check_person = os.path.basename(f.name)
            
            if('ignore' not in check_person):
                GPIO.output(24, True)
                GPIO.output(25, True)
                time.sleep(0.5) #Buzzer turns on for 0.5 sec
                print("Motion Detected...")
                
                sql = "insert into data (pic,turnoff,android)VALUES(%s, %s, %s)"
                args = (photo, 0,0)
                cursor.execute(sql, args)
                db.commit()
                sql = "SELECT * FROM data ORDER BY id DESC LIMIT 1"
                cursor.execute(sql)
                myresult = cursor.fetchone()
                print(myresult[0])
                db.commit()
                while(True):
                    sql = "SELECT * FROM data WHERE id ="+str(myresult[0])+"  ORDER BY id DESC LIMIT 1"
                    cursor.execute(sql)
                    resultnew = cursor.fetchone()
                    if(resultnew[2] == 1):
                        GPIO.output(24, False)
                        GPIO.output(25, False)
                    if(resultnew[3] == 1):
                        print('inner loop')
                        break
                    print(resultnew[3])
                    db.commit()
                    time.sleep(2)
                    
            else:
                GPIO.output(24, False)
                GPIO.output(25, False)
                
                time.sleep(2) #to avoid multiple detection
        time.sleep(0.1) #loop delay, should be less than detection delay

except Exception  as e:
    GPIO.cleanup()
    print(e)
