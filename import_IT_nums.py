import csv
import json
import time

if __name__ == "__main__":
    with open("Ipad-Excel-Leihe/24-06-10_Leihvertrag iPad und Anmeldung Stadt- und Landesbibliothek Gerätedaten.csv", "r") as file:
        reader_obj = csv.reader(file)

        dictionary = {"moddate": 1702976491, "opendate": 1704881188, "Ipads": {}}

        for i in list(reader_obj)[1:-1]:

            if str(i[30]) != "nein" and str(i[26]) != "":
                it_num = str(i[26])
                try:
                    device_info = {"deviceInfo": {"version": str(i[28])[0:10], "storage": int(str(i[28])[17:19]), "SNr": str(i[27])}}
                except:
                    device_info = {"deviceInfo": {"version": str(i[28])[0:10], "storage": str(i[28])[17:19], "SNr": str(i[27])}}
                user_info = {"userInfo": {"surname": str(i[3]), "name": str(i[2]), "birth": str(i[4]), "street": str(i[12]), "postcode": str(i[13]), "city": str(i[14]), "lendBegin": "lul", "class": str(i[11]), "subclass": None, "ifdNr": str(i[0])}}
                user_history = {"userHistory": {}}
                repair_history = {"repairHistory": {}}
                additional_infos = {"moddate": time.time(), "status": 0, "comments": str(i[32])}

                updated_dict = {it_num: {}}
                updated_dict[it_num].update(device_info)
                updated_dict[it_num].update(user_info)
                updated_dict[it_num].update(user_history)
                updated_dict[it_num].update(repair_history)
                updated_dict[it_num].update(additional_infos)

                dictionary["Ipads"].update(updated_dict)

        with open("database.json", "w") as dictFile:
            json.dump(dictionary, dictFile, indent=2)
