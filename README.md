# fortifyapiclient
Fortify API client used to approve FPRs uploaded to a Software Security Center (SSC)

## Configuration

Before running the script, you will have to create a `.env` file with the following variables:

```
FORTIFY_SSC_URL=https://my-ssc-url/ssc
FORTIFY_SSC_USERNAME=my-admin-user
FORTIFY_SSC_PASSWORD=my-admin-password
```

## Running

The script takes two parameters: `appname` and `appversion`. For example: `python3 fortifyapiclient.py NewsBotIRC 0.2.2`.
