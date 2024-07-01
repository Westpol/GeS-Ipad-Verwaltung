from datetime import datetime

date_string = "27.06.2023"
date_format = "%d.%m.%Y"

# Parse das Datum
date_object = datetime.strptime(date_string, date_format)

# Erhalte den Unix-Zeitstempel
unix_timestamp = int(date_object.timestamp())

print(unix_timestamp)

date_object = datetime.utcfromtimestamp(unix_timestamp)

# Formatieren und drucken des lesbareren Datums im gewünschten Format
formatted_date = date_object.strftime("%d.%m.%Y")
print(formatted_date)