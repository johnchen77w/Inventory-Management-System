# **📊 Monitoring System (Prometheus + Grafana)**

This project includes a monitoring system for real-time observability of the inventory management service.

## **🧱 Architecture**

The monitoring stack consists of:

* **Prometheus** — collects metrics from the backend API
* **Grafana** — visualizes metrics through dashboards

```
Backend API (/metrics) → Prometheus → Grafana Dashboard
```

## **🚀 How to Run**

Start all services using Docker:

```
docker compose up -d
```

## **🔍 Access Points**

### **Prometheus**

* URL: http://localhost:9090
* Used to query raw metrics

Example query:

```
up
```

### **Grafana**

* URL: http://localhost:3001
* Default login:
  * Username: **admin**
  * Password: **admin**

## **📊 Dashboard**

### **Service Monitoring Dashboard**

The Grafana dashboard provides real-time monitoring of:

* API health status
* CPU usage
* Memory usage

## **📈 Key Metrics**


| **Metric**                       | **Description**                    |
| -------------------------------- | ---------------------------------- |
| up                               | API health (1 = running, 0 = down) |
| process\_cpu\_seconds\_total     | CPU usage over time                |
| process\_resident\_memory\_bytes | Memory usage                       |

## **🎨 Features**

* Real-time system monitoring
* Threshold-based visualization:
  * 🟢 Green → normal
  * 🟡 Yellow → warning
  * 🔴 Red → high usage
* Production-style dashboard layout

## **⚠️ Notes**

* Designed for DevOps and system observability
* Dashboard is accessible locally via Grafana
