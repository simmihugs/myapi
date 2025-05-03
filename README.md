# TTS API

## Run
```shell
docker compose -f compose.dev.yml up --build
```

## Test
### Create audio
```shell
curl -X POST -H "Content-Type: application/json" \
    -d '{"description": "Test text"}' \
    http://127.0.0.1:8000/audio/ \
    --output test.wav
```
### Query audio db
```shell
curl -X GET http://127.0.0.1:8000/audio/all
```

```shell
[
    {
        "id": "e0b71aa2c36406d07d55ac893942ac13",
        "description": "Want me to make this clearer?",
        "file_path": "audio/e0b71aa2c36406d07d55ac893942ac13.wav"
    },
    {
        "id": "8d13479f3677667f3409b72fb07dca5f",
        "description": "Okay, heres the modified code that returns the audio file via the API, handling both existing and newly generated audio. f",
        "file_path": "audio/8d13479f3677667f3409b72fb07dca5f.wav"
    }
]
```

### Delete audio
Use the id from the item to delete to delete it
```shell
curl -X DELETE http://127.0.0.1:8000/audio/8d13479f3677667f3409b72fb07dca5f
```
