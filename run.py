from BookingSystem import create_app

app = create_app()  # Create an app instance

if __name__ == '__main__':
    app.run(debug=True, port=5001)
