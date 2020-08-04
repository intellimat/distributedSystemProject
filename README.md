# distributedSystemProject
This project is a simple example of how many systems can communicate together through the socket technology. 
The client can make a payment request through the html web page or can get/set some parameters on the processors through the appropriate url.
The request is first processed by the web server, that forwards it to the Gateway Server which handles the logic (it's like a controller).
The Gateway Server then makes the proper request to the processors and gets all the needed information and lastly generates an html page that sends to the web server.
Finally the web server returns this page to the client.
