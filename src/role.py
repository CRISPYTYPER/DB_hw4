import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import print_command_to_file
from helpers.utils import make_csv


def display_info(search_type, search_value, search_role):
    try:
        cur = conn.cursor()

        cur.execute("SET search_path to s_2019040591")

        if search_type == 'm_id' :
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            STRING_AGG(DISTINCT pe.role, ', ') AS role,
            STRING_AGG(DISTINCT pe.casting, ', ') AS casting
            FROM movie m 
            LEFT OUTER JOIN participate pe ON m.m_id = pe.m_id
            LEFT OUTER JOIN participant pt ON pt.p_id = pe.p_id
            WHERE m.m_id = %(m_id)s AND pe.role = %(role)s
            GROUP BY m.m_id, pt.p_id
            ORDER BY pt.p_id ASC;
            """
            cur.execute(sql, {"m_id": search_value, "role": search_role})

        elif search_type == 'all' :
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            STRING_AGG(DISTINCT pe.role, ', ') AS role,
            m.m_name,
            STRING_AGG(DISTINCT pe.casting, ', ') AS casting
            FROM movie m 
            LEFT OUTER JOIN participate pe ON m.m_id = pe.m_id
            LEFT OUTER JOIN participant pt ON pt.p_id = pe.p_id
            WHERE pe.role = %(role)s
            GROUP BY m.m_id, pt.p_id
            ORDER BY pt.p_id ASC
            LIMIT %(row_num)s;
            """
            cur.execute(sql, {"row_num": search_value, "role": search_role})

        else :
            print("can't search by", search_type)
            return False

        rows = cur.fetchall()
        if not rows:
            print("No results found.")
            return False
        else:
            column_names = [desc[0] for desc in cur.description]
            #
            print_rows_to_file(column_names, rows)
            make_csv(column_names, rows)
            #
            print_rows(column_names, rows)
            return True

    except Exception as err:
        print(err)

    finally:
        cur.close()
    # end
    pass
def main(args):
    if args.command == "info":
        if args.m_id:
            m_id, role = args.m_id
            display_info('m_id', int(m_id), role)
        elif args.all:
            num_of_rows, role = args.all
            display_info('all', int(num_of_rows), role)
    else:
        print("Error: query command error.")

if __name__ == "__main__":
    #
    print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-a(all) / -o(one)] value role
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display participant associated to genre info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    group_info.add_argument('-a', dest='all', nargs=2, type=str, help='display rows with top [value] with given role')
    group_info.add_argument('-i', dest='m_id', nargs=2, type=str, help='Search by m_id and role')

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
