import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http

class GatewayService:
    name = 'gateway'

    # RPC Proxies for your backend servicesj
    order_rpc = RpcProxy('order_service')
    order_detail_rpc = RpcProxy('order_detail_service')
    order_package_rpc = RpcProxy('order_package_service')

    # --- Endpoints for OrderService ---

    @http('GET', '/orders')
    def get_all_orders(self, request):
        """
        Retrieves all main orders.
        """
        print("Gateway: Received GET /orders request")
        try:
            orders = self.order_rpc.get_all_orders()
            return json.dumps(orders)
        except Exception as e:
            print(f"Gateway Error: get_all_orders - {e}")
            return 500, json.dumps({"error": str(e)})
    
     # --- Endpoints for OrderDetailService ---

    @http('GET', '/order-details')
    def get_all_order_details(self, request):
        """
        Retrieves all order details.
        """
        print("Gateway: Received GET /order-details request")
        try:
            details = self.order_detail_rpc.get_all_order_details()
            return json.dumps(details)
        except Exception as e:
            print(f"Gateway Error: get_all_order_details - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('GET', '/order-details/by-order/<string:order_id>')
    def get_order_details_by_order_id(self, request, order_id):
        """
        Retrieves order details by a specific order ID.
        """
        print(f"Gateway: Received GET /order-details/by-order/{order_id} request")
        try:
            details = self.order_detail_rpc.get_order_details_orderID(order_id)
            if details:
                return json.dumps(details)
            return 404, json.dumps({"message": "Order details not found for this order ID."})
        except Exception as e:
            print(f"Gateway Error: get_order_details_by_order_id - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('GET', '/order-details/by-chef/<int:chef_id>')
    def get_order_details_by_chef_id(self, request, chef_id):
        """
        Retrieves order details by a specific chef ID.
        """
        print(f"Gateway: Received GET /order-details/by-chef/{chef_id} request")
        try:
            details = self.order_detail_rpc.get_order_details_chefID(chef_id)
            if details:
                return json.dumps(details)
            return 404, json.dumps({"message": "Order details not found for this chef ID."})
        except Exception as e:
            print(f"Gateway Error: get_order_details_by_chef_id - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('POST', '/order-details')
    def add_order_details(self, request):
        """
        Adds new order details.
        Expected JSON body: {"order_id": "...", "menu_id": int, "chef_id": int, "quantity": int, "note": "...", "status": "..."}
        """
        print("Gateway: Received POST /order-details request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            required_fields = ['order_id', 'menu_id', 'chef_id', 'quantity']
            if not all(field in payload for field in required_fields):
                return 400, json.dumps({"error": f"Missing required fields. Required: {required_fields}"})

            # Call the RPC service
            result = self.order_detail_rpc.add_order_details(
                order_id=payload['order_id'],
                menu_id=payload['menu_id'],
                chef_id=payload['chef_id'],
                quantity=payload['quantity'],
                note=payload.get('note'),   
                status=payload.get('status', 'PENDING') # Default status if not provided
            )
            return 201, json.dumps(result) # 201 Created
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: add_order_details - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-details/<int:order_details_id>/status')
    def change_order_details_status(self, request, order_details_id):
        """
        Changes the status of a specific order detail.
        Expected JSON body: {"new_status": "..."}
        """
        print(f"Gateway: Received PUT /order-details/{order_details_id}/status request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_status = payload.get('new_status')
            if not new_status:
                return 400, json.dumps({"error": "Missing 'new_status' in payload."})

            result = self.order_detail_rpc.change_order_details_status(order_details_id, new_status)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_details_status - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-details/<int:order_details_id>/quantity')
    def change_order_details_quantity(self, request, order_details_id):
        """
        Changes the quantity of a specific order detail.
        Expected JSON body: {"new_quantity": int}
        """
        print(f"Gateway: Received PUT /order-details/{order_details_id}/quantity request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_quantity = payload.get('new_quantity')
            if new_quantity is None: # Check for None to allow 0 if applicable, but validation handles positive
                return 400, json.dumps({"error": "Missing 'new_quantity' in payload."})

            result = self.order_detail_rpc.change_order_details_quantity(order_details_id, new_quantity)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_details_quantity - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-details/<int:order_details_id>/note')
    def change_order_details_note(self, request, order_details_id):
        """
        Changes the note of a specific order detail.
        Expected JSON body: {"new_note": "..."}
        """
        print(f"Gateway: Received PUT /order-details/{order_details_id}/note request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_note = payload.get('new_note') # Allows new_note to be null/None
            if new_note is None and 'new_note' not in payload: # Check if key exists vs value is None
                return 400, json.dumps({"error": "Missing 'new_note' in payload."})

            result = self.order_detail_rpc.change_order_details_note(order_details_id, new_note)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_details_note - {e}")
            return 500, json.dumps({"error": str(e)})
        

        # --- Endpoints for OrderPackageService ---



    # -- Endopints for OrderPackageService --- #

    @http('GET', '/order-packages')
    def get_all_order_packages(self, request):
        """
        Retrieves all order packages.
        """
        print("Gateway: Received GET /order-packages request")
        try:
            packages = self.order_package_rpc.get_all_order_packages()
            return json.dumps(packages)
        except Exception as e:
            print(f"Gateway Error: get_all_order_packages - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('GET', '/order-packages/by-order/<string:order_id>')
    def get_order_packages_by_order_id(self, request, order_id):
        """
        Retrieves order packages by a specific order ID.
        """
        print(f"Gateway: Received GET /order-packages/by-order/{order_id} request")
        try:
            packages = self.order_package_rpc.get_order_packages_orderID(order_id)
            if packages:
                return json.dumps(packages)
            return 404, json.dumps({"message": "Order packages not found for this order ID."})
        except Exception as e:
            print(f"Gateway Error: get_order_packages_by_order_id - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('GET', '/order-packages/by-chef/<int:chef_id>')
    def get_order_packages_by_chef_id(self, request, chef_id):
        """
        Retrieves order packages by a specific chef ID.
        """
        print(f"Gateway: Received GET /order-packages/by-chef/{chef_id} request")
        try:
            packages = self.order_package_rpc.get_order_packages_chefID(chef_id)
            if packages:
                return json.dumps(packages)
            return 404, json.dumps({"message": "Order packages not found for this chef ID."})
        except Exception as e:
            print(f"Gateway Error: get_order_packages_by_chef_id - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('POST', '/order-packages')
    def add_order_packages(self, request):
        """
        Adds new order packages.
        Expected JSON body: {"order_id": "...", "menu_package_id": int, "chef_id": int, "quantity": int, "note": "...", "status": "..."}
        """
        print("Gateway: Received POST /order-packages request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            required_fields = ['order_id', 'menu_package_id', 'chef_id', 'quantity']
            if not all(field in payload for field in required_fields):
                return 400, json.dumps({"error": f"Missing required fields. Required: {required_fields}"})

            result = self.order_package_rpc.add_order_packages(
                order_id=payload['order_id'],
                menu_package_id=payload['menu_package_id'],
                chef_id=payload['chef_id'],
                quantity=payload['quantity'],
                note=payload.get('note'),
                status=payload.get('status', 'PENDING')  # Default status if not provided
            )
            return 201, json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: add_order_packages - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-packages/<int:order_packages_id>/status')
    def change_order_packages_status(self, request, order_packages_id):
        """
        Changes the status of a specific order package.
        Expected JSON body: {"new_status": "..."}
        """
        print(f"Gateway: Received PUT /order-packages/{order_packages_id}/status request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_status = payload.get('new_status')
            if not new_status:
                return 400, json.dumps({"error": "Missing 'new_status' in payload."})

            result = self.order_package_rpc.change_order_packages_status(order_packages_id, new_status)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_packages_status - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-packages/<int:order_packages_id>/quantity')
    def change_order_packages_quantity(self, request, order_packages_id):
        """
        Changes the quantity of a specific order package.
        Expected JSON body: {"new_quantity": int}
        """
        print(f"Gateway: Received PUT /order-packages/{order_packages_id}/quantity request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_quantity = payload.get('new_quantity')
            if new_quantity is None:
                return 400, json.dumps({"error": "Missing 'new_quantity' in payload."})

            result = self.order_package_rpc.change_order_packages_quantity(order_packages_id, new_quantity)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_packages_quantity - {e}")
            return 500, json.dumps({"error": str(e)})

    @http('PUT', '/order-packages/<int:order_packages_id>/note')
    def change_order_packages_note(self, request, order_packages_id):
        """
        Changes the note of a specific order package.
        Expected JSON body: {"new_note": "..."}
        """
        print(f"Gateway: Received PUT /order-packages/{order_packages_id}/note request")
        try:
            payload = json.loads(request.get_data(as_text=True))
            new_note = payload.get('new_note')
            if new_note is None and 'new_note' not in payload:
                return 400, json.dumps({"error": "Missing 'new_note' in payload."})

            result = self.order_package_rpc.change_order_packages_note(order_packages_id, new_note)
            return json.dumps(result)
        except json.JSONDecodeError:
            return 400, json.dumps({"error": "Invalid JSON payload."})
        except Exception as e:
            print(f"Gateway Error: change_order_packages_note - {e}")
            return 500, json.dumps({"error": str(e)})
