from flask import Flask, request, jsonify
import pika
import random
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/create-order', methods=['POST'])
def create_order():
    # Step 1: Parse Input
    data = request.json
    order_id = data.get('orderId')
    num_items = data.get('itemsNum')


    # Step 2: Validate Input
    if not order_id or not isinstance(num_items, int) or num_items <= 0:
        return jsonify({"error": "Invalid input"}), 400


    # Step 3: Generate Order Object
    items = [
        {
            "itemId": f"ITEM-{i+1}",
            "quantity": random.randint(1, 5),  # Random quantity between 1 and 5
            "price": round(random.uniform(10, 100), 2)  # Random price between $10 and $100
        }
        for i in range(num_items)
    ]
    total_amount = sum(item["quantity"] * item["price"] for item in items)

    # Add a list of statuses and pick one randomly
    statuses = ["new", "processing", "shipped", "cancelled"]
    random_status = random.choice(statuses)

    order = {
        "orderId": order_id,
        "customerId": f"CUST-{random.randint(1, 1000)}",
        "orderDate": datetime.now().isoformat(),
        "items": items,
        "totalAmount": round(total_amount, 2),
        "currency": "USD",
        "status": random_status
    }

    # Step 4: Publish to RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))  # Use 'rabbitmq' service name
        channel = connection.channel()

        # Declare the 'orders' exchange
        channel.exchange_declare(exchange='orders', exchange_type='fanout', durable=True)

        # Publish the message to the exchange
        channel.basic_publish(
            exchange='orders',
            routing_key='',  # Not needed for fanout exchanges
            body=json.dumps(order)
        )

        connection.close()
    except pika.exceptions.AMQPError as e:
        return jsonify({"error": "Failed to publish message", "details": str(e)}), 500

    # Step 5: Return Response
    return jsonify(order), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Bind to 0.0.0.0 to allow access from outside the container
