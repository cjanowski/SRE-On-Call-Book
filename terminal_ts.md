# 🛠️ Site Reliability Engineering - Bash Cheat Sheet

A quick reference guide for essential SRE commands to monitor, debug, and maintain production systems.

---

## 📊 System Monitoring

### `top` / `htop`
Monitor system resources in real-time.

```bash
top                    # Basic system monitor
htop                   # Interactive process viewer (better UI)
top -u username        # Filter by user
```

**Key shortcuts in top:**
- `P` - Sort by CPU
- `M` - Sort by Memory
- `k` - Kill a process
- `q` - Quit

### `vmstat`
Virtual memory statistics.

```bash
vmstat 1               # Update every 1 second
vmstat 5 10            # 10 samples, 5 seconds apart
```

### `iostat`
CPU and I/O statistics.

```bash
iostat -x 2            # Extended stats every 2 seconds
iostat -d -p sda       # Specific disk stats
```

---

## 📝 Log Analysis

### `tail`
View and follow log files.

```bash
tail -f /var/log/app.log              # Follow log in real-time
tail -n 100 /var/log/syslog           # Last 100 lines
tail -f app.log | grep ERROR          # Filter while following
```

### `grep`
Search through files and logs.

```bash
grep "ERROR" /var/log/app.log                    # Find errors
grep -r "OutOfMemory" /var/log/                  # Recursive search
grep -i "error" app.log                          # Case insensitive
grep -A 5 "Exception" app.log                    # Show 5 lines after match
grep -B 3 "ERROR" app.log                        # Show 3 lines before match
grep -C 2 "FATAL" app.log                        # Show 2 lines before and after
grep -v "DEBUG" app.log                          # Exclude DEBUG lines
grep -c "WARNING" app.log                        # Count matches
```

### `awk`
Text processing and analysis.

```bash
# Top IP addresses from access log
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10

# Sum column values
awk '{sum += $3} END {print sum}' data.txt

# Filter by column value
awk '$9 == 500 {print $0}' access.log

# Print specific columns
awk '{print $1, $4, $9}' access.log
```

### `sed`
Stream editor for text transformation.

```bash
# Extract lines between patterns
sed -n '/ERROR/,/END/p' app.log

# Replace text
sed 's/old/new/g' file.txt

# Delete lines matching pattern
sed '/DEBUG/d' app.log

# Print specific line range
sed -n '10,20p' file.txt
```

---

## 💾 Disk Usage

### `df`
Disk space by filesystem.

```bash
df -h                  # Human-readable format
df -i                  # Inode usage
df -T                  # Show filesystem type
```

### `du`
Directory and file sizes.

```bash
du -sh /var/log/*                     # Size of each log directory
du -h --max-depth=1 /                 # Top-level directory sizes
du -sh * | sort -h                    # Sorted by size
du -aBM /var | sort -nr | head -20    # Top 20 largest files in MB
```

### `lsof`
List open files and processes.

```bash
lsof | wc -l                          # Count open files
lsof /path/to/file                    # Processes using a file
lsof -u username                      # Files opened by user
lsof -i :8080                         # Processes using port 8080
lsof -p PID                           # Files opened by process
```

---

## 🔌 Network Diagnostics

### `netstat` / `ss`
Network connections and statistics.

```bash
# netstat (older)
netstat -tulpn                        # Listening ports
netstat -an | grep ESTABLISHED        # Active connections
netstat -s                            # Network statistics

# ss (modern replacement)
ss -tulpn                             # Listening TCP/UDP ports
ss -s                                 # Socket statistics
ss -t -a                              # All TCP sockets
ss -o state established               # Established connections with timers
```

### `curl`
HTTP requests and API testing.

```bash
# Basic requests
curl https://example.com
curl -I https://example.com                      # Headers only
curl -X POST https://api.com/endpoint            # POST request

# Response time and status
curl -o /dev/null -s -w "%{http_code}\n" https://example.com
curl -w "@curl-format.txt" -o /dev/null -s https://example.com

# With authentication
curl -u user:pass https://api.com/endpoint
curl -H "Authorization: Bearer TOKEN" https://api.com/data

# Follow redirects
curl -L https://example.com

# Verbose output
curl -v https://example.com
```

### `tcpdump`
Network packet capture and analysis.

```bash
tcpdump -i eth0                       # Capture on interface
tcpdump -i eth0 port 80               # Capture HTTP traffic
tcpdump -i eth0 host 192.168.1.1      # Specific host
tcpdump -w capture.pcap               # Write to file
tcpdump -r capture.pcap               # Read from file
```

