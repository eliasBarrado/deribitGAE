docker build -t deribit-gae-image .
docker run --network host -it --rm --name deribit-gae deribit-gae-image