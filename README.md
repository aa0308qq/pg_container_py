# pg_container_py
Using Docker Python SDK to start a PostgreSQL container

## Getting Started

### Dependencies

- Docker installed on your machine
- Python and pip installed

### Installing
Use requirements.txt for PyPI installation
```
pip3 install -r requirements.txt
```

## Usage Guide
### Config
Setting up PostgreSQL through YAML
```
image_name: postgres:16
container_name: postgresql_db
connection_info:
  database: 'postgres'
  user: 'admin'
  password: '******'
  host: '127.0.0.1'
  port: 9527
heartbeat: True
```
### Library

```
from launcher import pull_image,start,stop
```

### Test
Will automatically pull the Docker image, start the container, and then stop the container

```
python3 launcher.py
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [postgrsql](https://docs.postgresql.tw/reference/sql-commands)
* [psycopg](https://www.psycopg.org/psycopg3/docs/)
* [pyyaml](https://pyyaml.org/wiki/PyYAMLDocumentation)
* [docker_python_sdk](https://docker-py.readthedocs.io/en/stable/)
* [pydantic](https://docs.pydantic.dev/latest/)