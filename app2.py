import mysql.connector
from mysql.connector.constants import FieldType, FieldFlag, CharacterSet
from mysql.connector.utils import NUMERIC_TYPES
from mysql.connector.custom_types import HexLiteral

class CustomMySQLConverter(mysql.connector.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        """Convert a MySQL text result row to Python types

        The row argument is a sequence containing text result returned
        by a MySQL server. Each value of the row is converted to the
        using the field type information in the fields argument.

        Returns a tuple.
        """
        i = 0
        result = [None]*len(fields)

        if not self._cache_field_types:
            self._cache_field_types = {}
            for name, info in FieldType.desc.items():
                try:
                    self._cache_field_types[info[0]] = getattr(
                        self, '_{0}_to_python'.format(name))
                except AttributeError:
                    # We ignore field types which has no method
                    pass
                    
        # print(row)  # (bytearray(b'1'), bytearray(b'aaaa'))
        
        for field in fields:
            field_type = field[1]
            print(field)  
            # ('id', 3, None, None, None, None, 0, 16899, 63)
            # ('name', 252, None, None, None, None, 1, 144, 45)
            if (row[i] == 0 and field_type != FieldType.BIT) or row[i] is None:
                # Don't convert NULL value
                i += 1
                continue

            try:
                # mediumtext型もblobとしかわからない
                # mediumtext型のカラムも複数あり、名前も異なるため、一律変換するしかない
                # ここでカラムのデータ型("mediumtext")を受け取ることはできなさそう
                # フィールド名(selectでの名前)はfield[0]で取得できる
                if field_type == FieldType.BLOB:
                    result[i] = row[i].decode('utf-8')
                else:
                    result[i] = self._cache_field_types[field_type](row[i], field)
            except KeyError:
                # If one type is not defined, we just return the value as str
                try:
                    result[i] = row[i].decode('utf-8')
                except UnicodeDecodeError:
                    result[i] = row[i]
            except (ValueError, TypeError) as err:
                err.message = "{0} (field {1})".format(str(err), field[0])
                raise

            i += 1

        return tuple(result)


conn = mysql.connector.connect(user='root', password='password',
                              host='localhost',
                              database='world',
                              converter_class=CustomMySQLConverter)

sql = 'select * from mtext'
cur = conn.cursor(dictionary=True)
cur.execute(sql, [])
rows = cur.fetchall()
for r in rows:
    print(r['name'], type(r['name']))
conn.close()
