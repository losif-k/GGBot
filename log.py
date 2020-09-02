from datetime import datetime


def writelog(txt):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    with open('log.txt', 'a', encoding='UTF-8') as log:
        log.write(f"[{date_time}] {txt}\n")
        log.close()
