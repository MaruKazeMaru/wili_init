#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import os
import argparse
import sqlite3

def main(args):
    if os.path.exists(args.dbpath):
        return

    conn = sqlite3.connect(args.dbpath)
    cur = conn.cursor()

    cur.execute('PRAGMA foreign_keys=true')
    cur.execute( \
        'CREATE TABLE motion(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT' \
        ')' \
    )
    cur.execute( \
        'CREATE TABLE tr_prob(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'from_motion INTEGER,' \
        'to_motion INTEGER,' \
        'elem REAL,' \
        'FOREIGN KEY(from_motion) REFERENCES motion(id),' \
        'FOREIGN KEY(to_motion) REFERENCES motion(id)' \
        ')' \
    )
    for i in range(args.motionnum):
        cur.execute('INSERT INTO motion(id) values(%d)' % i)
    init_prob = 1.0 / float(args.motionnum)
    for i in range(args.motionnum):
        for j in range(args.motionnum):
            cur.execute('INSERT INTO tr_prob(from_motion, to_motion, elem) values(%d, %d, %f)' % (i, j, init_prob))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WILI db initializer")
    parser.add_argument("motionnum", help="int. number of motion", type=int)
    parser.add_argument("dbpath", help="str. path of database(SQLite)", type=str)
    args = parser.parse_args()
    main(args)
