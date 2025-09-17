# utils/config.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

# Load .env file from project root
load_dotenv()

def pick(env: str, key: str, default: str | None = None) -> str | None:
    return os.getenv(f"{env.upper()}_{key}", default)

class Settings(BaseModel):
    test_env: str
    env_prefix: str

    # URLs
    base_url: str
    login_url: str

    # Browser
    browser: str
    headless: bool

    # Creds
    phone_number: str
    email: str
    password: str

    @property
    def phone(self) -> str:
        return self.phone_number


# ---------- Build Settings ----------
raw_env = os.getenv("TEST_ENV")
if not raw_env:
    sys.exit("❌ ERROR: TEST_ENV not found in .env. Please set TEST_ENV=dev|staging|prod")

env = raw_env.lower()
if env not in {"dev", "staging", "prod"}:
    sys.exit(f"❌ ERROR: Invalid TEST_ENV={env}. Must be one of dev|staging|prod")

prefix = {"dev": "DEV", "staging": "STAGING", "prod": "PROD"}[env]

settings = Settings(
    test_env=env,
    env_prefix=prefix,
    base_url=pick(prefix, "BASE_URL") or sys.exit(f"❌ {prefix}_BASE_URL missing"),
    login_url=pick(prefix, "LOGIN_URL") or f"{pick(prefix, 'BASE_URL').rstrip('/')}/account/login?return_url=%2Faccount",
    browser=pick(prefix, "BROWSER", "chromium"),
    headless=(pick(prefix, "HEADLESS", "true").lower() == "true"),
    phone_number=pick(prefix, "PHONE") or sys.exit(f"❌ {prefix}_PHONE missing"),
    email=pick(prefix, "EMAIL") or sys.exit(f"❌ {prefix}_EMAIL missing"),
    password=pick(prefix, "PASSWORD") or sys.exit(f"❌ {prefix}_PASSWORD missing"),
)

print(f"[settings] ✅ Using env={settings.test_env} url={settings.login_url} email={bool(settings.email)} phone={bool(settings.phone)}")


# # utils/config.py
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# def pick(prefix: str, key: str, default: str | None = None) -> str | None:
#     """Read a namespaced key like STAGING_EMAIL given prefix='STAGING' and key='EMAIL'."""
#     return os.getenv(f"{prefix}_{key}", default)

# class Settings(BaseModel):
#     # Public attributes (initialized in __init__)
#     test_env: str = "dev"
#     env_prefix: str = "DEV"

#     base_url: str = ""
#     login_url: str = ""
#     browser: str = "chromium"
#     headless: bool = True

#     email: str = ""
#     password: str = ""
#     phone: str = ""  # exposed directly; no phone_number aliasing needed

#     def __init__(self, **data):
#         # 1) ensure .env is loaded before reading any env vars
#         load_dotenv()
#         super().__init__(**data)

#         # 2) which env are we using?
#         self.test_env = (os.getenv("TEST_ENV") or "dev").lower()
#         self.env_prefix = {"dev": "DEV", "staging": "STAGING", "prod": "PROD"}.get(self.test_env, "DEV")

#         # 3) URLs
#         self.base_url = (pick(self.env_prefix, "BASE_URL") or "https://www.matahari.com").rstrip("/")
#         explicit_login = pick(self.env_prefix, "LOGIN_URL", "")
#         self.login_url = (explicit_login or f"{self.base_url}/account/login?return_url=%2Faccount").rstrip("/")

#         # 4) Browser
#         self.browser = pick(self.env_prefix, "BROWSER", "chromium") or "chromium"
#         self.headless = (pick(self.env_prefix, "HEADLESS", "true") or "true").lower() == "true"

#         # 5) Credentials
#         self.email = pick(self.env_prefix, "EMAIL", "") or ""
#         self.password = pick(self.env_prefix, "PASSWORD", "") or ""
#         self.phone = pick(self.env_prefix, "PHONE", "") or ""

#         # 6) quick one-line debug so you can see what got loaded
#         print(f"[settings] env={self.test_env} url={self.login_url} email={bool(self.email)} phone={bool(self.phone)}")

# settings = Settings()


# # utils/config.py
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def pick(env: str, key: str, default: str | None = None) -> str | None:
#     return os.getenv(f"{env.upper()}_{key}", default)

# class Settings(BaseModel):
#     test_env: str = os.getenv("TEST_ENV", "dev").lower()
#     env_prefix: str = {"dev": "DEV", "staging": "STAGING", "prod": "PROD"}.get(
#         os.getenv("TEST_ENV", "dev").lower(), "DEV"
#     )

#     # URLs
#     base_url: str = pick(env_prefix, "BASE_URL", "https://www.matahari.com")
#     login_url: str = pick(env_prefix, "LOGIN_URL") or f"{base_url.rstrip('/')}/account/login?return_url=%2Faccount"

#     # Browser
#     browser: str = pick(env_prefix, "BROWSER", "chromium")
#     headless: bool = (pick(env_prefix, "HEADLESS", "true").lower() == "true")

#     # Creds
#     phone_number: str = pick(env_prefix, "PHONE", "")
#     email: str = pick(env_prefix, "EMAIL", "")
#     password: str = pick(env_prefix, "PASSWORD", "")

#     # Back-compat alias so tests can use settings.phone
#     @property
#     def phone(self) -> str:
#         return self.phone_number

# settings = Settings()
