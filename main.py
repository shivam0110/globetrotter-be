from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Print a message to confirm routes are registered
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.methods} {rule.rule}")
    
    # Run the application
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
