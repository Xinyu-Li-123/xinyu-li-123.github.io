.PHONY: pagefind-index server server-dev

public:
	hugo build

pagefind-index: public
	npx -y pagefind --site public

server: pagefind-index
	hugo server

server-dev: pagefind-index
	hugo server -D
