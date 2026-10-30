# readme-doctor

A zero-dependency CLI that scores a README.md out of 100 and lists concrete fixes as JSON. It can also generate a skeleton for the sections that are missing.

Landing page: https://madhavarora-hub.github.io/readme-doctor/

## Install

Requires Python 3.8+. No dependencies.

```
git clone https://github.com/madhavarora-hub/readme-doctor
cd readme-doctor
```

## Usage

```
python cli.py README.md              # score + fixes (JSON)
python cli.py README.md --template   # skeleton for failing checks
python server.py 8080                # local HTTP API: POST /score
python x402_server.py 8402           # x402-paywalled API (USDC on Base)
```

Use it in CI by failing the build when the score is under a threshold (see `action.yml`).

## Contributing

Pull requests are welcome. Open an issue first to discuss changes.

## License

MIT
