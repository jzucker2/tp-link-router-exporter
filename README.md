# tp-link-router-exporter

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
