init:
	docker run -it --rm -u $$(id -u):$$(id -g) -v "$$PWD":/app -w /app node npm install
