from nameko.rpc import rpc
import dependencies
from nameko.rpc import RpcProxy


class OrdersService:

    name = 'order_service'
    order_detail_rpc = RpcProxy('order_detail_service')
    order_package_rpc = RpcProxy('order_package_service')

    database = dependencies.Database()

    @rpc
    
    def get_all_orders(self):
        orders = self.database.get_all_orders()
        return orders
    
    @rpc
    def create_order_with_multiple_items(
        self, 
        items: list, # Accepts a list of item dictionaries
        user_id: int = "default_user", 
        reservasi_id: int = None, 
        event_id: int = None, 
        voucher_id: int = None, 
        order_type: int = 1,
        total_payment: float = 0.0 
    ):
        """
        Creates a new main order and associated order details/packages for multiple items.
        Automatically creates a main order and then adds details/packages via respective services.

        Args:
            items: A list of dictionaries, where each dictionary represents an item:
                   e.g., [{"type": "menu_item", "id": 101, "quantity": 2, "chef_id": 500, "note": "extra cheese"},
                          {"type": "menu_package", "id": 201, "quantity": 1, "note": "gift wrap"}]
                   Required keys for each item: "type", "id", "quantity".
                   Optional keys: "chef_id", "note", "status".
        """
        print(f"Received request to create order with {len(items)} items.")

        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            return {"success": False, "error": "Items must be a list of dictionaries."}
        if not items:
            return {"success": False, "error": "At least one item is required to create an order."}

        try:
            # 1. Create the main order
            # In a real scenario, you might fetch item prices and calculate total_payment here
            main_order_result = self.database.add_order(
                user_id=user_id,
                reservasi_id=reservasi_id,
                event_id=event_id,
                voucher_id=voucher_id,
                order_type=order_type,
                total_payment=total_payment
            )

            if not main_order_result.get("success"):
                raise Exception(f"Failed to create main order: {main_order_result.get('error', 'Unknown error')}")
            
            new_order_id = main_order_result.get("order_id")
            print(f"Main order created with ID: {new_order_id}")

            # 2. Iterate through items and create order details/packages
            details_results = []
            for item in items:
                item_type = item.get("type")
                item_id = item.get("id")
                item_quantity = item.get("quantity")
                
                if not all([item_type, item_id, item_quantity]):
                    print(f"Skipping invalid item: {item}. Missing type, id, or quantity.")
                    details_results.append({"success": False, "item": item, "error": "Missing type, id, or quantity for item."})
                    continue # Skip to the next item

                # Extract optional fields, providing None if not present
                item_note = item.get('note')
                item_status = item.get('status', 'PENDING')  # Default to 'PENDING' if not provided
                item_chef_id = item.get('chef_id') # Do not default here; let the RPC method's default handle it or explicitly pass None

                item_result = None
                if item_type == "menu_item":
                    print(f"Adding menu item detail for order {new_order_id}: menu_id={item_id}, qty={item_quantity}")
                    item_result = self.order_detail_rpc.add_order_details(
                        order_id=new_order_id,
                        menu_id=item_id,
                        chef_id=item_chef_id, # Pass what's provided, None if not provided
                        quantity=item_quantity,
                        note=item_note,
                        status=item_status 
                    )
                elif item_type == "menu_package":
                    print(f"Adding menu package detail for order {new_order_id}: package_id={item_id}, qty={item_quantity}")
                    item_result = self.order_package_rpc.add_order_packages(
                        order_id=new_order_id,
                        menu_package_id=item_id,
                        chef_id=item_chef_id, # Pass what's provided, None if not provided
                        quantity=item_quantity,
                        note=item_note,
                        status=item_status 
                    )
                else:
                    print(f"Unknown item type: {item_type} for item: {item}. Skipping.")
                    details_results.append({"success": False, "item": item, "error": f"Unknown item type: {item_type}"})
                    continue

                details_results.append({"item": item, "result": item_result})
                
                if not item_result or not item_result.get("success"):
                    print(f"Warning: Failed to process item {item_id} (type: {item_type}). Result: {item_result}")
                    # In a production system, you might want to log this more extensively
                    # or implement compensating transactions for the main order.

            print(f"All items processed for order ID {new_order_id}.")
            
            return {
                "success": True,
                "order_id": new_order_id,
                "items_processing_results": details_results,
                "message": "Order and all specified items processing initiated."
            }

        except Exception as e:
            print(f"Error creating order with multiple items: {e}")
            return {"success": False, "error": str(e)}
    