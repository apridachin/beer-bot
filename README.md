### Useful commands

#### Lint
`python -m mypy ./app` - run typechecking
`python -m pylint ./app` - run pylint check
`python -m bandit ./app` - run bandit security check


#### Test
`pytest -v /tests` - run all tests


#### Docker
`docker build -f docker/bakhus-bot/Dockerfile -t bakhus-bot .` - build bot image

`docker run -d -p 6379:6379 --name redis redis` - start default redis container

`docker run --name bakhus-bot bakhus-but` - start bot container

`docker-compose up` - run application in docker

`docker logs {container name}` - see logs in container

#### Redis
`redis-cli` - start redis client in terminal 