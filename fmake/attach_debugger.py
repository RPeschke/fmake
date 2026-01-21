
import os


def get_from_envirment(verbose=False):
        # Check for environment variable FMAKE_ATTACH_DEBUGGER in format "ip_address:port"
    if verbose:
        print("\n   Try to detect FMAKE_ATTACH_DEBUGGER Environment Variable:")
        print( "   Purpose: Configure debugpy listener IP address and port for remote debugging")
        print(f"   Format: 'ip_address:port' (e.g., '127.0.0.1:5678')")
    
    ip_address = None 
    port = None
    env_debugger = os.environ.get("FMAKE_ATTACH_DEBUGGER")
    if env_debugger:
        if verbose:
            print(f"   Value: {env_debugger}\n")

        try:
            parts = env_debugger.split(":")
            if len(parts) == 2:
                ip_address = parts[0]
                port = int(parts[1])
                if verbose:
                    print(f"✅ Using FMAKE_ATTACH_DEBUGGER: {ip_address}:{port}")
            else:
                if verbose:
                    print(f"❌ Invalid FMAKE_ATTACH_DEBUGGER format: {env_debugger}. Expected 'ip_address:port'")
        except (ValueError, IndexError) as e:
            if verbose:
                print(f"Error parsing FMAKE_ATTACH_DEBUGGER: {e}")
    return ip_address, port

launch_json_template = """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to python (debugpy)",
      "type": "python",
      "request": "attach",
      "connect": { "host": "{ip_address}", "port": {port} },
      "justMyCode": false
    }
  ]
}"""


def attach_debugger(ip_address=None, port = None , verbose=False , print_launch_message=False):
    import debugpy




    env = get_from_envirment(verbose=verbose)
    
    # Use provided arguments or defaults
    ip_address = ip_address if ip_address is not None else env[0] if env[0] is not None else "127.0.0.1"
    port = port if port is not None  else env[1] if env[1] is not None else 5678
    debugpy.listen((ip_address, port))
    
    if verbose:
        print(f"🛑 debugpy listening on {ip_address}:{port}, waiting for VS Code attach...")
    
    if print_launch_message:
        launch_json = launch_json_template.format(ip_address=ip_address, port=port)
        print("Add the following configuration to your VS Code launch.json:")
        print(launch_json)
    
    debugpy.wait_for_client()
    if verbose:
        print("✅ debugger attached")
