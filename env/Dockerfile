# One image for every Spark role (master, workers, history server, Jupyter driver),
# so driver and executors always share the same Spark, Java, Python, and jars.
FROM spark:4.1.3-scala2.13-java17-python3-ubuntu

USER root

# Iceberg 1.11.x has no runtime for Spark 4.2 yet, which is why this image is Spark 4.1.
ARG ICEBERG_VERSION=1.11.0
ARG POSTGRES_JDBC_VERSION=42.7.13

ADD --chown=spark:spark \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.1_2.13/${ICEBERG_VERSION}/iceberg-spark-runtime-4.1_2.13-${ICEBERG_VERSION}.jar \
    /opt/spark/jars/
ADD --chown=spark:spark \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_JDBC_VERSION}/postgresql-${POSTGRES_JDBC_VERSION}.jar \
    /opt/spark/jars/

RUN pip3 install --no-cache-dir jupyterlab pandas pyarrow

RUN mkdir -p /opt/spark/conf /opt/spark/events /opt/warehouse /opt/data /home/spark /workspace \
 && chown -R spark:spark /opt/spark/conf /opt/spark/events /opt/warehouse /opt/data /home/spark /workspace

COPY --chown=spark:spark spark-defaults.conf /opt/spark/conf/spark-defaults.conf

ENV HOME=/home/spark \
    PYSPARK_PYTHON=python3 \
    PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.9-src.zip \
    PATH=/opt/spark/bin:${PATH}

USER spark
WORKDIR /workspace
