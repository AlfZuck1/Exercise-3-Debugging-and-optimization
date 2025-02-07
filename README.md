# Exercise-3-Debugging-and-optimization
Review the log at the end of the document, detect the main error, fix and optimize.

Identify the following error:
- **Identify the main error in the GET request to /api/users?id=123.**

The main error in the GET request is the KeyError.
- **Explain the cause of the KeyError and how to fix it.**

The KeyError happens when the requested information doesn't receive the "id" argument by using the GET request.

The solution is using args.get() instead of direct args["id"], this change allows us to get none instead of raising the exception. By doing this I created the method that lists all users when the parameter "id" is not present in the request.
- **Analyze the database error in the POST /api/orders request and propose a solution.**

The database error in the POST request is the IntegrityError: UNIQUE contraint, this means that the orders table cannot have 2 elements with the same id.  I came up with 2 possible solutions. The first is to prevent the POST request from being made if the "id" already exists. The second is to assume that the user intended to modify the existing element, so instead of making a POST request, a PUT request is made if the id already exists.

So the solution that I decided to implement was the second one.

- **Explain what the message "Transaction rolled back due to error" means.**

This message means that an error ocurred during a database transaction, so the rollback function undoes any changes made before the error ocurred to ensure the database consistency. In this case, this happened because the POST request created a duplicated "id" entry.

```Error log:
[2025-02-03 10:15:23] INFO  Server starting on port 8080... 
[2025-02-03 10:15:24] INFO  Database connection established successfully.
[2025-02-03 10:16:05] INFO  Received request: GET /api/users?id=123
[2025-02-03 10:16:06] ERROR Unhandled exception occurred
[2025-02-03 10:16:06] ERROR Traceback (most recent call last):
[2025-02-03 10:16:06] ERROR File "/app/server.py", line 87, in handle_request
[2025-02-03 10:16:06] ERROR   user_data = database.get_user(request.params["id"])
[2025-02-03 10:16:06] ERROR KeyError: 'id'
[2025-02-03 10:16:06] WARN  Falling back to default user data
[2025-02-03 10:16:07] INFO  Response sent with status 200
[2025-02-03 10:16:08] INFO  Received request: POST /api/orders
[2025-02-03 10:16:08] ERROR Database query failed: IntegrityError: UNIQUE constraint failed: orders.id
[2025-02-03 10:16:08] ERROR Query: INSERT INTO orders (id, user_id, total) VALUES (123, 456, 99.99);
[2025-02-03 10:16:09] ERROR Transaction rolled back due to error.
[2025-02-03 10:16:10] INFO  Server shutting down...
```

