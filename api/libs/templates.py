confirmation_email = """<html>
    <head></head>
    <style>
        table {{
            padding: .25rem; border: 1px solid black; border-radius: .25rem;
        }}
        table th {{
            background: #fcba03;
            border: 1px solid black;
            font-weight: 600;
            padding: .5rem;
            text-align: center;
        }}
        table td {{
            text-align: center;
            border: 1px solid black;
            padding: .25rem;
        }}
    </style>
    <body>
        <h2>Beantown Pub Merch Order Confirmation</h2>
        <table>
            <tr><th>Confirmation Code</th></tr>
            <tr><td>{}</td></tr>
        </table>
        <h3>Items</h3>
        <table>
            <tr><th>Name</th><th>Size</th><th>Quantity</th><th>Price</th><th>Item Total</th></tr>
            {}
        </table>
        <br />
        <table>
            <tr><th>Sub Total</th><td>{}</td></tr>
            <tr><th>Shipping</th><td>{}</td></tr>
            <tr><th>Total</th><td>{}</td></tr>
        </table>
        <h3>Shipping Address</h3>
        {}
        <p>Thank you for your order!</p>
        <p>You should receive your items in 4 to 6 business days</p>
        <p>Please do not reply directly to this email</p>
        <p>If you have any questions or concerns please contact us at {}<br />
        or give us a call during office hours (9am to 5pm EST) at {}</p>
    </body>
    </html>
    """

event_request_html = """<html>
    <head></head>
    <body>
        <h3>{} Private Event Contact</h3>
        <table>
            <tr><td><strong>Name:</strong></td><td>{}</td></tr>
            <tr><td><strong>Phone:</strong></td><td>{}</td></tr>
            <tr><td><strong>Email:</strong></td><td>{}</td></tr>
            <tr><td><strong>Details:</strong></td><td>{}</td></tr>
            <tr><td><strong>Catering:</strong></td><td>{}</td></tr>
        </table>
    </body>
    </html>
    """

event_request_raw = """
        {} Event Contact
        Name: {}
        Phone: {}
        Email: {}
        Details: {}
        Catering: {}
    """
