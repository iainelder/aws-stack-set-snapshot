# Notes and References

https://akshayranganath.github.io/Rate-Limiting-With-Python/

Has a way to avoid bursts by evenly spacing out the calls.
https://pypi.org/project/ratemate/

Unmaintained. Includes a sleep and retry decorator. Shows how to mix with the backoff library for exponential backoff. Unclear whether it supports spreading requests versus bursting
https://github.com/tomasbasham/ratelimit/issues/51

A fork of the above that implements the sliding-bucket algorithm instead of the leaky-bucket algorithm. Not sure if it does the even spacing which is what I want.
https://github.com/deckar01/ratelimit

If you limit it to say 3 per second it unleashes all of them at the start of the next second.
I want even spacing.
https://github.com/vutran1710/PyrateLimiter

https://yellowdesert.consulting/2019/02/20/python-boto3-logging/

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html

https://stackoverflow.com/questions/35088139/how-to-make-a-thread-safe-global-counter-in-python