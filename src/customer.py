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

        if search_type == 'id' :
            sql = """
            SELECT 
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_id = %(id)s
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"id": search_value})

        elif search_type == 'name' :
            sql = """
            SELECT
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_name ILIKE %(name)s
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"name": search_value})

        elif search_type == 'genre' :
            sql = """
            SELECT 
                cu.c_id, 
                cu.c_name, 
                cu.email, 
                cu.gender, 
                cu.phone, 
                STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu JOIN prefer p ON cu.c_id = p.c_id JOIN genre gr ON p.gr_id = gr.gr_id
            WHERE cu.c_id IN (
                SELECT cu.c_id
                FROM customer cu
                JOIN prefer p ON cu.c_id = p.c_id
                JOIN genre gr ON p.gr_id = gr.gr_id
                WHERE gr.gr_name = %(genre)s
                )
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC;
            """
            cur.execute(sql, {"genre": search_value})

        elif search_type == 'all' :
            sql = """
            SELECT
            cu.c_id, 
            cu.c_name, 
            cu.email, 
            cu.gender, 
            cu.phone, 
            STRING_AGG(DISTINCT gr.gr_name, ', ') AS preferred_genres
            FROM customer cu 
            JOIN prefer p ON cu.c_id = p.c_id 
            JOIN genre gr ON p.gr_id = gr.gr_id
            GROUP BY cu.c_id, cu.c_name, cu.email, cu.gender, cu.phone
            ORDER BY cu.c_id ASC
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

def insert_customer(id, name, email, pwd, gender, phone, genres) :
    try:
        cur = conn.cursor()

        cur.execute("SET search_path to s_2019040591")

        # Insert into customer table
        sql_customer = """
        INSERT INTO customer (c_id, c_name, email, pwd, gender, phone)
        VALUES (%(id)s, %(name)s, %(email)s, %(pwd)s, %(gender)s, %(phone)s);
        """
        cur.execute(sql_customer, {"id": id, "name": name, "email": email, "pwd": pwd, "gender": gender, "phone": phone})

        # Insert into prefer table for genres
        for genre in genres:
            # Ensure the genre exists in the genre table to avoid foreign key constraint violations
            sql_genre_check = """
            SELECT gr_id FROM genre WHERE gr_name = %(genre)s;
            """
            cur.execute(sql_genre_check, {"genre": genre})
            genre_row = cur.fetchone()
            if not genre_row:
                raise ValueError(f"Genre '{genre}' does not exist in the genre table.")

            sql_prefer = """
            INSERT INTO prefer (c_id, gr_id)
            SELECT %(c_id)s, gr_id FROM genre WHERE gr_name = %(genre)s;
            """
            cur.execute(sql_prefer, {"c_id": id, "genre": genre})

        conn.commit()
        print(f"Customer {name} successfully inserted.")
    except Exception as err:
        conn.rollback()
        print(f"Error while inserting customer: {err}")

    finally:
        display_info('id', id)
        cur.close()

def update_customer(id, target, *values) :
    display_info('id', id)
    try:
        cur = conn.cursor()

        cur.execute("SET search_path to s_2019040591")

        sql_update = None
        # Update customer information based on target field
        if target == 'email':
            sql_update = """
            UPDATE customer
            SET email = %(value)s
            WHERE c_id = %(id)s;
            """
            cur.execute(sql_update, {"id": id, "value": values[0]})
        elif target == 'pwd':
            previous_pwd, new_pwd = values
            # Verify previous password
            sql_verify = """
            SELECT pwd FROM customer WHERE c_id = %(id)s;
            """
            cur.execute(sql_verify, {"id": id})
            result = cur.fetchone()
            if not result or result[0] != previous_pwd:
                raise ValueError("Previous password does not match.")
            sql_update = """
            UPDATE customer
            SET pwd = %(value)s
            WHERE c_id = %(id)s;
            """
            cur.execute(sql_update, {"id": id, "value": new_pwd})
        elif target == 'phone':
            sql_update = """
            UPDATE customer
            SET phone = %(value)s
            WHERE c_id = %(id)s;
            """
            cur.execute(sql_update, {"id": id, "value": values[0]})
        elif target == 'genres':
            # First, delete existing genre preferences for the customer
            sql_delete_genres = """
            DELETE FROM prefer
            WHERE c_id = %(id)s;
            """
            cur.execute(sql_delete_genres, {"id": id})

            # Then, insert new genre preferences
            for genre in value:
                sql_genre_check = """
                SELECT gr_id FROM genre WHERE gr_name = %(genre)s;
                """
                cur.execute(sql_genre_check, {"genre": genre})
                genre_row = cur.fetchone()
                if not genre_row:
                    raise ValueError(f"Genre '{genre}' does not exist in the genre table.")

                sql_insert_genre = """
                INSERT INTO prefer (c_id, gr_id)
                SELECT %(c_id)s, gr_id FROM genre WHERE gr_name = %(genre)s;
                """
                cur.execute(sql_insert_genre, {"c_id": id, "genre": genre})

        else:
            print(f"Error: Invalid target field '{target}' for update.")
            return

        conn.commit()
        print(f"Customer {id} successfully updated.")

    except Exception as err:
        conn.rollback()
        print(f"Error while updating customer: {err}")

    finally:
        display_info('id', id)
        cur.close()

def delete_customer(id) :
    display_info('id', id)
    try:
        cur = conn.cursor()

        cur.execute("SET search_path to s_2019040591")

        # Delete referencing rows in the prefer table
        sql_delete_prefer = """
        DELETE FROM prefer WHERE c_id = %(id)s;
        """
        cur.execute(sql_delete_prefer, {"id": id})

        # Delete customer and associated data
        sql_delete_customer = """
        DELETE FROM customer WHERE c_id = %(id)s;
        """
        cur.execute(sql_delete_customer, {"id": id})

        conn.commit()
        print(f"Customer {id} successfully deleted.")
    except Exception as err:
        conn.rollback()
        print(f"Error deleting customer: {err}")

    finally:
        cur.close()

def main(args):
    if args.command == "info":
        if args.id:
            display_info('id',args.id)
        elif args.name:
            display_info('name', args.name)
        elif args.genre:
            if not is_valid_genre(args.genre):
                print(f"Error: '{args.genre}' is not a valid genre.")
            else:
                display_info('genre', args.genre)
        elif args.all:
            display_info('all', args.all)

    elif args.command == "insert":
        insert_customer(args.id, args.name,
            args.email, args.pwd, args.gender, args.phone, args.genres)

    elif args.command == "update":
        if args.email:
            update_customer(args.c_id, 'email', args.email)
        elif args.pwd:
            previous_pwd, new_pwd = args.pwd
            update_customer(args.c_id, 'pwd', previous_pwd, new_pwd)
        elif args.phone:
            update_customer(args.c_id, 'phone', args.phone)
        elif args.genres:
            update_customer(args.c_id, 'genres', args.genres)

    elif args.command == "delete":
        delete_customer(args.c_id)
    else:
        print("Error: query command error.")


if __name__ == "__main__":
    #
    print_command_to_file()
    #
    start = time.time()
    
    parser = argparse.ArgumentParser(description = """
    how to use
    1. info [-i(c_id) / -n(c_name) / -g(genre) / -a (all)] [value]
    2. insert c_id, c_name, email, pwd, gender, phone -g (genre1, genre2, genre3)
    3. update -i [c_id] [-m(e-mail) / -p(password) / -ph(phone)] [new_value]
    4. delete -i [c_id]
    """, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', 
        help='select one of query types [info, insert, update, delete]')

    #[1-1]info
    parser_info = subparsers.add_parser('info', help='Display target customers info')
    group_info = parser_info.add_mutually_exclusive_group(required=True)
    group_info.add_argument('-i', dest='id', type=int, help='c_id of customer entity')
    group_info.add_argument('-n', dest='name', type=str, help='c_name of customer entity')
    group_info.add_argument('-g', dest='genre', type=str, help='genre which customer prefer')
    group_info.add_argument('-a', dest='all', type=int, help='display rows with top [value]')

    #[1-2]insert
    parser_insert = subparsers.add_parser('insert', help='Insert new customer data')
    parser_insert.add_argument('-g', dest='genres', nargs=3, type=str, required=True,
                               help='List of three genres preferred by customer')
    parser_insert.add_argument('id', type=int, help='Customer ID')
    parser_insert.add_argument('name', type=str, help='Customer name')
    parser_insert.add_argument('email', type=str, help='Customer email')
    parser_insert.add_argument('pwd', type=str, help='Customer password')
    parser_insert.add_argument('gender', type=str, choices=['M', 'F'], help='Customer gender (M or F)')
    parser_insert.add_argument('phone', type=str, help='Customer phone number')
    
    #[1-3]update
    parser_update = subparsers.add_parser('update', help='Update one of customer data')
    parser_update.add_argument('-i', dest='c_id', type=int, required=True, help='Customer ID to modify')
    update_group = parser_update.add_mutually_exclusive_group(required=True)
    update_group.add_argument('-m', dest='email', type=str, help='New email address')
    update_group.add_argument('-p', dest='pwd', nargs=2, type=str, help='New password')
    update_group.add_argument('-ph', dest='phone', type=str, help='New phone number (use "~ ~" to include spaces)')
    update_group.add_argument('-gs', dest='genres', nargs=3, type=str, help='List of three new genres')

    # TODO CLI로의 출력은 업데이트 전 정보 1번, 업데이트 후 정보 1번-> 총 2번의 출력

    #[1-4]delete
    parser_delete = subparsers.add_parser('delete', help='Delete customer data with associated data')
    parser_delete.add_argument('-i', dest='c_id', type=int, required=True, help='Customer ID to delete')
    
    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
