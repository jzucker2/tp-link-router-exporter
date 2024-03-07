# Configuration

## Example

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
