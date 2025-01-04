# RabbitMQ
Project in events oriented programming, using RabbitMQ

1. What's the project about?
Scenario: You are building a simplified backend system for an e-commerce platform.
When a customer places an order,
the order details must be broadcast to multiple downstream services (e.g., inventory management, billing, and shipping) via RabbitMQ.

2.The full Url’s and type of API request to generate the producer and the consumer applications.

Producer:  
URL: "http://<hostname>:5002/create-order"  

Consumer:  
URL: "http://<hostname>:5001/order-details"  


3.What type of exchange you chose and why?
 
Exchange Type: fanout  
Reason: I used a fanout exchange since i wanted, for this exersice,  all consumers to receive every message.
Also, This setup also allows adding more consumers in the future without modifying the producer logic.



4.Is there a binding key on the consumer? If so, what is it and why?

No Binding Key is Used, A fanout exchange ignores binding keys


5.Which service declared the exchange and queue and why?

Exchange Declaration:  
Declared by the Producer.  
Reason: The producer needs the orders exchange to exist before publishing messages.

Queue Declaration:  
Declared by the Consumer.  
Reason: The consumer declares a temporary queue (with `exclusive=True`) to receive messages during its runtime, therefore no need for the Producer to declare queue aswell.
