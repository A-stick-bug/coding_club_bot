"""
WARNING: DB INFO GETS OVERRIDE
Save the information in the `userdata` folder to the database
"""

import os
from user_data import UserData

USERDATA_FOLDER = "userdata"

if __name__ == '__main__':
    users = []
    for f in os.listdir(USERDATA_FOLDER):
        if not f.endswith(".txt"):  # only care about user_data info
            continue
        args = []
        with open(USERDATA_FOLDER + "/" + f) as user:
            for i in user.readlines():
                args.append(i.strip())
        args = args[:2] + list(map(int, args[2:]))
        args_ud = UserData(*args)
        args_ud.save_to_db()
