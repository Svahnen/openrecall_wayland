# OpenRecall Wayland (Unofficial Fork)

**Disclaimer**: This is an unofficial fork of [OpenRecall](https://github.com/openrecall/openrecall) that attempts to support Wayland-based Linux systems (e.g. Fedora Silverblue/Gnome). It replaces `mss` with PyScreenshot for Wayland capture. This approach is **temporary** until the official OpenRecall project natively implements Wayland support.

---

## What’s Different in This Fork?

- **Wayland Compatibility**: Uses PyScreenshot’s `grab()` when `XDG_SESSION_TYPE=wayland`, instead of `mss`.
- **Flashing & Sound**: On Gnome/Wayland, taking screenshots can produce a camera-shutter sound or screen flash by default. To mitigate:
  1. **Mute Sound**:  

     ```bash
     gsettings set org.gnome.desktop.sound event-sounds false
     ```

  2. **Disable Screen Flash**:  
     Install my [Gnome Extension “No-Flash”](https://github.com/Svahnen/gnome-extension-no-flash), which prevents Gnome from showing the white flash animation during screenshots.

> **Note**: Because of Wayland security, there’s no purely user-space way to completely bypass the system’s screenshot indicator if the compositor enforces it. This fork merely switches to a method that “works” on Wayland; it doesn’t remove all limitations or notifications.

---

## Installation

1. Clone this fork:

    ```bash
    git clone https://github.com/Svahnen/openrecall_wayland.git
    cd openrecall_wayland

2. Install in editable mode:

    ```bash
    python3 -m pip install --upgrade --no-cache-dir -e .

3. Run OpenRecall:

    ```bash
    python3 -m openrecall.app

4. Open your browser at <http://localhost:8082>.

## Support & Issues

- If you have issues **specific to Gnome on Wayland** in this fork, please open an issue here.
- For general OpenRecall usage, refer to the official repo:  
  [**openrecall/openrecall**](https://github.com/openrecall/openrecall)

## License

This project is a fork of [OpenRecall](https://github.com/openrecall/openrecall) and is also released under the [AGPLv3](https://opensource.org/licenses/AGPL-3.0) license, ensuring that it remains open and accessible to everyone.
