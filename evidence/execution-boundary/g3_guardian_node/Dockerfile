FROM g3-zelda-test:py313
USER 0:0
COPY engine/ /engine/
WORKDIR /engine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/engine
ENTRYPOINT ["python", "-B", "/engine/g3_guardian_node/service.py"]
CMD ["serve"]
