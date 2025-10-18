import pymysql

def main():
    conn = pymysql.connect(host='centerbeam.proxy.rlwy.net', port=11015, user='root', password='bZFZkbKFWCBSDWjNuLcehPViOrOgiEQA', database='railway')
    try:
        with conn.cursor() as cur:
            for t in ['prestamos_cliente', 'prestamos_prestamo', 'prestamos_cuotapago']:
                cur.execute(f"SELECT COUNT(*) FROM `{t}`")
                count = cur.fetchone()[0]
                print(f"{t}: {count}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()