---

## 🔍 Process Management

### `ps`
Process information.

```bash
ps aux                                # All processes
ps -ef                                # Full format listing
ps aux | grep java                    # Find Java processes
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head    # Top memory consumers
ps -p PID -o pid,vsz=MEMORY -o user,group,comm      # Specific process details
```

### `kill`
Terminate processes.

```bash
kill PID                              # Graceful termination (SIGTERM)
kill -9 PID                           # Force kill (SIGKILL)
kill -l                               # List all signals
killall process_name                  # Kill by name
pkill -f "pattern"                    # Kill matching pattern
```

### `strace`
Trace system calls and signals.

```bash
strace -p PID                         # Attach to running process
strace -c ./program                   # Count system calls
strace -e trace=open,read ./program   # Trace specific calls
strace -tt -o output.txt ./program    # Timestamps to file
```

---

## 📋 System Logs (systemd)

### `journalctl`
Query systemd journal logs.

```bash
# Basic queries
journalctl -u nginx.service                      # Service logs
journalctl -f                                    # Follow all logs
journalctl -u nginx.service -f                   # Follow service logs

# Time-based queries
journalctl --since "2024-01-01 00:00:00"
journalctl --since "1 hour ago"
journalctl --since today
journalctl --until "2024-01-01 23:59:59"

# Priority filtering
journalctl -p err                                # Errors only
journalctl -p warning..err                       # Warnings and errors

# Boot logs
journalctl -b                                    # Current boot
journalctl -b -1                                 # Previous boot
journalctl --list-boots                          # List all boots

# Output formats
journalctl -o json                               # JSON format
journalctl -o json-pretty                        # Pretty JSON
```

### `systemctl`
Control systemd services.

```bash
systemctl status nginx                # Service status
systemctl start nginx                 # Start service
systemctl stop nginx                  # Stop service
systemctl restart nginx               # Restart service
systemctl reload nginx                # Reload config
systemctl enable nginx                # Enable on boot
systemctl disable nginx               # Disable on boot
systemctl list-units --type=service   # List all services
```

---

## 🔧 Performance Analysis

### One-Liners for Common Tasks

**Find top CPU consuming processes:**
```bash
ps aux | sort -nrk 3,3 | head -n 10
```

**Find top memory consuming processes:**
```bash
ps aux | sort -nrk 4,4 | head -n 10
```

**Count HTTP status codes in access log:**
```bash
awk '{print $9}' access.log | sort | uniq -c | sort -rn
```

**Monitor connection count to port 80:**
```bash
watch -n 1 "netstat -an | grep :80 | wc -l"
```

**Find large files modified in last 7 days:**
```bash
find /var -type f -mtime -7 -size +100M -exec ls -lh {} \;
```

**Check disk I/O per process:**
```bash
iotop -o
```

**Real-time bandwidth usage:**
```bash
iftop -i eth0
```

**Find deleted files still held open:**
```bash
lsof +L1
```

---

## 🚨 Quick Incident Response

**Check if service is responding:**
```bash
curl -f https://example.com || echo "Service down!"
```

**Restart hung service:**
```bash
systemctl restart service-name && journalctl -u service-name -f
```

**Free up disk space (clear logs):**
```bash
journalctl --vacuum-time=7d           # Keep last 7 days
journalctl --vacuum-size=500M         # Keep last 500MB
```

**Find what's filling up disk:**
```bash
du -sh /* 2>/dev/null | sort -h | tail -10
```

**Check for memory leaks:**
```bash
ps aux | awk '{print $6/1024 " MB\t\t" $11}' | sort -n
```

---

## 💡 Pro Tips

1. **Combine commands with pipes** for powerful analysis:
   ```bash
   tail -f app.log | grep ERROR | awk '{print $1, $5}' | sort | uniq -c
   ```

2. **Use `watch`** to monitor commands continuously:
   ```bash
   watch -n 1 'df -h | grep /dev/sda'
   ```

3. **Create aliases** for frequently used commands:
   ```bash
   alias logs='journalctl -f'
   alias port='netstat -tulpn | grep'
   ```

4. **Background long-running traces** with `nohup`:
   ```bash
   nohup strace -p PID -o trace.log &
   ```

5. **Use `time`** to measure command execution:
   ```bash
   time curl https://example.com
   ```

---

## 📚 Additional Resources

- **Man pages**: `man command-name`
- **Command help**: `command-name --help`
- **TLDR pages**: Quick command examples at tldr.sh

---

*Keep calm and debug on! 🚀*
