import mysql.connector

conn = mysql.connector.connect(user='root', password='password',
                              host='host.docker.internal',
                              database='world')

sql = 'insert into `日本語`(`カラム１`, `カラム（２）`)  values (%s, %s)'
cur = conn.cursor(dictionary=True)
cur.execute(sql, [2, '２つ目のデータ'])
conn.commit()
conn.close()
