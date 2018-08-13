The file seeed_grove_fingerprint_sensor.py contains a library making the Seeed Grove Fingerprint Sensor (or ZhianTec ZFM-20) usable on a Raspberry Pi with all functions documented in the manual. 
There is no checking for complete or consistent data. There is no error handling within the library. This has to be done when using the library.

The file door.py is a prototype/ test for an acces control using the library and the sensor named above.

The files fingerprint_data.py and fingerprint_object.py are used for saving generated characteristics in a simple text file.

For external use, the functionality and security of the code in this files must be determined by the user. There is no warranty for correctness and completeness. 
