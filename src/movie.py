import time
import argparse
from helpers.connection import conn
from helpers.utils import print_rows
from helpers.utils import print_rows_to_file
from helpers.utils import is_valid_genre
from helpers.utils import print_command_to_file
from helpers.utils import make_csv

def display_info(search_type, search_value):
    try:
        cur = conn.cursor()

        cur.execute("SET search_path to s_2019040591")

        if search_type == 'm_id':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.m_id = %(m_id)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"m_id": search_value})
        elif search_type == 'm_name':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.m_name ILIKE %(m_name)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"m_name": search_value})
        elif search_type == 'genre':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.genre = %(genre)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"genre": search_value})
        elif search_type == 'type':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.type = %(type)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"type": search_value})
        elif search_type == 'start_year':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.start_year = %(start_year)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"start_year": search_value})
        elif search_type == 'end_year':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.end_year = %(end_year)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"end_year": search_value})
        elif search_type == 'is_adult':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.is_adult = %(is_adult)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"is_adult": search_value})
        elif search_type == 'rating':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            WHERE m.rating = %(rating)s
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
            ORDER BY m.m_id ASC;
            """
            cur.execute(sql, {"rating": search_value})
        elif search_type == 'all':
            sql = """
            SELECT 
            m.m_id,
            m.m_name,
            m.genre,
            m.type,
            m.start_year,
            m.end_year,
            m.is_adult,
            m.rating AS imdb_rating,
            ((COALESCE(m.rating * m.votes, 0) + COALESCE(SUM(ct.rating), 0)) / 
            NULLIF(m.votes + COALESCE(COUNT(ct.c_id), 0), 0)) AS recalculated_avg_rating
            FROM movie m
            LEFT OUTER JOIN comment_to ct ON m.m_id = ct.m_id
            GROUP BY m.m_id, m.m_name, m.genre, m.type, m.start_year, m.end_year, m.is_adult, m.rating, m.votes
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
    # TODO


if __name__ == "__main__":
    #
    #print_command_to_file()
    #
    start = time.time()
    parser = argparse.ArgumentParser(description = """
    how to use
    1-1. info [-a(all) / -i(m_id) / -n(m_name) / -g(genre)] [value]
    1-2. info [-sy(start_year) / -ey(end_year) / -ad(is_adult) / -r(rating)] [value]
    2. ...
    3. ...
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, ...]')

    #info
    parser_info = subparsers.add_parser('info', help='Display target movie info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    # TODO


    
    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
