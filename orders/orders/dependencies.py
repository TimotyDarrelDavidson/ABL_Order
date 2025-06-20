from nameko.extensions import DependencyProvider
import mysql.connector

class DatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection



    # ---     Order      --- #

    def get_all_orders(self):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            result = []
            sql = "SELECT * FROM `orders`"
            cursor.execute(sql)
            for row in cursor.fetchall():
                result.append({
                    'order_id': row['order_id'],
                    'user_id': row['user_id'],
                    'reservasi_id': row['reservasi_id'],
                    'event_id': row['event_id'],
                    'voucher_id': row['voucher_id'],
                    'order_type': row['order_type'],
                    'total_payment': row['total_payment']
                })
            return result
        except mysql.connector.Error as e:
            print(f"DatabaseWrapper.get_all_orders error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def add_order(self, user_id, reservasi_id, event_id, voucher_id, order_type, total_payment):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO `orders`
                (user_id, reservasi_id, event_id, voucher_id, order_type, total_payment)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (user_id, reservasi_id, event_id, voucher_id, order_type, total_payment)
            cursor.execute(sql, values)
            self.connection.commit()
            # FIX: Changed cursor.lastrowid() to cursor.lastrowid
            new_order_id = cursor.lastrowid
            print(f"Main order added with ID: {new_order_id}")
            return {"success": True, "order_id": new_order_id}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.add_order error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


    # --- Order Packages --- #

    def add_order_packages(self, order_id, menu_package_id, chef_id, quantity, note, status):
        cursor = None
        try:
            cursor = self.connection.cursor()
            
            sql = "INSERT INTO order_packages (order_id, menu_package_id, chef_id, quantity, note, status) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (order_id, menu_package_id, chef_id, quantity, note, status)
            cursor.execute(sql, values)
            
            self.connection.commit()
            print(f"DatabaseWrapper: Order packages added: Order ID {order_id}, Menu Package ID {menu_package_id}")
            return {"success": True, "id": cursor.lastrowid if cursor.lastrowid else None} # Return success and ID
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.add_order_packages error: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def get_all_order_packages(self):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = "SELECT * FROM order_packages"
        cursor.execute(sql)
        for row in cursor.fetchall():
            result.append({
                'order_package_id': row['order_package_id'],
                'order_id': row['order_id'],
                'menu_id': row['menu_id'],
                'chef_id': row['chef_id'],
                'quantity': row['quantity'],
                'note': row['note'],
                'status': row['status']
            })
        cursor.close()
        return result

    def get_order_packages_orderID(self, order_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            sql = "SELECT * FROM order_packages WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            result = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
        return result or "Room not found"
    
    def get_order_packages_chefID(self, chef_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            sql = "SELECT * FROM order_packages WHERE chef_id = %s"
            cursor.execute(sql, (chef_id,))
            result = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
        return result or "Room not found"
    
    def change_order_packages_status(self, order_package_id, new_status):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_packages` SET `status` = %s WHERE `id` = %s"
            values = (new_status, order_package_id)
            cursor.execute(sql, values)
            self.connection.commit()
            if cursor.rowcount == 0:
                print(f"Order package with ID {order_package_id} not found for status update.")
                return {"success": False, "message": f"Order package {order_package_id} not found."}
            else:
                print(f"Order package {order_package_id} status updated to {new_status}.")
                return {"success": True, "message": f"Order package {order_package_id} status updated."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_packages_status error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def change_order_packages_quantity(self, order_package_id, new_quantity):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_packages` SET `quantity` = %s WHERE `order_package_id` = %s"
            values = (new_quantity, order_package_id)
            cursor.execute(sql, values)
            self.connection.commit()
            if cursor.rowcount == 0:
                print(f"Order package with ID {order_package_id} not found for quantity update.")
                return {"success": False, "message": f"Order package {order_package_id} not found."}
            else:
                print(f"Order package {order_package_id} quantity updated to {new_quantity}.")
                return {"success": True, "message": f"Order package {order_package_id} quantity updated."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_packages_quantity error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def change_order_packages_note(self, order_package_id, new_note):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_packages` SET `note` = %s WHERE `id` = %s"
            values = (new_note, order_package_id)
            cursor.execute(sql, values)
            self.connection.commit()
            print(f"Order package with ID {order_package_id} not found for note update.")
            return {"success": False, "message": f"Order package {order_package_id} not found."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_packages_note error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def delete_order_package(self, order_package_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            sql = "DELETE FROM `order_packages` WHERE num = %s"
            cursor.execute(sql,(order_package_id,))
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()


    # --- Order Details --- #

    def add_order_details(self, order_id, menu_id, chef_id, quantity, note, status):
        cursor = None
        try:
            cursor = self.connection.cursor()
            
            sql = "INSERT INTO order_details (order_id, menu_id, chef_id, quantity, note, status) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (order_id, menu_id, chef_id, quantity, note, status)
            cursor.execute(sql, values)
            
            self.connection.commit()
            print(f"DatabaseWrapper: Order details added: Order ID {order_id}, Menu ID {menu_id}")
            return {"success": True, "id": cursor.lastrowid if cursor.lastrowid else None} # Return success and ID
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.add_order_details error: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def get_all_order_details(self):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = "SELECT * FROM order_details"
        cursor.execute(sql)
        for row in cursor.fetchall():
            result.append({
                'order_detail_id': row['order_detail_id'],
                'order_id': row['order_id'],
                'menu_id': row['menu_id'],
                'chef_id': row['chef_id'],
                'quantity': row['quantity'],
                'note': row['note'],
                'status': row['status']
            })
        cursor.close()
        return result

    def get_order_details_orderID(self, order_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            sql = "SELECT * FROM order_details WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            result = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
        return result or "Room not found"
    
    def get_order_details_chefID(self, chef_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            sql = "SELECT * FROM order_details WHERE chef_id = %s"
            cursor.execute(sql, (chef_id,))
            result = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
        return result or "Room not found"
    
    def change_order_details_status(self, order_detail_id, new_status):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_details` SET `status` = %s WHERE `id` = %s"
            values = (new_status, order_detail_id)
            cursor.execute(sql, values)
            self.connection.commit()
            if cursor.rowcount == 0:
                print(f"Order detail with ID {order_detail_id} not found for status update.")
                return {"success": False, "message": f"Order detail {order_detail_id} not found."}
            else:
                print(f"Order detail {order_detail_id} status updated to {new_status}.")
                return {"success": True, "message": f"Order detail {order_detail_id} status updated."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_details_status error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def change_order_details_quantity(self, order_detail_id, new_quantity):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_details` SET `quantity` = %s WHERE `order_detail_id` = %s"
            values = (new_quantity, order_detail_id)
            cursor.execute(sql, values)
            self.connection.commit()
            if cursor.rowcount == 0:
                print(f"Order detail with ID {order_detail_id} not found for quantity update.")
                return {"success": False, "message": f"Order detail {order_detail_id} not found."}
            else:
                print(f"Order detail {order_detail_id} quantity updated to {new_quantity}.")
                return {"success": True, "message": f"Order detail {order_detail_id} quantity updated."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_details_quantity error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def change_order_details_note(self, order_detail_id, new_note):
        cursor = None
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE `order_details` SET `note` = %s WHERE `id` = %s"
            values = (new_note, order_detail_id)
            cursor.execute(sql, values)
            self.connection.commit()
            print(f"Order detail with ID {order_detail_id} not found for note update.")
            return {"success": False, "message": f"Order detail {order_detail_id} not found."}
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"DatabaseWrapper.change_order_details_note error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def delete_order_detail(self, order_detail_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            sql = "DELETE FROM `order_details` WHERE num = %s"
            cursor.execute(sql,(order_detail_id,))
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()

class Database(DependencyProvider):

    connection_pool = None

    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="database_pool",
                pool_size=10,
                pool_reset_session=True,
                host='127.0.0.1',
                port="3306",
                database='abl_order',
                user='root',
                password=''
            )
        except mysql.connector.Error as e:
            print ("Error while connecting to MySQL using Connection pool:", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())

# def get_all_room_type(self):
    #     cursor = self.connection.cursor(dictionary=True)
    #     result = []
    #     sql = "SELECT * FROM room_type"
    #     cursor.execute(sql)
    #     for row in cursor.fetchall():
    #         result.append({
    #             'id': row['id'],
    #             'name': row['name'],
    #             'price': row['price'],
    #             'capacity': row['capacity'],
    #             'status': row['status']
    #         })
    #     cursor.close()
    #     return result

    # def get_all_room(self):
    #     cursor = self.connection.cursor(dictionary=True)
    #     result = []
    #     sql = "SELECT * FROM room"
    #     cursor.execute(sql)
    #     for row in cursor.fetchall():
    #         result.append({
    #             'num': row['num'],
    #             'id_type': row['id_type'],
    #             'status': row['status']
    #         })
    #     cursor.close()
    #     return result

    # def get_room_by_num(self, num):
    #     try:
    #         cursor = self.connection.cursor(dictionary=True)
    #         sql = "SELECT * FROM room WHERE num = {}".format((num))
    #         cursor.execute(sql)
    #         result = cursor.fetchone()
    #     except mysql.connector.Error as e:
    #         print(f"Database error: {e}")
    #     finally:
    #         cursor.close()
    #     return result or "Room not found"
    
    # def add_room(self, room_num, room_type):
    #     try:
    #         cursor = self.connection.cursor(dictionary=True)
            
    #         sql = "SELECT * FROM room_type WHERE id = %s"
    #         cursor.execute(sql,(room_type,))
    #         result = cursor.fetchone()
            
    #         if result is None:
    #             return f"Error: Room type {room_type} not found!"
            
    #         status = result["status"]
            
    #         sql = "INSERT INTO room (num, id_type, status) VALUES (%s, %s, %s)"
    #         values = (room_num, room_type, status)
    #         cursor.execute(sql, values)
            
    #         self.connection.commit()
    #     except mysql.connector.Error as e:
    #         print(f"Database error: {e}")
    #     finally:
    #         cursor.close()
            
    # def change_room_status(self,room_num):
    #     try:
    #         cursor = self.connection.cursor(dictionary=True)
            
    #         sql = "SELECT * FROM room WHERE num = %s"
    #         cursor.execute(sql,(room_num,))
    #         result = cursor.fetchone()
            
    #         if result is None:
    #             cursor.close()
    #             print(f"Error: Room type {room_num} not found!")
    #             return
            
    #         status = 0 if result["status"] == 1 else 1
            
    #         sql = "UPDATE `room` SET `status`= %s WHERE num = %s"
    #         values = (status, room_num)
    #         cursor.execute(sql, values)
            
    #         self.connection.commit()
    #     except mysql.connector.Error as e:
    #         print(f"Database error: {e}")
    #     finally:
    #         cursor.close()
            
    # def delete_room(self, room_num):
    #     try:
    #         cursor = self.connection.cursor(dictionary=True)
            
    #         sql = "DELETE FROM `room` WHERE num = %s"
    #         cursor.execute(sql,(room_num,))
    #         self.connection.commit()
    #     except mysql.connector.Error as e:
    #         print(f"Database error: {e}")
    #     finally:
    #         cursor.close()

    # def __del__(self):
    #    self.connection.close()