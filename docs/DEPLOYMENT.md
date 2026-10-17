# Local deployment

The supported demo uses the local Python process. No account creation, purchases, top-ups, or hosted deployment is required.

```sh
python3 -m core_genesis.server --fresh
```

Open http://127.0.0.1:8080. The default bind is loopback; inference stays server-side. Do not expose this server publicly: it has no remote-user authentication.

## Optional Docker packaging

The Dockerfile packages the engine and Arena without Python dependencies. Docker must already be installed; building pulls the free Python image. The image excludes `.env`, Git data and prior experiments.

```sh
docker build -t core-genesis .
docker run --rm -p 127.0.0.1:8080:8080 --env-file .env \
  -v "$PWD/experiments:/app/experiments" \
  -v "$PWD/budget:/app/budget" core-genesis
```

The mounted directories must be writable by the container's `genesis` user. They preserve evidence, verified team and the project spending ledger across restarts. **Keep the budget mount**: container recreation must not reset spending. Pricing must remain verified and unexpired before live mode unlocks. Docker packaging is prepared but has not been built or run on the development machine.

No public endpoint is claimed. Public interactive hosting would require authentication and a server-wide spending budget before enabling inference actions.
