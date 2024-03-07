# Configuration

## Example

### Quick with Environmental Variables

```
    ...
    environment:
      # like `http://10.0.1.1` or `http://tplinkwifi.net`
      - TP_LINK_ROUTER_IP=${TP_LINK_ROUTER_IP}
      # this you can make up to be whatever you want, like `Living Room Router`
      - TP_LINK_ROUTER_NAME=${TP_LINK_ROUTER_NAME}
      # hopefully something secret!
      - TP_LINK_ROUTER_PASSWORD=${TP_LINK_ROUTER_PASSWORD}
```

### Multiple Routers with yaml config file

```yaml
routers:
  - router_name: Living Room Router
    router_ip: http://10.0.1.1
    router_password: foo

  - router_name: Kitchen Router
    router_ip: http://10.0.1.2
    router_password: bar
```

## Development

I am using [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) to parse the YAML configs
