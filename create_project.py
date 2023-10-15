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

    # CREATE TABLES
    cur.execute('PRAGMA foreign_keys=true')
    cur.execute( \
        'CREATE TABLE motion(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT' \
        ')' \
    )
    cur.execute( \
        'CREATE TABLE init_prob(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'motion INTEGER,' \
        'data REAL,' \
        'FOREIGN KEY(motion) REFERENCES motion(id)' \
        ')' \
    )
    cur.execute( \
        'CREATE TABLE tr_prob(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'from_motion INTEGER,' \
        'to_motion INTEGER,' \
        'data REAL,' \
        'FOREIGN KEY(from_motion) REFERENCES motion(id),' \
        'FOREIGN KEY(to_motion) REFERENCES motion(id)' \
        ')' \
    )
    cur.execute( \
        'CREATE TABLE gaussian(' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'motion INTEGER,' \
        'avr_x REAL,' \
        'avr_y REAL,' \
        'covar_xx REAL,' \
        'covar_xy REAL,' \
        'covar_yy REAL,' \
        'FOREIGN KEY(motion) REFERENCES motion(id)' \
        ')' \
    )

    # INSERT motion
    values = ['(%d)' % i for i in range(motion_num)]
    cur.execute('INSERT INTO motion(id) VALUES' + ','.join(values))

    # INSERT init_prob
    values = [] 
    init_prob = 1.0 / float(motion_num)
    for i in range(motion_num):
        values.append('(%d, %f)' % (i, init_prob))
    cur.execute('INSERT INTO init_prob(motion, data) VALUES' + ','.join(values))

    # INSERT tr_prob
    values = [] 
    for i in range(motion_num):
        for j in range(motion_num):
            values.append('(%d, %d, %f)' % (i, j, init_prob))
    cur.execute('INSERT INTO tr_prob(from_motion, to_motion, data) VALUES' + ','.join(values))

    # INSERT gaussian
    values = []
    v = np.array([1.0, 0.0])
    ang = 2.0 * np.pi / float(motion_num)
    c = np.cos(ang)
    s = np.sin(ang)
    R = np.array([[c,-s], [s,c]])
    for i in range(motion_num):
        values.append('(%d, %f, %f, %f, %f, %f)' % (i, 2.0 * v[0], 1.0 * v[1], 1.0, 0.0, 1.0))
        v = R @ v
    sql = \
    'INSERT INTO gaussian' \
    ' (motion, avr_x, avr_y, covar_xx, covar_xy, covar_yy)' \
    ' VALUES'
    cur.execute(sql + ','.join(values))

    conn.commit()
    conn.close()


def main(args):
    db_path = '/var/wili/db.sqlite3'

    if os.path.exists(db_path):
        os.remove(db_path)
    with open(db_path, 'x'):
        pass
    create_db(db_path, args.motionnum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WILI db initializer")
    parser.add_argument("motionnum", help="int. number of motion", type=int)
    args = parser.parse_args()
    main(args)
