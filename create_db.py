#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import os
import sys
import argparse
import sqlite3
import numpy as np

def create_db(db_path:str, motion_num:int):
    conn = sqlite3.connect(db_path)
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
    cur.execute( \
        'CREATE TABLE heatmap_user(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'motion INTEGER,' \
        'avr_x REAL,' \
        'avr_y REAL,' \
        'inv_var_xx REAL,' \
        'inv_var_xy REAL,' \
        'inv_var_yy REAL,' \
        'FOREIGN KEY(motion) REFERENCES motion(id)' \
        ')' \
    )

    for i in range(motion_num):
        cur.execute('INSERT INTO motion(id) values(%d)' % i)

    init_prob = 1.0 / float(motion_num)
    for i in range(motion_num):
        for j in range(motion_num):
            cur.execute('INSERT INTO tr_prob(from_motion, to_motion, elem) values(%d, %d, %f)' % (i, j, init_prob))

    v = np.array([1.0, 0.0])
    ang = 2.0 * np.pi / float(motion_num)
    c = np.cos(ang)
    s = np.sin(ang)
    R = np.array([[c,-s], [s,c]])
    for i in range(motion_num):
        cur.execute('INSERT INTO heatmap_user(motion, avr_x, avr_y, inv_var_xx, inv_var_xy, inv_var_yy) values(%d, %f, %f, %f, %f, %f)' % (i, v[0], v[1], 1.0, 0.0, 1.0))
        v = R @ v

    conn.commit()
    conn.close()


def main(args):
    dir_path = '/var/lib/wili/' + args.projectname
    if os.path.exists(dir_path):
        print('%s already exists' % args.projectname, file=sys.stderr)
        exit(1)

    os.mkdir(dir_path)

    db_path = dir_path + '/db.sqlite3'
    with open(db_path, 'x'):
        pass
    create_db(db_path, args.motionnum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WILI db initializer")
    parser.add_argument("motionnum", help="int. number of motion", type=int)
    parser.add_argument("projectname", help="str. name of project", type=str)
    args = parser.parse_args()
    main(args)
