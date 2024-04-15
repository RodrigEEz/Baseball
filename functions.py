import sqlite3
import numpy as np
import time
import os

def calculate_moreyz(a,b,c):
    """Morey-z formula to determine the probability of an outcome when two opponents face, given their success rate"""

    first_subterm = (a-c)/np.sqrt(c*(1-c))
    second_subterm = (b-c)/np.sqrt(c*(1-c))
    moreyz = (((first_subterm+second_subterm)/np.sqrt(2))*np.sqrt(c*(1-c)))+c

    return moreyz


def read_average_stats():
    """Queries average stats from the database"""
    
    value_select = """
                    SELECT 
	                    *
                    FROM 
	                    AVERAGE_STATS
                    """
    
    name_select = """
                    SELECT 
                        NAME
                    FROM 
                        PRAGMA_TABLE_INFO('AVERAGE_STATS')
                """
    
    values = execute_select(value_select)[0]
    names = execute_select(name_select)

    names = [name[0] for name in names]

    average_stats = dict(zip(names,values))

    return average_stats


def execute_select(select, *args):
    """Queries the database with the select provided"""
    
    data = ''

    con = sqlite3.connect("database.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()

    if args == ():
        cur.execute(select)
        data = cur.fetchall()     
    else:   
        for arg in args:
            cur.execute(select, (str(arg),))
            data = cur.fetchall()

    return data


def code_result(result):
    """Codes the hit result"""

    match result:
        case 1:
            return '1B'
        case 2:
            return '2B'
        case 3:
            return '3B'
        case 4:
            return 'HR'

def insert_data(select):
    """Updates database records"""

    con = sqlite3.connect("database.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()

    cur.execute(select)  

    con.commit()
    con.close()

def update_average_stats():

    calculation_select = """
                            SELECT 
                                SUM(PA) PA,
                                SUM(H) H,
                                SUM("1B") "1B",
                                SUM("2B") "2B",
                                SUM("3B") "3B",
                                SUM(HR) HR,
                                SUM(SO) SO,
                                SUM("OUT") "OUT",
                                SUM(BB) BB
                            FROM
                                BATTER_STATS
                        """
    
    calculation = execute_select(calculation_select)[0]

    update_select  = """
                        UPDATE AVERAGE_STATS
                            SET PA = {},
                              H = {},
                             "1B" = {},
                             "2B" = {},
                             "3B" = {},
                             HR = {},
                             SO = {},
                             OUT = {},
                             BB = {}
                        WHERE ID = 1;
                    """.format(calculation[0], calculation[1], calculation[2], calculation[3], calculation[4], calculation[5], 
                    calculation[6], calculation[7], calculation[8])

    insert_data(update_select)