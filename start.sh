bot="bakhus-bot"
redis="redis-bot"

lint(){
  source venv/bin/activate
  python -m mypy ./app
  python -m pylint ./app
  python -m bandit ./app
}

build_bot_image(){
  docker build -f docker/bakhus-bot/Dockerfile -t $bot .
}

run_bot_container(){
  docker run --name bakhus-bot $bot
}

run_redis_container(){
  docker run -d \
    -p 6379:6379 \
    -v redis-data:/data \
    --mount type=bind,source="$(pwd)/docker/redis/redis.conf",target=/redis.conf \
    -e REDIS_PASSWORD="test_pass" \
    --name $redis \
    --rm \
    redis /bin/sh -c "redis-server"
}

stop_containers(){
  docker container stop $bot
  docker container stop $redis
}

remove_containers(){
  docker container rm $bot
  docker container rm $redis
}

restart(){
  stop_containers
  remove_containers
  run_bot_container
  run_redis_container
}

action=$1;
case $action in
    'lint')
      lint
    ;;
    'build_bot')
      build_bot_image
      ;;
    'run_bot')
      run_bot_container
      ;;
    'run_redis')
      run_redis_container
      ;;
    'restart')
      restart
      ;;
    *)
esac
