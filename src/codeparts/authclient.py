# https://github.com/floxay/python-riot-auth

import contextlib
import ctypes
import ssl
import sys
import warnings
from secrets import token_urlsafe
from typing import Optional, Sequence, Tuple

import aiohttp

class AuthClient:
    RIOT_CLIENT_USER_AGENT = token_urlsafe(111)
    CIPHERS13 = str(":".join(
        (
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_128_GCM_SHA256",
            "TLS_AES_256_GCM_SHA384",
        )
    ))
    CIPHERS = str(":".join(
        (
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_128_GCM_SHA256",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
            "ECDHE-ECDSA-CHACHA20-POLY1305",
            "ECDHE-RSA-CHACHA20-POLY1305",
            "ECDHE-ECDSA-AES256-SHA384",
            "ECDHE-RSA-AES256-SHA384",
            "ECDHE-ECDSA-AES128-SHA256",
            "ECDHE-RSA-AES128-SHA256",
            "DHE-RSA-AES256-GCM-SHA384",
            "DHE-RSA-AES128-GCM-SHA256",
            "DHE-RSA-AES256-SHA256",
            "DHE-RSA-AES128-SHA256",
        )
    ))
    SIGALGS = str(":".join(
        (
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512",
            "rsa_pkcs1_sha1",
        )
    ))

    def __init__(self) -> None:
        self._auth_ssl_ctx = AuthClient.create_riot_auth_ssl_ctx()
        self._cookie_jar = aiohttp.CookieJar()
        self.access_token: Optional[str] = None
        self.scope: Optional[str] = None
        self.id_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: int = 0
        self.user_id: Optional[str] = None
        self.entitlements_token: Optional[str] = None

    @staticmethod
    def create_riot_auth_ssl_ctx() -> ssl.SSLContext:
        ssl_ctx = ssl.create_default_context()

        addr = int(id(ssl_ctx) + sys.getsizeof(object()))
        ssl_ctx_addr = ctypes.cast(addr, ctypes.POINTER(ctypes.c_void_p)).contents

        libssl: Optional[ctypes.CDLL] = None
        if sys.platform.startswith("win32"):
            for dll_name in (
                "libssl-3.dll",
                "libssl-3-x64.dll",
                "libssl-1_1.dll",
                "libssl-1_1-x64.dll",
            ):
                with contextlib.suppress(FileNotFoundError, OSError):
                    libssl = ctypes.CDLL(dll_name)
                    break
        elif sys.platform.startswith(("linux", "darwin")):
            libssl = ctypes.CDLL(ssl._ssl.__file__)

        if libssl is None:
            raise NotImplementedError(
                "Failed to load libssl. Your platform or distribution might be unsupported, please open an issue."
            )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1
        ssl_ctx.set_alpn_protocols(["http/1.1"])
        ssl_ctx.options |= 1 << 19
        # libssl.SSL_CTX_set_ciphersuites(ssl_ctx_addr, AuthClient.CIPHERS13.encode())
        # libssl.SSL_CTX_set_cipher_list(ssl_ctx_addr, AuthClient.CIPHERS.encode())
        # libssl.SSL_CTX_ctrl(ssl_ctx_addr, 98, 0, AuthClient.SIGALGS.encode())

        # print([cipher["name"] for cipher in ssl_ctx.get_ciphers()])
        return ssl_ctx

    def __update(
        self,
        extract_jwt: bool = False,
        key_attr_pairs: Sequence[Tuple[str, str]] = (
            ("sub", "user_id"),
            ("exp", "expires_at"),
        ),
        **kwargs:any,
    ) -> None:
        predefined_keys = list([key for key in self.__dict__.keys() if key[0] != "_"])

        self.__dict__.update(
            (key, val) for key, val in kwargs.items() if key in predefined_keys
        )

        if extract_jwt:  # extract additional data from access JWT
            additional_data = self.__get_keys_from_access_token(key_attr_pairs)
            self.__dict__.update(
                (key, val) for key, val in additional_data if key in predefined_keys
            )

    async def createSession(self) -> aiohttp.ClientSession:
        self._cookie_jar.clear()

        conn = aiohttp.TCPConnector(ssl=self._auth_ssl_ctx)
        session = aiohttp.ClientSession(
            connector=conn, raise_for_status=True, cookie_jar=self._cookie_jar
        )
        return session