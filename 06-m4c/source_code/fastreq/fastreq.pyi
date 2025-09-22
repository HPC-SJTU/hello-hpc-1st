def get(urls: list[str], remote_port: int = 18080) -> list[bytes]:
    '''
    Perform batch HTTP 1.1 get from localhost:[remote_port][url].

    It assumes remote is exactly the m4c server, and cannot used on any normal HTTP server.
    '''
