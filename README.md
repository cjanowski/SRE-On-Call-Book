# SRE Quick Reference Guide

## Core SRE Principles

### The Four Golden Signals
1. **Latency** - Time to service a request
2. **Traffic** - Demand on your system
3. **Errors** - Rate of failed requests
4. **Saturation** - How "full" your service is

### SLI, SLO, SLA
- **SLI (Service Level Indicator)** - Quantitative measure of service level (e.g., 99.9% of requests succeed)
- **SLO (Service Level Objective)** - Target value for SLI (e.g., 99.95% uptime)
- **SLA (Service Level Agreement)** - Business contract with consequences if SLO is not met

### Error Budget
```
Error Budget = 100% - SLO
```
- If SLO is 99.9%, error budget is 0.1%
- Use error budget to balance reliability vs. feature velocity
- When budget exhausted, focus on reliability over features

## Incident Management

### Incident Response Roles
- **Incident Commander (IC)** - Coordinates response, makes decisions
- **Communications Lead** - Updates stakeholders, manages external comms
- **Operations Lead** - Executes fixes, implements changes
- **Subject Matter Expert (SME)** - Provides domain expertise

### Incident Severity Levels
| Level | Impact | Response Time | Example |
|-------|--------|---------------|---------|
| SEV-1 | Critical system down | Immediate | Complete service outage |
| SEV-2 | Major degradation | < 15 min | Significant performance issues |
| SEV-3 | Minor impact | < 1 hour | Non-critical feature broken |
| SEV-4 | Minimal impact | Next business day | Cosmetic issues |

### Incident Response Workflow
1. **Detect** - Alert fires or user report
2. **Triage** - Assess severity and impact
3. **Mitigate** - Stop the bleeding (rollback, failover)
4. **Resolve** - Fix root cause
5. **Document** - Write postmortem
6. **Follow-up** - Implement action items

## Monitoring & Alerting

### Alerting Best Practices
- ✅ Alert on symptoms, not causes
- ✅ Every alert should be actionable
- ✅ Use multiple severity levels
- ❌ Don't alert on things that self-heal
- ❌ Avoid alert fatigue

### USE Method (Resources)
- **Utilization** - % time resource is busy
- **Saturation** - Amount of queued work
- **Errors** - Count of error events

### RED Method (Services)
- **Rate** - Requests per second
- **Errors** - Failed requests per second
- **Duration** - Time per request

## On-Call Best Practices

### Shift Handoff Checklist
- [ ] Review ongoing incidents
- [ ] Check recent alerts and trends
- [ ] Review scheduled maintenance
- [ ] Verify monitoring systems operational
- [ ] Ensure runbooks are up-to-date
- [ ] Test paging/escalation works

### On-Call Rotation Tips
- Follow sun: distribute across time zones
- Limit to 1 week rotations
- Provide compensation (time off, pay)
- Have clear escalation paths
- Maintain 50% non-oncall work time

## Capacity Planning

### Key Metrics to Track
- **Peak Load** - Maximum observed demand
- **Growth Rate** - % increase per time period
- **Headroom** - Capacity available before hitting limits
- **Lead Time** - Time to provision new capacity

### Capacity Planning Formula
```
Required Capacity = (Current Load × Growth Rate × Time Period) + Safety Buffer
```

## Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** SEV-X
**Impact:** [Users affected, revenue lost, etc.]

## Timeline
- HH:MM - Event occurred
- HH:MM - Alert fired
- HH:MM - Incident declared
- HH:MM - Mitigation started
- HH:MM - Service restored

## Root Cause
[Clear explanation of what went wrong]

## Resolution
[What was done to fix it]

## Action Items
1. [ ] [Item] - Owner: [Name] - Due: [Date]
2. [ ] [Item] - Owner: [Name] - Due: [Date]

## Lessons Learned
- What went well
- What went poorly
- Where we got lucky
```

## Common SRE Commands

### Health Checks
```bash
# Check service status
systemctl status <service>

# Test endpoint
curl -f https://api.example.com/health || echo "Health check failed"

# Monitor logs in real-time
journalctl -u <service> -f

# Check open connections
ss -tuln | grep <port>
```

### Performance Analysis
```bash
# CPU usage by process
top -bn1 | head -20

# Memory usage
free -h && cat /proc/meminfo | grep -i available

# Disk I/O
iostat -xz 1 5

# Network connections
netstat -ant | awk '{print $6}' | sort | uniq -c | sort -rn
```

### Quick Diagnostics
```bash
# Check last 100 errors
journalctl -p err -n 100

# Find processes using most CPU
ps aux --sort=-%cpu | head -10

# Check disk space
df -h

# View system load
uptime && cat /proc/loadavg
```

## Toil Reduction

### Definition
**Toil** - Manual, repetitive, automatable work with no lasting value

### Identifying Toil
- Manual (requires human action)
- Repetitive (done over and over)
- Automatable (could be done by machine)
- Tactical (interrupt-driven, reactive)
- No enduring value (pure overhead)
- Scales linearly with growth

### Toil Budget
- Target: < 50% of SRE time on toil
- Track toil hours per engineer per sprint
- Prioritize automation of high-frequency tasks

## Reliability Engineering Metrics

### Key SRE Metrics
- **MTBF** (Mean Time Between Failures) - Average time between incidents
- **MTTR** (Mean Time To Recovery) - Average time to restore service
- **MTTD** (Mean Time To Detect) - Average time to detect an issue
- **MTTA** (Mean Time To Acknowledge) - Average time to respond to alert

### Availability Calculation
```
Availability % = (Total Time - Downtime) / Total Time × 100
```

| Availability | Downtime/Year | Downtime/Month | Downtime/Week |
|--------------|---------------|----------------|---------------|
| 99% | 3.65 days | 7.31 hours | 1.68 hours |
| 99.9% | 8.77 hours | 43.83 minutes | 10.08 minutes |
| 99.99% | 52.60 minutes | 4.38 minutes | 1.01 minutes |
| 99.999% | 5.26 minutes | 26.30 seconds | 6.05 seconds |

## Chaos Engineering

### Principles
1. Build a hypothesis around steady-state behavior
2. Vary real-world events (failures, latency, etc.)
3. Run experiments in production
4. Automate experiments to run continuously
5. Minimize blast radius

### Common Experiments
- Kill random instances
- Inject network latency
- Exhaust CPU/memory resources
- Corrupt data/config
- Simulate region outages

## Quick Rollback Checklist

```bash
# 1. Confirm rollback decision with IC
# 2. Communicate rollback starting
# 3. Execute rollback
kubectl rollout undo deployment/<name>
# OR
git revert <commit> && git push && deploy

# 4. Monitor metrics during rollback
# 5. Verify service recovery
# 6. Update incident timeline
# 7. Communicate completion
```

## Useful SRE Resources

- **Google SRE Book** - https://sre.google/sre-book/table-of-contents/
- **Postmortem Culture** - Blameless, focused on learning
- **Runbook Template** - Step-by-step operational procedures
- **Incident Response Plan** - Defined roles, escalation paths
- **Service Dependencies Map** - Visual service topology

---

## SRE Mantras

> "Hope is not a strategy." - Traditional SRE wisdom

> "Embrace risk. Perfect reliability is the wrong goal."

> "Make tomorrow better than today."

> "Automate this year's job away."

> "Move fast without breaking things - or break them in a safe way."
