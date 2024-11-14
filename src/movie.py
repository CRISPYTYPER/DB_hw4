import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import is_valid_genre
from helpers.utils import print_command_to_file
from helpers.utils import make_csv

def display_info(search_type, search_value):
    def get_common_movie_query():
        return """
        SELECT 
        m.m_id,
        m.m_name,
        m.m_type,
        m.start_year,
        m.end_year,
        m.is_adult,
        m.runtimes,
        m.m_rating AS imdb_rating,
        ((COALESCE(m.m_rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
        NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS final_rating,
        STRING_AGG(DISTINCT gr.gr_name, ', ') AS genres
        FROM movie m
        LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
        LEFT OUTER JOIN classify cl ON m.m_id = cl.m_id
        LEFT OUTER JOIN genre gr ON cl.gr_id = gr.gr_id
        """

    try:
        cur = conn.cursor()

        base_sql = get_common_movie_query()

        if search_type == 'm_id':
            sql = base_sql + """
            WHERE m.m_id = %(m_id)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"m_id": search_value})
        elif search_type == 'm_name':
            sql = base_sql + """
            WHERE m.m_name ILIKE %(m_name)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"m_name": search_value})
        elif search_type == 'genre':
            sql = base_sql + """
            WHERE gr.gr_name ILIKE %(genre)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"genre": search_value})
        elif search_type == 'type':
            sql = base_sql + """
            WHERE m.m_type ILIKE %(type)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"type": search_value})
        elif search_type == 'start_year':
            sql = base_sql + """
            WHERE EXTRACT(YEAR FROM m.start_year) >= %(start_year)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"start_year": search_value})
        elif search_type == 'end_year':
            sql = base_sql + """
            WHERE EXTRACT(YEAR FROM m.end_year) >= %(end_year)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"end_year": search_value})
        elif search_type == 'is_adult':
            sql = base_sql + """
            WHERE m.is_adult = %(is_adult)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"is_adult": search_value})
        elif search_type == 'rating':
            sql = base_sql + """
            WHERE m.m_rating >= %(rating)s
            GROUP BY m.m_id
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"rating": search_value})
        elif search_type == 'all':
            sql = base_sql + """
            GROUP BY m.m_id
            ORDER BY m.m_id ASC
            LIMIT %(all)s;
            """
            cur.execute(sql, {"all": search_value})

        else:
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
        if args.m_id:
            display_info('m_id',args.m_id)
        elif args.m_name:
            display_info('m_name', args.m_name)
        elif args.genre:
            if not is_valid_genre(args.genre):
                print(f"Error: '{args.genre}' is not a valid genre.")
            else:
                display_info('genre', args.genre)
        elif args.type:
            display_info('type', args.type)
        elif args.start_year:
            display_info('start_year', args.start_year)
        elif args.end_year:
            display_info('end_year', args.end_year)
        elif args.is_adult:
            display_info('is_adult', args.is_adult)
        elif args.rating:
            display_info('rating', args.rating)
        elif args.all:
            display_info('all', args.all)
    else:
            print("Error: query command error.")

if __name__ == "__main__":
    #
    # print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1-1. info [-a(all) / -i(m_id) / -n(m_name) / -g(genre) / -t(type)] [value]
    1-2. info [-sy(start_year) / -ey(end_year) / -ad(is_adult) / -r(rating)] [value]
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display target movie info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    group_info.add_argument('-i', dest='m_id', type=int, help='Search by m_id')
    group_info.add_argument('-n', dest='m_name', type=str, help='Search by m_name')
    group_info.add_argument('-g', dest='genre', type=str, help='Search by genre (one)')
    group_info.add_argument('-t', dest='type', type=str, help='Search by type')
    group_info.add_argument('-sy', dest='start_year', type=int, help='Search by start_year')
    group_info.add_argument('-ey', dest='end_year', type=int, help='Search by end_year')
    group_info.add_argument('-ad', dest='is_adult', type=str, help='Search by is_adult')
    group_info.add_argument('-r', dest='rating', type=float, help='Search by rating')
    group_info.add_argument('-a', dest='all', type=int, help='display rows with top [value]')


    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
