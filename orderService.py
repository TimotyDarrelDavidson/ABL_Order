from nameko.rpc import rpc
from nameko.rpc import RpcProxy
from datetime import datetime  # ← tambahkan ini

import dependencies

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
        items: list,
        user_id: int = "default_user",
        reservasi_id: int = None,
        event_id: int = None,
        voucher_id: int = None,
        order_type: int = 1,
        total_payment: float = 0.0
    ):
        print(f"Received request to create order with {len(items)} items.")

        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            return {"success": False, "error": "Items must be a list of dictionaries."}
        if not items:
            return {"success": False, "error": "At least one item is required to create an order."}

        try:
            # ✅ Tambahkan timestamp created_at
            created_at = datetime.now()

            # 1. Create the main order
            main_order_result = self.database.add_order(
                user_id=user_id,
                reservasi_id=reservasi_id,
                event_id=event_id,
                voucher_id=voucher_id,
                order_type=order_type,
                total_payment=total_payment,
                created_at=created_at  # ← kirim created_at ke database
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
                    continue

                item_note = item.get('note')
                item_status = item.get('status', 'PENDING')
                item_chef_id = item.get('chef_id')

                item_result = None
                if item_type == "menu_item":
                    print(f"Adding menu item detail for order {new_order_id}: menu_id={item_id}, qty={item_quantity}")
                    item_result = self.order_detail_rpc.add_order_details(
                        order_id=new_order_id,
                        menu_id=item_id,
                        chef_id=item_chef_id,
                        quantity=item_quantity,
                        note=item_note,
                        status=item_status
                    )
                elif item_type == "menu_package":
                    print(f"Adding menu package detail for order {new_order_id}: package_id={item_id}, qty={item_quantity}")
                    item_result = self.order_package_rpc.add_order_packages(
                        order_id=new_order_id,
                        menu_package_id=item_id,
                        chef_id=item_chef_id,
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

    @rpc
    def update_order(self, order_id, update_data: dict):
        """
        Memperbarui data utama dari sebuah order berdasarkan order_id.
        update_data bisa berisi: user_id, reservasi_id, event_id, voucher_id, order_type, total_payment
        """
        try:
            # Cek apakah order ada
            orders = self.database.get_all_orders()
            if not any(o["order_id"] == order_id for o in orders):
                return {"success": False, "message": f"Order with ID {order_id} not found."}

            result = self.database.update_order(order_id, update_data)
            return {"success": result, "message": "Order updated successfully." if result else "Update failed."}
        except Exception as e:
            return {"success": False, "message": str(e)}


    @rpc
    def delete_order(self, order_id):
        """
        Menghapus order beserta detail dan paketnya.
        """
        try:
            # Hapus semua order details
            deleted_details = self.order_detail_rpc.delete_order_details_by_order_id(order_id)
            deleted_packages = self.order_package_rpc.delete_order_packages_by_order_id(order_id)

            # Hapus order utama
            success = self.database.delete_order(order_id)

            return {
                "success": success,
                "message": "Order deleted successfully." if success else "Failed to delete order.",
                "details_deleted": deleted_details,
                "packages_deleted": deleted_packages
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

