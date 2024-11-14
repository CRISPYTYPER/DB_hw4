import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import is_valid_genre
from helpers.utils import print_command_to_file
from helpers.utils import make_csv
from helpers.utils import is_valid_pro

def display_info(search_type, search_value):
    try:
        cur = conn.cursor()

        if search_type == 'id' :
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            pt.major_work,
            STRING_AGG(DISTINCT o.ocu_name, ', ') AS profession
            FROM participant pt
            LEFT OUTER JOIN profession p ON pt.p_id = p.p_id
            LEFT OUTER JOIN occupation o ON p.ocu_id = o.ocu_id
            WHERE pt.p_id = %(id)s
            GROUP BY pt.p_id, pt.major_work
            ORDER BY pt.p_id ASC;
            """
            cur.execute(sql, {"id": search_value})

        elif search_type == 'name':
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            pt.major_work,
            STRING_AGG(DISTINCT o.ocu_name, ', ') AS profession
            FROM participant pt
            LEFT OUTER JOIN profession p ON pt.p_id = p.p_id
            LEFT OUTER JOIN occupation o ON p.ocu_id = o.ocu_id
            WHERE pt.p_name ILIKE %(name)s
            GROUP BY pt.p_id, pt.major_work
            ORDER BY pt.p_id ASC;
            """
            cur.execute(sql, {"name": search_value})

        elif search_type == 'profession':
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            pt.major_work,
            STRING_AGG(DISTINCT o.ocu_name, ', ') AS profession
            FROM participant pt
            LEFT OUTER JOIN profession p ON pt.p_id = p.p_id
            LEFT OUTER JOIN occupation o ON p.ocu_id = o.ocu_id
            WHERE pt.p_id IN (
                SELECT pt.p_id
                FROM participant pt
                LEFT OUTER JOIN profession p ON pt.p_id = p.p_id
                LEFT OUTER JOIN occupation o ON p.ocu_id = o.ocu_id
                WHERE o.ocu_name ILIKE %(profession)s
            )
            GROUP BY pt.p_id, pt.major_work
            ORDER BY pt.p_id ASC;
            """
            cur.execute(sql, {"profession": search_value})

        elif search_type == 'all' :
            sql = """
            SELECT
            pt.p_id,
            pt.p_name,
            pt.major_work,
            STRING_AGG(DISTINCT o.ocu_name, ', ') AS profession
            FROM participant pt
            LEFT OUTER JOIN profession p ON pt.p_id = p.p_id
            LEFT OUTER JOIN occupation o ON p.ocu_id = o.ocu_id
            GROUP BY pt.p_id, pt.major_work
            ORDER BY pt.p_id ASC
            LIMIT %(all)s;
            """
            cur.execute(sql, {"all": search_value})

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
            # print_rows_to_file(column_names, rows)
            # make_csv(column_names, rows)
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
        if args.all:
            display_info('all', args.all)
        elif args.id:
            display_info('id',args.id)
        elif args.name:
            display_info('name', args.name)
        elif args.profession:
            if not is_valid_pro(args.profession) :
                print(f"Error: {args.profession} is not valid profession.")
            else :
                display_info('profession', args.profession)
    
    else :
        print("Error: query command error.")


if __name__ == "__main__":
    #
    # print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-a(all) / -i(p_id) / -n(p_name) / -pr(profession name)] [value]
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display target participant info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    group_info.add_argument('-a', dest='all', type=int, help='display rows with top [value]')
    group_info.add_argument('-i', dest='id', type=int, help='Search by p_id')
    group_info.add_argument('-n', dest='name', type=str, help='Search by p_name')
    group_info.add_argument('-pr', dest='profession', type=str, help='Search by profession name')

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
