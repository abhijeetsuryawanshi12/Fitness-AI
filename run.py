import uvicorn

if __name__ == "__main__":
    # We change the host to "127.0.0.1" which is the standard address
    # for accessing a local server from your browser.
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)