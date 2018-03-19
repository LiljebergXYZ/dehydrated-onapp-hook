# OnApp hook for dehydrated

Tested with:
* moln.ballou.se

## Configuration

The service URL and your email/api-key have to be in your environment.
The recommended way to do this is by adding the following to your config file for dehydrated

```
export ONAPP_EMAIL=example@example.com
export ONAPP_KEY=APIKEYFROMONAPP
export ONAPP_URL=onapp.test
```

If you want more debugging information you can also add `export DEBUG=TRUE`