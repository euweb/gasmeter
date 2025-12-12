# Gasmeter Systemd Service - Installation Guide

## Installation

1. **Copy files to Raspberry Pi:**
   ```bash
   sudo mkdir -p /home/pi/gas_reader
   sudo cp gasmeter.py gpio_handler.py mqtt_config.json logging.conf /home/pi/gas_reader/
   sudo chown -R pi:pi /home/pi/gas_reader
   ```

2. **Install service file:**
   ```bash
   sudo cp gasmeter.service /etc/systemd/system/
   sudo chmod 644 /etc/systemd/system/gasmeter.service
   ```

3. **Enable and start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gasmeter.service
   sudo systemctl start gasmeter.service
   ```

## Service Management

**Check status:**
```bash
sudo systemctl status gasmeter.service
```

**View logs:**
```bash
sudo journalctl -u gasmeter.service -f
```

**Stop service:**
```bash
sudo systemctl stop gasmeter.service
```

**Restart service:**
```bash
sudo systemctl restart gasmeter.service
```

**Disable service:**
```bash
sudo systemctl disable gasmeter.service
```

## Log Files

- **Systemd Journal:** `sudo journalctl -u gasmeter.service`
- **Application Log:** `/home/pi/gas_reader/gasmeter.log` (configured in logging.conf)

## Customization

If you want to use a different user or path, adjust in the `gasmeter.service` file:
- `User=` and `Group=`
- `WorkingDirectory=`
- `ExecStart=`
