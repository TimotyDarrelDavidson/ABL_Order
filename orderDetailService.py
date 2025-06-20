from nameko.rpc import rpc
import dependencies

class orderDetailsService:

    name = 'order_detail_service'

    database = dependencies.Database()

    @rpc
    def get_all_order_details(self):
        """
        Retrieves all Order Detail
        """
        orders = self.database.get_all_order_details()
        return orders

    @rpc
    def get_order_details_orderID(self, order_id):
        """
        Retrieves all Order Detail by Order ID
        """
        orders = self.database.get_order_details_orderID(order_id)
        return orders
    
    @rpc
    def get_order_details_chefID(self, chef_id):
        """
        Retrieves all Order Detail by Chef ID
        """
        orders = self.database.get_order_details_chefID(chef_id)
        return orders
    
    @rpc 
    def add_order_details(self, order_id, menu_id, chef_id, quantity, note='None', status='PENDING'):
        """
        Creates a new Order Detail
        Expected data: Order_id, Menu_id, Chef_id, Quantity 
        New order with empty status automatically becomes PENDING
        """
        self.database.add_order_details(order_id, menu_id, chef_id, quantity, note, status)

    @rpc
    def delete_order_details_by_order_id(self, order_id):
        return self.database.delete_order_details_by_order_id(order_id)


    @rpc
    def change_order_details_status(self, order_details_id, new_status):
        """
        Changes status of a specific Order Detail
        Expected data: Order_Detail_ID, new_status
        """
        if new_status not in ['PENDING', 'ON DELIVERY', 'COMPLETED']:
            return {"success": False, "error": "New status must be one of these: 'PENDING', 'ON DELIVERY', 'COMPLETED"}
        
        try:
            result = self.database.change_order_details_status(order_details_id, new_status)
            return result
        except Exception as e:
            print(f"Error changing order detail status: {e}")
            return {"success": False, "error": f"Failed to change status: {e}"}

    @rpc
    def change_order_details_quantity(self, order_details_id: int, new_quantity: int):
        """
        Changes quantity of a specific Order Detail
        Expected data: Order_Detail_ID, new_quantity
        """
        if not isinstance(new_quantity, int) or new_quantity <= 0:
            return {"success": False, "error": "New quantity must be a positive integer."}
        
        try:
            result = self.database.change_order_details_quantity(order_details_id, new_quantity)
            return result
        except Exception as e:
            print(f"Error changing order detail quantity: {e}")
            return {"success": False, "error": f"Failed to change quantity: {e}"}

    @rpc
    def change_order_details_note(self, order_details_id: int, new_note: str):
        """
        Changes note of a specific Order Detail
        Expected data: Order_Detail_ID, new_note
        """
        if not isinstance(new_note, str):
            return {"success": False, "error": "New note must be a string."}
        
        try:
            result = self.database.change_order_details_note(order_details_id, new_note)
            return result
        except Exception as e:
            print(f"Error changing order detail note: {e}")
            return {"success": False, "error": f"Failed to change note: {e}"}