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

The script takes three parameters: an option *flag*, the *name* of the application and the *version* of the applicaction. For example, to approve an artifact you have to run: `/usr/bin/python3 fortifyapiclient.py -a NewsBotIRC 0.2.2`.

You may run the script with the options `-h` or `--help` to get all the available option flags.
