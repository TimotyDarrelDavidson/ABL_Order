from nameko.rpc import rpc
import dependencies

class orderPackagesService:

    name = 'order_package_service'

    database = dependencies.Database()

    @rpc
    def get_all_order_packages(self):
        orders = self.database.get_all_order_packages()
        return orders
    
    @rpc
    def get_order_packages_orderID(self, order_id):
        orders = self.database.get_order_packages_orderID(order_id)
        return orders
    
    @rpc
    def get_order_packages_chefID(self, chef_id):
        orders = self.database.get_order_packages_chefID(chef_id)
        return orders
    
    @rpc 
    def add_order_packages(self, order_id, menu_package_id, chef_id, quantity, note='None', status='PENDING'):
        """
        Adds a new order package. Updated to accept all fields.
        """
        print(f"OrderPackagesService: Adding package for order {order_id}, package {menu_package_id}...")
        try:
            # Calls DatabaseWrapper.add_order_packages with all parameters
            result = self.database.add_order_packages(order_id, menu_package_id, chef_id, quantity, note, status)
            print(f"Order package added result: {result}")
            return result
        except Exception as e:
            print(f"Error adding order package: {e}")
            return {"success": False, "error": f"Failed to add order package: {e}"}


    @rpc
    def change_order_packages_status(self, order_packages_id, new_status):
        if new_status not in ['PENDING', 'ON DELIVERY', 'COMPLETED', 'PACKED']: # Added PACKED status for packages
            return {"success": False, "error": "New status must be one of these: 'PENDING', 'ON DELIVERY', 'COMPLETED', 'PACKED'"}
        
        try:
            result = self.database.change_order_packages_status(order_packages_id, new_status)
            return result
        except Exception as e:
            print(f"Error changing order package status: {e}")
            return {"success": False, "error": f"Failed to change status: {e}"}

    @rpc
    def change_order_packages_quantity(self, order_packages_id: int, new_quantity: int):
        """
        Changes the quantity of a specific order package.
        """
        if not isinstance(new_quantity, int) or new_quantity <= 0:
            return {"success": False, "error": "New quantity must be a positive integer."}
        
        try:
            result = self.database.change_order_packages_quantity(order_packages_id, new_quantity)
            return result
        except Exception as e:
            print(f"Error changing order package quantity: {e}")
            return {"success": False, "error": f"Failed to change quantity: {e}"}

    @rpc
    def change_order_packages_note(self, order_packages_id: int, new_note: str):
        """
        Changes the note of a specific order package.
        """
        if not isinstance(new_note, str):
            return {"success": False, "error": "New note must be a string."}
        
        try:
            result = self.database.change_order_packages_note(order_packages_id, new_note)
            return result
        except Exception as e:
            print(f"Error changing order package note: {e}")
            return {"success": False, "error": f"Failed to change note: {e}"}
