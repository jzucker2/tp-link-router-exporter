# tp-link-router-exporter

Based around a really awesome client library [`tplinkrouterc6u`](https://github.com/AlexandrErohin/TP-Link-Archer-C6U)

## Instructions

To run, first create a `.env` file in the same directory as this project, like so:

```shell
TP_LINK_ROUTER_IP=http://10.0.1.1
TP_LINK_ROUTER_PASSWORD=foo
```

Then create the container like:

```shell
docker compose up -d --build
```
