# Dockerfile
FROM mambaorg/micromamba:1.4.2
# ARG NEW_MAMBA_USER=root
# ARG NEW_MAMBA_USER_ID=1000
# ARG NEW_MAMBA_USER_GID=1000
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yaml /tmp/environment.yaml
RUN micromamba install -y -n base -f /tmp/environment.yaml
# install nginx
RUN micromamba install --yes -n base -c conda-forge nginx && \
    micromamba clean --all --yes

# activate micromamba
ARG MAMBA_DOCKERFILE_ACTIVATE=1

USER root

# Note that conda conf is inside conda
COPY nginx.default /opt/conda/etc/nginx/sites.d/sampledb.conf
RUN ln -sf /dev/stdout /opt/conda/var/log/nginx//access.log \
   && ln -sf /dev/stderr /opt/conda/var/log/nginx//error.log


# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/sampledb
# COPY requirements.txt start-server.sh /opt/app/
# COPY .pip_cache /opt/app/pip_cache/
COPY . /opt/app/
WORKDIR /opt/app
# RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]