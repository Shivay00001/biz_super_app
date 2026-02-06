import sys
import os
import tkinter as tk

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import BizApp
    print("Import successful")
    
    app = BizApp()
    print("App instantiated")
    
    app.update() # Process pending events
    print("App updated")
    
    # Check if billing frame exists
    if "billing" in app.frames:
        print("Billing module loaded")
    else:
        print("Billing module MISSING")
        sys.exit(1)
        
    app.destroy()
    print("App destroyed safely")
    
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
