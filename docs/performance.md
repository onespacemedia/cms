# Notes on performance

TODO:

* `.content` is not free (the first time)
* because it renders only when there is a 404, your 404 page is rendered before the page is served, so if your 404 page is expensive to render all requests will be too
