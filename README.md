Paste testindex.py and etymology.py to /home/ of the sample docker container
Run testindex first with:
spark-submit /home/testindex.py --spark.worker.timeout=9999999 --spark.executor.heartbeatInterval=999999

Run etymology.py second