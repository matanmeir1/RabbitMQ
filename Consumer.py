import pika
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory database to store processed orders
orders_db = {}


def callback(ch, method, properties, body):
    """Callback function to process received messages."""
    print("Callback invoked.")
    print(f" [x] Received message: {body.decode()}")
    try:
        order = json.loads(body)

        if order["status"] == "new":
            # Calculate shipping cost
            shipping_cost = round(order["totalAmount"] * 0.02, 2)
            order["shippingCost"] = shipping_cost
            orders_db[order["orderId"]] = order
            print(f" [x] Processed Order: {order}")
        else:
            print(f" [x] Ignoring order with status: {order['status']}")
    except Exception as e:
        print(f"Error processing message: {e}")


def consume_orders():
    """Continuously consume messages from RabbitMQ."""
    while True:
        try:
            print("Attempting to connect to RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            print("Connected to RabbitMQ.")

            channel = connection.channel()
            channel.exchange_declare(exchange='orders', exchange_type='fanout', durable=True)
            print("Exchange declared.")

            channel.queue_declare(queue='order_queue', durable=True)
            print("Queue declared: order_queue.")

            channel.queue_bind(exchange='orders', queue='order_queue')
            print("Queue bound to exchange: orders.")

            print("Subscribing to queue: order_queue...")
            channel.basic_consume(queue='order_queue', on_message_callback=callback, auto_ack=True)
            print("Consumer is ready. Waiting for messages...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")

        except Exception as e:
            print(f"Unexpected error in consume_orders: {e}")
            break


# Flask API endpoint to retrieve order details
@app.route('/order-details', methods=['GET'])
def get_order_details():
    """API endpoint to retrieve order details."""

    


    order_id = request.args.get('orderId')

    if not order_id or order_id not in orders_db:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(orders_db[order_id])


if __name__ == '__main__':
    import threading

    consumer_thread = threading.Thread(target=consume_orders)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host='0.0.0.0', port=5001)
