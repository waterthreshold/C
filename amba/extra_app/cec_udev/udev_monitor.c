// udev_monitor.c
#include <libudev.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    struct udev *udev = udev_new();
    if (!udev) {
        fprintf(stderr, "Failed to create udev\n");
        return 1;
    }

    // Create a monitor for "udev" events
    struct udev_monitor *mon = udev_monitor_new_from_netlink(udev, "udev");
    if (!mon) {
        fprintf(stderr, "Failed to create udev monitor\n");
        udev_unref(udev);
        return 1;
    }

    // Filter for the "usb" subsystem (optional — you can monitor other subsystems)
    udev_monitor_filter_add_match_subsystem_devtype(mon, "usb", NULL);
    udev_monitor_enable_receiving(mon);

    int fd = udev_monitor_get_fd(mon);
    printf("Listening for USB events (add/remove). Press Ctrl+C to exit.\n");

    while (1) {
        fd_set fds;
        FD_ZERO(&fds);
        FD_SET(fd, &fds);

        int ret = select(fd + 1, &fds, NULL, NULL, NULL);
        if (ret <= 0) continue;

        if (FD_ISSET(fd, &fds)) {
            struct udev_device *dev = udev_monitor_receive_device(mon);
            if (dev) {
                const char *action = udev_device_get_action(dev); // "add", "remove", "change"
                const char *subsys = udev_device_get_subsystem(dev);
                const char *devnode = udev_device_get_devnode(dev); // may be NULL for some USB events
                const char *vendor = udev_device_get_sysattr_value(dev, "idVendor");
                const char *product = udev_device_get_sysattr_value(dev, "idProduct");
                printf("Event: action=%s subsystem=%s devnode=%s vendor=%s product=%s\n",
                       action ?: "(null)",
                       subsys ?: "(null)",
                       devnode ?: "(none)",
                       vendor ?: "(unknown)",
                       product ?: "(unknown)");
                udev_device_unref(dev);
            }
        }
    }

    // never reached but tidy:
    udev_monitor_unref(mon);
    udev_unref(udev);
    return 0;
}

