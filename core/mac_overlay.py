import logging
import sys

def enforce_mac_overlay(win_id):
    if sys.platform != "darwin":
        return

    try:
        import objc
        from AppKit import (
            NSWindow, 
            NSScreenSaverWindowLevel, 
            NSWindowCollectionBehaviorCanJoinAllSpaces,
            NSWindowCollectionBehaviorFullScreenAuxiliary,
            NSWindowCollectionBehaviorStationary,
            NSWindowCollectionBehaviorIgnoresCycle
        )
        
        # win_id from QWidget.winId() on macOS is the NSView pointer
        # We need to get the NSWindow
        ns_view = objc.objc_object(c_void_p=int(win_id))
        ns_window = ns_view.window()
        
        if ns_window:
            # Set above normal windows
            ns_window.setLevel_(NSScreenSaverWindowLevel)
            
            # Collection behavior
            ns_window.setCollectionBehavior_(
                NSWindowCollectionBehaviorCanJoinAllSpaces |
                NSWindowCollectionBehaviorFullScreenAuxiliary |
                NSWindowCollectionBehaviorStationary |
                NSWindowCollectionBehaviorIgnoresCycle
            )
            
            # Crucial: Don't hide when app loses focus
            ns_window.setHidesOnDeactivate_(False)
            
    except Exception as e:
        logging.error(f"macOS overlay enforcement failed: {e}")

def debug_mac_overlay(win_id):
    if sys.platform != "darwin":
        return
        
    try:
        import objc
        ns_view = objc.objc_object(c_void_p=int(win_id))
        ns_window = ns_view.window()
        if ns_window:
            level = ns_window.level()
            hides = ns_window.hidesOnDeactivate()
            collection = ns_window.collectionBehavior()
            logging.info(f"Overlay NSWindow state -> level: {level}, hidesOnDeactivate: {hides}, collectionBehavior: {collection}")
    except Exception as e:
        logging.error(f"macOS overlay debug failed: {e}")
